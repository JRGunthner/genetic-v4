# coding: utf-8
import math
from datetime import datetime, timedelta
from pcp_scheduler.src.model.LoadBalancer import LoadBalancer
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler import scheduler_utils
from pcp_scheduler.utils import utils
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException


class OrdinaryStrategy:
    def __init__(self, planjobs, potential_slots, configs, same_start=None, same_finish=None, all_planjobs=[],
                 non_working_days=[]):
        self.planjobs = planjobs
        self.potential_slots = potential_slots
        self.configs = configs
        self.same_start = True if same_start is None and same_finish is None else same_start
        self.same_finish = False if same_start is None and same_finish is None else same_finish
        self.all_planjobs = self.set_planjobs(all_planjobs)
        self.non_working_days = non_working_days

    def allocate(self):
        '''
        Define os horários de alocação dos planjobs fornecidos no construtor
        :return:
        '''
        if self.same_start and self.same_finish:
            self.set_execution_slots_same_start_and_finish()
        elif self.same_start:
            self.set_execution_slots_same_start()
        elif self.same_finish:
            self.set_execution_slots_same_finish()

    def set_execution_slots_same_start(self):
        """
        Seta as datas de inicio e fim das planjobs em potential_slots, escolhendo o
        slot em potencial que se enquadra da restrição de inicio-inicio e as demais configuraçãoes
        :return: Uma lista dos planjobs alocados
        """
        if len(self.planjobs) == 1 and self.planjobs[0].configs.is_deadline:
            self.set_deadline(self.planjobs[0])
            return

        most_early_date = min(self.potential_slots.keys())
        most_early_slot = min(self.potential_slots[most_early_date].keys())

        planjobs = self.potential_slots[most_early_date][most_early_slot].keys()

        for planjob in planjobs:
            if planjob.configs.fractioned_between_planjobs:
                self.set_execution_slots_fractioned_planjob(planjob, global_start=most_early_slot[0])
            elif planjob.configs.fractioned_between_intervals:
                self.set_execution_slots_fractioned_intervals(planjob, most_early_date, most_early_slot)
            else:
                slot = Slot(most_early_slot[0], most_early_slot[0],
                            most_early_slot[0] + timedelta(minutes=planjob.time + planjob.setup))
                LoadBalancer.load_balance(planjob, most_early_date, slot,
                                          scheduler_utils.get_all_allocated_resources(planjobs), self.configs)
                planjob.execution_slots.append(slot)

        return planjobs

    def set_execution_slots_same_finish(self):
        """
        Seta as datas de inicio e fim das planjobs em potential_slots, escolhendo o
        slot em potencial que se enquadra da restrição de fim-fim e as demais configuraçãoes
        :return: Uma lista dos planjobs alocados
        """

        most_early_date = min(self.potential_slots.keys())
        most_early_slot = min(self.potential_slots[most_early_date].keys())
        planjobs = list(self.potential_slots[most_early_date][most_early_slot].keys())

        planjobs.sort(key=lambda t: t.time, reverse=True)
        longest_task = planjobs[0]

        for planjob in planjobs:
            finish_date = min(most_early_slot[0] + timedelta(minutes=longest_task.time), most_early_slot[1])
            start_date = finish_date - timedelta(minutes=planjob.time + planjob.setup)
            slot = Slot(start_date, start_date, finish_date)
            LoadBalancer.load_balance(planjob, most_early_date, slot,
                                      scheduler_utils.get_all_allocated_resources(planjobs), self.configs)
            planjob.execution_slots.append(slot)

        '''
        has_fractioned_planjob = False
        for planjob in planjobs:
            if planjob.configs.fractioned_between_planjobs:
                has_fractioned_planjob = True
                break

        if not has_fractioned_planjob:
            for planjob in planjobs:
                planjob.finish_date = min(most_early_slot[0] + timedelta(minutes=longest_task.time), most_early_slot[1])
                planjob.start_date = planjob.finish_date - timedelta(minutes=planjob.time)

        else:
            for date in sorted(potential_slots.keys()):
                for slot in sorted(potential_slots[date]):
                    #aloque o planjob em planjobs[0]
                    #faça superior_limit igual a ultima finish_date
                    #tente alocar os outros, se der certo otimo, caso contrário va p o proximo slot
                    is_allocated = True
                    if planjobs[0].configs.fractioned_between_planjobs or planjob[0].configs.fractioned_between_intervals:
                        is_allocated = set_start_finish_dates_fractioned_planjob(planjobs[0], potential_slots, global_start=slot)
                    else:
                        start, finish = slot.start_time, slot.start_time + timedelta(minutes=planjobs[0].time)
                        planjobs[0].execution_slots.append(Slot(slot.date, start, finish))
                    if is_allocated:
                        superior_limit = planjobs[0].execution_slots[-1].finish_time

                        for planjob in planjobs[1:]:
                            if planjob.configs.fractioned_between_planjobs:
                                set_start_finish_dates_fractioned_planjob(planjob, potential_slots, global_finish=superior_limit)
                            else:
                                start, finish = superior_limit - timedelta(minutes=planjob.time), superior_limit
                                planjob.execution_slots.append(Slot(superior_limit.date, start, finish))
        '''

        return planjobs

    def set_execution_slots_same_start_and_finish(self):
        major_time = self.get_major_planjob_time()
        most_early_date = min(self.potential_slots.keys())
        most_early_slot = min(self.potential_slots[most_early_date].keys())

        self.allocate_planjobs_with_major_time(major_time, most_early_slot)

        for planjob in self.planjobs:
            self.fix_execution_slots_planjob(planjob)

    def fix_execution_slots_planjob(self, planjob):
        if len(planjob.same_start) > 0 and len(planjob.same_finish) > 0:
            siblings_start_satisfied = self.is_siblings_same_start_satisfied(planjob)
            if siblings_start_satisfied:
                self.fix_duration_if_need(planjob)
                siblings_finish_satisfied = self.is_siblings_same_finish_satisfied(planjob)
                if not siblings_finish_satisfied:
                    self.add_break_in_planjob(planjob)
        elif len(planjob.same_start) > 0:
            self.fix_duration_if_need(planjob)
        else:
            self.fix_duration_if_need(planjob, reverse=True)

    def set_deadline(self, planjob):
        predecessors = [self.get_planjob_by_id(id) for id in planjob.predecessors]
        start_time = scheduler_utils.get_max_finish_time_predecessor(planjob, predecessors)
        if start_time is None:
            first_date = sorted(list(self.potential_slots.keys()))[0]
            first_slot = sorted(self.potential_slots[first_date].keys())[0]
            start_time = first_slot[0]
        elif start_time is not None and planjob.configs.not_in_same_day_predecessor:
            start_time = start_time + timedelta(days=1)
            start_time = datetime(year=start_time.year, month=start_time.month, day=start_time.day)

        finish_time = scheduler_utils.choose_finish_time_planjob_deadline(planjob, start_time, non_working_days=self.non_working_days)
        if finish_time is None:
            value = {"planjobs": [planjob.id], "resources": [r.id for r in planjob.allocated_resources]}
            raise InsufficientResourceCalendarException(value)

        slot = Slot(start_time, start_time, finish_time)

        if self.configs.deadline_hour is not None:
            possible_finish_time = slot.finish_time.replace(hour=self.configs.deadline_hour)
            if possible_finish_time > slot.start_time:
                slot.finish_time = possible_finish_time

        planjob.execution_slots.append(slot)

    def set_execution_slots_fractioned_planjob(self, planjob, global_start=None, global_finish=None):
        '''
        Seta a(s) data(s) do(s) execution slots para o planjob passado como parâmetro
        :param planjob: planjob a ser alocado
        :param global_start: datetime opcional caso esse planjob tenha uma restrição de data que deve começar
        :param global_finish: datetime opcional caso esse planjob tenha uma restrição de data que deve terminar
        :return:
        '''
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, self.potential_slots)
        utils.change_limits(available_slots, inferior_limit=global_start, superior_limit=global_finish)

        start_finish_dates = []
        remainder = timedelta(minutes=planjob.time)
        setup = timedelta(minutes=planjob.setup)
        if global_finish is None:
            for date in sorted(available_slots.keys()):
                if remainder == timedelta(minutes=0): break
                for slot in available_slots[date]:
                    duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() / 60))
                    if duration >= remainder:
                        new_slot = Slot(slot.start_time, slot.start_time, slot.start_time + remainder)
                        start_finish_dates.append(new_slot)
                        remainder = timedelta(minutes=0)
                        break
                    else:
                        new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                        remainder -= (duration - setup)
                        start_finish_dates.append(new_slot)
        else:
            for date in sorted(available_slots.keys())[::-1]:
                if remainder == timedelta(minutes=0): break
                for slot in available_slots[date][::-1]:
                    duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() / 60))
                    if duration >= remainder:
                        new_slot = Slot(slot.start_time, slot.finish_time - remainder, slot.finish_time)
                        start_finish_dates.insert(0, new_slot)
                        remainder = timedelta(minutes=0)
                        break
                    else:
                        new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                        remainder -= duration
                        start_finish_dates.insert(0, new_slot)
            if remainder != timedelta(minutes=0):
                return False

        planjob.execution_slots = start_finish_dates
        return True

    def set_execution_slots_fractioned_intervals(self, planjob, target_date_str, target_slot):
        '''
         Seta a(s) data(s) do(s) execution slots para o planjob passado como parâmetro
        :param planjob: planjob a ser alocado
        :param target_date_str: data como string alvo que o planjob deve começar
        :param target_slot: tuple(datetime, datetime) slot alvo que o planjob deve começar
        :return:
        '''
        target_date = datetime.strptime(target_date_str, utils.DATE_FORMAT)
        real_slots = self.potential_slots[target_date_str][target_slot][planjob]
        chosen_slot = real_slots[0]

        duration = (chosen_slot.finish_time - target_slot[0]).total_seconds() // 60
        if duration >= planjob.time + planjob.setup:
            slot = Slot(target_slot[0], target_slot[0], target_slot[0] + timedelta(minutes=planjob.time+planjob.setup))
            LoadBalancer.load_balance(planjob, target_date_str, slot,
                                      scheduler_utils.get_all_allocated_resources(self.planjobs), self.configs)
            planjob.execution_slots.append(slot)
        else:
            self.set_execution_slots_with_complement_slots(planjob, chosen_slot, target_date, target_slot)

    def set_execution_slots_with_complement_slots(self, planjob, chosen_slot, target_date, target_slot):
        '''
        Define o(s) execution slot(s) do planjob passado como parâmetro usando os slots complementares
        do chosen_slot
        :param planjob:
        :param chosen_slot: slot escolhido pra alocar o planjob
        :param target_date: data alvo que o planjob deve começar
        :param target_slot:
        :return: tuple(datetime, datetime) slot alvo que o planjob deve começar
        '''
        setup = timedelta(minutes=planjob.setup)
        remainder = timedelta(minutes=planjob.time)

        new_slot = Slot(target_date, target_slot[0], target_slot[1])
        duration = timedelta(minutes=((new_slot.finish_time - new_slot.start_time).total_seconds() / 60))
        remainder -= (duration - setup)
        planjob.execution_slots.append(new_slot)

        for slot in chosen_slot.complement:
            duration = timedelta(minutes=((slot.finish_time - slot.start_time).total_seconds() / 60))
            if duration >= remainder:
                new_slot = Slot(slot.start_time, slot.start_time, slot.start_time + remainder)
                planjob.execution_slots.append(new_slot)
                break
            else:
                new_slot = Slot(slot.start_time, slot.start_time, slot.finish_time)
                remainder -= (duration - setup)
                planjob.execution_slots.append(new_slot)

    def get_major_planjob_time(self):
        '''
        Retorna o tempo do planjob de maior duração
        :return: tempo em minutos
        '''
        major_time = 0
        for planjob in self.planjobs:
            if planjob.time + planjob.setup > major_time:
                major_time = planjob.time + planjob.setup

        return major_time

    def allocate_planjobs_with_major_time(self, major_time, slot_intersection):
        '''
        Aloca os planjobs a partir de um slot interseção com o tempo passado como parâmetro
        :param major_time:
        :param slot_intersection:
        :return:
        '''
        start_time = slot_intersection[0]
        finish_time = start_time + timedelta(minutes=major_time)
        for planjob in self.planjobs:
            planjob.execution_slots = [Slot(start_time, start_time, finish_time)]

    def is_siblings_same_start_satisfied(self, planjob):
        '''
        Verifica se todos os planjobs que têm restrição de inicio-inicio com o planjob passado como parâmetro realmente
        estão começando no mesmo start_time que ele
        :param planjob: planjob que terá seus siblings same_start analisados
        :return:
        '''
        for sibling_id in planjob.same_start:
            sibling = self.get_planjob_by_id(sibling_id)
            if sibling.execution_slots[0].start_time != planjob.execution_slots[0].start_time:
                return False
        return True

    def is_siblings_same_finish_satisfied(self, planjob):
        '''
        Verifica se todos os planjobs que têm restrição de fim-fim com o planjob passado como parâmetro realmente
        estão terminando no mesmo finish_time que ele
        :param planjob: planjob que terá seus siblings same_finish analisados
        :return:
        '''
        for sibling_id in planjob.same_finish:
            #Todo preciso ter certeza que planjobs e all_planjobs compartilham a referencia
            sibling = self.get_planjob_by_id(sibling_id)
            if sibling.execution_slots[-1].finish_time != planjob.execution_slots[-1].finish_time:
                return False
        return True

    def fix_duration_if_need(self, planjob, reverse=False):
        '''
        Corrige os execution slots do planjob, caso eles estejam maior do que o necessário
        :param planjob: planjob a ser ajustado
        :return:
        '''
        # Todo não estou segura que será sempre no execution_slots[0] analisar melhor depois
        if planjob.execution_slots[0].minutes() > planjob.time + planjob.setup:
            if reverse:
                correct_start_time = planjob.execution_slots[0].finish_time - timedelta(minutes=planjob.time+planjob.setup)
                planjob.execution_slots[0].start_time = correct_start_time
            else:
                correct_finish_time = planjob.execution_slots[0].start_time + timedelta(minutes=planjob.time+planjob.setup)
                planjob.execution_slots[0].finish_time = correct_finish_time

    def add_break_in_planjob(self, planjob):
        needed_start = self.get_planjob_by_id(planjob.same_start[0]).execution_slots[0].start_time #min
        needed_finish = self.get_planjob_by_id(planjob.same_finish[0]).execution_slots[-1].finish_time # max

        break_ = needed_finish - needed_start - timedelta(planjob.time+2*planjob.setup)
        new_time1, new_time2 = self.get_2_half_time(planjob)

        current_start = planjob.execution_slots[0].start_time
        first_slot = Slot(current_start, current_start, current_start+new_time1)

        next_start = first_slot.finish_time + break_
        second_slot = Slot(next_start, next_start, next_start+new_time2)

        planjob.execution_slots = [first_slot, second_slot]

    def get_2_half_time(self, planjob):
        '''
        Retorna dois times cuja soma é igual ao time do planjob, se o tempo do planjob é um valor par os times
        retornado são iguais, se for ímpar o primeiro time retornado é o teto da divisão do tempo do planjob por dois e
        o segundo é o piso da divisão do tempo do planjob por dois
        :param planjob: planjob alvo
        :return:
        '''
        return planjob.setup+math.ceil(planjob.time/2), planjob.setup+math.floor(planjob.time/2)

    def get_planjob_by_id(self, id):
        return self.all_planjobs[id]

    def set_planjobs(self, planjobs):
        planjobs_dict = {}
        for planjob in planjobs:
            planjobs_dict[planjob.id] = planjob
        return planjobs_dict
