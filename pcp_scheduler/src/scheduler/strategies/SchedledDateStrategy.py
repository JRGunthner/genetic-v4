# coding: utf-8

import random
import copy

from datetime import timedelta, datetime

from pcp_scheduler.src.scheduler import scheduler_utils
from pcp_scheduler.utils import utils
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.LoadBalancer import LoadBalancer
from pcp_scheduler.src.scheduler.SchedulerFilter import SchedulerFilter
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException


class ScheduledDateStrategy:
    def __init__(self, planjobs, configs=None, all_planjobs=[], non_working_days=[]):
        self.planjobs = planjobs
        self.resources_allocation = None
        self.configs = configs
        self.all_planjobs = self.set_planjobs(all_planjobs)
        self.non_working_days = non_working_days

    def allocate(self):
        self.resources_allocation = self.get_resources_allocation()
        self.allocate_same_start()

    def validate_planjob(self, planjob, min_date):
        predecessors = [self.get_planjob_by_id(id) for id in planjob.predecessors]
        last_time = scheduler_utils.get_max_finish_time_predecessor(planjob, predecessors)
        if last_time is not None and last_time > min_date:
            pass

    def allocate_same_start(self):
        """
        Aloca um planjob com restrição de inicio-inicio
        :return:
        """
        # ToDo: ta errado não posso ter mais de uma scheduled_date
        min_date = min([p.scheduled_date for p in self.planjobs if p.scheduled_date is not None])

        for planjob in self.planjobs:
            self.validate_planjob(planjob, min_date)

            if planjob.configs.fractioned_between_planjobs:
                self.set_execution_slots_fract_btw_planjobs(planjob, self.resources_allocation[planjob], min_date)
            elif planjob.configs.fractioned_between_intervals:
                self.build_complementary_slots(planjob, min_date)
                self.set_execution_slots_with_complement_slots(planjob, min_date)
            elif planjob.configs.is_deadline:
                if planjob.configs.not_in_same_day_predecessor:
                    min_date = min_date + timedelta(days=1)
                    min_date = datetime(year=min_date.year, month=min_date.month, day=min_date.day)

                finish_time = scheduler_utils.choose_finish_time_planjob_deadline(planjob, min_date,
                                                                                  self.non_working_days)
                if finish_time is None:
                    value = {"planjobs": [planjob.id], "resources": [r.id for r in planjob.allocated_resources]}
                    raise InsufficientResourceCalendarException(value)

                slot = Slot(min_date, min_date, finish_time)
                if self.configs.deadline_hour is not None:
                    possible_finish_time = slot.finish_time.replace(hour=self.configs.deadline_hour)
                    if possible_finish_time > slot.start_time:
                        slot.finish_time = possible_finish_time
                planjob.execution_slots.append(slot)
            else:
                slot = Slot(min_date, min_date, min_date+timedelta(minutes=planjob.setup+planjob.time))
                LoadBalancer.load_balance(planjob, min_date.strftime(utils.DATE_FORMAT), slot,
                                          scheduler_utils.get_all_allocated_resources(self.planjobs), self.configs)
                planjob.execution_slots = [slot]

    def set_execution_slots_fract_btw_planjobs(self, planjob, resources_allocation, start_time):
        """
        Faz a alocação de planjob fracionado que começa a executar no start time passado como
        parâmetro
        :param planjob:
        :param resources_allocation:
        :param start_time:
        :return:
        """
        potential_slots = scheduler_utils.get_initial_potential_slots(resources_allocation[0], planjob, None, self.configs)
        for i in range(1, len(resources_allocation)):
            potential_slots = scheduler_utils.define_correspondent_slots(potential_slots, resources_allocation[i],
                                                                         planjob, self.configs)

        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, potential_slots)
        utils.change_limits(available_slots, inferior_limit=start_time)

        start_finish_dates = []
        remainder = timedelta(minutes=planjob.time)
        setup = timedelta(minutes=planjob.setup)
        for date in sorted(available_slots.keys()):
            if remainder == timedelta(minutes=0): break

            for slot in available_slots[date]:
                duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() / 60))
                if duration >= remainder+setup:
                    new_slot = Slot(slot.start_time, slot.start_time, slot.start_time + remainder + setup)
                    start_finish_dates.append(new_slot)
                    remainder = timedelta(minutes=0)
                    break
                else:
                    new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                    remainder -= (duration - setup)
                    start_finish_dates.append(new_slot)

        planjob.execution_slots = start_finish_dates

        if start_finish_dates == []:
            pass #Todo lançar exceção?

    def build_complementary_slots(self, planjob, scheduled_date):
        filter = SchedulerFilter([planjob], self.configs, [planjob])
        date_desired_str = planjob.scheduled_date.strftime(utils.DATE_FORMAT)
        for resource in planjob.allocated_resources:
            for slot in resource.available_slots[date_desired_str]:
                if slot.start_time <= scheduled_date <= slot.finish_time:
                    filter.build_complementary_slots(resource, date_desired_str, slot)

    def set_execution_slots_with_complement_slots(self, planjob, start_time, target_slots=None):
        '''
        Define o(s) execution slot(s) do planjob passado como parâmetro usando os slots complementares
        do chosen_slot
        :param planjob:
        :param chosen_slot: slot escolhido pra alocar o planjob
        :param target_date: data alvo que o planjob deve começar
        :param target_slot:
        :return: tuple(datetime, datetime) slot alvo que o planjob deve começar
        '''
        target_slots = self.get_slots_target_in_solution_by_scheduled_date(planjob.allocated_resources, planjob) \
                        if target_slots is None else target_slots
        chosen_slot = random.choice(target_slots)
        chosen_slot.start_time = start_time
        all_slots = [chosen_slot]
        all_slots.extend(chosen_slot.complement)

        setup = timedelta(minutes=planjob.setup)
        remainder = timedelta(minutes=planjob.time)
        for slot in all_slots:
            duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() // 60))
            if duration >= remainder:
                new_slot = Slot(slot.start_time, slot.start_time, slot.start_time + remainder)
                planjob.execution_slots.append(new_slot)
                break
            else:
                new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                remainder -= (duration - setup)
                planjob.execution_slots.append(new_slot)

    def get_resources_allocation(self):
        resources_allocation = {}
        for planjob in self.planjobs:
            if planjob.configs.is_deadline: continue
            resources_allocation[planjob] = []
            for resource in planjob.allocated_resources:
                resources_allocation[planjob].append(copy.deepcopy(resource.available_slots))
        return resources_allocation

    def get_slots_target_in_solution_by_scheduled_date(self, solution, planjob):
        date_desired_str = planjob.scheduled_date.strftime(utils.DATE_FORMAT)
        slots_target = []
        for resource in solution:
            for slot in resource.available_slots[date_desired_str]:
                if slot.start_time <= planjob.scheduled_date <= slot.finish_time:
                    slots_target.append(slot)

        return slots_target

    def find_slot_by_scheduled_date(self, scheduled_date, resource):
        scheduled_date_str = scheduled_date.strftime(utils.DATE_FORMAT)
        if scheduled_date_str in resource.available_slots.keys():
            for slot in resource.available_slots[scheduled_date_str]:
                if slot.start_time <= scheduled_date <= slot.finish_time:
                    return slot

    def get_planjob_by_id(self, id):
        return self.all_planjobs[id]

    def set_planjobs(self, planjobs):
        planjobs_dict = {}
        for planjob in planjobs:
            planjobs_dict[planjob.id] = planjob
        return planjobs_dict