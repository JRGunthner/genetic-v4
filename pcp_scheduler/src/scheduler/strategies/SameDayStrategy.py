#coding: utf-8

from datetime import timedelta
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.utils import utils
from pcp_scheduler.src.model.LoadBalancer import LoadBalancer
from pcp_scheduler.src.scheduler import scheduler_utils


class SameDayStrategy:
    def __init__(self, planjobs, potential_slots, global_configs):
        self.planjobs = planjobs
        self.potential_slots = potential_slots
        self.global_configs = global_configs

    def allocate(self):
        if len(self.planjobs[0].same_start) > 0:
            self.allocate_same_start_planjobs()
        elif len(self.planjobs[0].same_finish) > 0:
            self.allocate_same_finish_planjobs()
        else:
            self.allocate_simple_planjob(self.planjobs[0])

    def allocate_same_start_planjobs(self):
        for date in sorted(self.potential_slots.keys()):
            sufficient = True
            for slot_interception in sorted(self.potential_slots[date].keys()):
                for planjob in self.planjobs:
                    if planjob.configs.fractioned_between_planjobs:
                        slots_fractioned = self.get_slots_fractioned_between_planjobs(planjob, global_start=slot_interception[0])
                        if slots_fractioned is None:
                            sufficient = False
                            break
                        else:
                            planjob.execution_slots = slots_fractioned
                    elif planjob.configs.fractioned_between_intervals:
                        chosen_slot = self.potential_slots[date][slot_interception][planjob][0]
                        slots_fractioned = self.get_slots_fractioned_between_intervals(planjob, chosen_slot, slot_interception)
                        if slots_fractioned is None:
                            sufficient = False
                            break
                        else:
                            planjob.execution_slots = slots_fractioned
                    else:
                        start_time = slot_interception[0]
                        finish_time = start_time + timedelta(minutes=planjob.time + planjob.setup)
                        if start_time.date() != finish_time.date():
                            sufficient = False
                            break

                        slot = Slot(start_time, start_time, finish_time)
                        LoadBalancer.load_balance(planjob, date, slot,
                                                  scheduler_utils.get_all_allocated_resources(self.planjobs),
                                                  self.global_configs)
                        planjob.execution_slots = [slot]

                if sufficient: break
            if sufficient: break
        # if not sufficient: #TO DO: lançar exceção?

    def allocate_same_finish_planjobs(self):
        self.planjobs.sort(key=lambda t: t.time+t.setup, reverse=True)
        longest_time = self.planjobs[0].time + self.planjobs[0].setup

        for date in sorted(self.potential_slots.keys()):
            for slot_intersection in sorted(self.potential_slots[date].keys()):
                finish_date = min(slot_intersection[0] + timedelta(minutes=longest_time), slot_intersection[1])
                other_day = False
                for planjob in self.planjobs:
                    start_date = finish_date - timedelta(minutes=planjob.time+planjob.setup)
                    if planjob.configs.same_day and start_date.date() != finish_date.date():
                        other_day = True
                        break
                    slot = Slot(start_date, start_date, finish_date)
                    LoadBalancer.load_balance(planjob, date, slot,
                                              scheduler_utils.get_all_allocated_resources(self.planjobs),
                                              self.global_configs)
                    planjob.execution_slots = [slot]

        #if other_day? TO Do: lançar exceção

    def allocate_simple_planjob(self, planjob):
        if planjob.configs.fractioned_between_planjobs:
            self.set_execution_slots_fractioned_between_planjobs(planjob)
        elif planjob.configs.fractioned_between_intervals:
            self.set_execution_slots_fractioned_btw_intervals(planjob)
        else:
            allocated = False
            for date in sorted(self.potential_slots.keys()):
                for slot_intersection in sorted(self.potential_slots[date].keys()):
                    finish_time = slot_intersection[0] + timedelta(minutes=planjob.time+planjob.setup)
                    if slot_intersection[0].date() == finish_time.date():
                        slot = Slot(slot_intersection[0], slot_intersection[0], finish_time)
                        LoadBalancer.load_balance(planjob, date, slot, [planjob], self.global_configs)
                        planjob.execution_slots.append(slot)
                        allocated = True
                        break

                if allocated: break
            if not allocated: pass #TO DO: lançar exceção?

    def set_execution_slots_fractioned_between_planjobs(self, planjob):
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, self.potential_slots)
        remainder = timedelta(minutes=planjob.time)
        setup = timedelta(minutes=planjob.setup)
        start_finish_dates = []
        for date in sorted(available_slots.keys()):
            for slot in sorted(available_slots[date]):
                duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() / 60))
                if duration >= (remainder+setup):
                    new_slot = Slot(slot.start_time, slot.start_time, slot.start_time + remainder + setup)
                    if new_slot.start_time.date() != new_slot.finish_time.date(): break
                    start_finish_dates.append(new_slot)
                    remainder = timedelta(minutes=0)
                    break
                else:
                    new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                    if new_slot.start_time.date() != new_slot.finish_time.date(): break
                    remainder -= (duration - setup)
                    start_finish_dates.append(new_slot)

            if remainder == timedelta(minutes=0):
                planjob.execution_slots = start_finish_dates
                return True
            else:
                remainder = timedelta(minutes=planjob.time)
                start_finish_dates = []

        #To DO: if chegou aqui, não conseuiu alocar: o que fazer

    def set_execution_slots_fractioned_btw_intervals(self, planjob):
        for date_str in sorted(self.potential_slots.keys()):
            for slot_interception in sorted(self.potential_slots[date_str]):
                chosen_slot = self.potential_slots[date_str][slot_interception][planjob][0]
                execution_slots = self.get_slots_fractioned_between_intervals(planjob, chosen_slot, slot_interception)
                if execution_slots is not None:
                    planjob.execution_slots = execution_slots

        #ToDo se chegar aqui, significa que não alocou. O que fazer?

    def get_slots_fractioned_between_planjobs(self, planjob, global_start=None):
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, self.potential_slots)
        utils.change_limits(available_slots, inferior_limit=global_start)

        dates = [global_start.strftime("%Y/%m/%d")] if planjob.configs.same_day else sorted(available_slots.keys())
        remainder = timedelta(minutes=planjob.time)
        start_finish_dates = []
        setup = timedelta(minutes=planjob.setup)
        for date in dates:
            if remainder == timedelta(minutes=0):
                break
            for slot in sorted(available_slots[date]):
                duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() / 60))
                if duration >= (remainder+setup):
                    new_slot = Slot(slot.start_time, slot.start_time, slot.start_time + remainder + setup)
                    if new_slot.start_time.date() != new_slot.finish_time.date(): return
                    start_finish_dates.append(new_slot)
                    remainder = timedelta(minutes=0)
                    break
                else:
                    new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                    if new_slot.start_time.date() != new_slot.finish_time.date(): return
                    remainder -= (duration - setup)
                    start_finish_dates.append(new_slot)

        if remainder == timedelta(minutes=0):
            return start_finish_dates
        return

    def get_slots_fractioned_between_intervals(self, planjob, chosen_slot, target_slot):
        '''
            Define o(s) execution slot(s) do planjob passado como parâmetro usando os slots complementares
            do chosen_slot
            :param planjob:
            :param chosen_slot: slot escolhido pra alocar o planjob
            :param target_date: data alvo que o planjob deve começar
            :param target_slot:
            :return: tuple(datetime, datetime) slot alvo que o planjob deve começar
        '''
        duration = (chosen_slot.finish_time - target_slot[0]).total_seconds() // 60
        if duration >= planjob.time + planjob.setup:
            finish_time = target_slot[0] + planjob.time + planjob.setup
            if target_slot[0].date() == finish_time.date():
                slot = Slot(target_slot[0], target_slot[0], finish_time)
                return [slot]
            else:
                return None

        setup = timedelta(minutes=planjob.setup)
        remainder = timedelta(minutes=planjob.time)
        execution_slots = []

        chosen_slot.start_time = target_slot[0]
        all_slots = [chosen_slot]
        all_slots.extend(chosen_slot.complement)

        finish_date = chosen_slot.start_time.date()
        for slot in all_slots:
            duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() / 60))
            if duration >= remainder:
                finish_time = slot.start_time + remainder
                if finish_time.date() != finish_date: return
                new_slot = Slot(slot.start_time, slot.start_time, finish_time)
                execution_slots.append(new_slot)
                break
            else:
                if slot.finish_time.date() != finish_date: return
                new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                remainder -= (duration - setup)
                execution_slots.append(new_slot)

        return execution_slots
