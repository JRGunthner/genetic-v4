# coding: utf-8
import copy
from datetime import datetime, timedelta
from pcp_scheduler.utils import utils
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.LoadBalancer import LoadBalancer
from pcp_scheduler.src.scheduler import scheduler_config_evaluating, scheduler_utils


class SchedulerFilter:
    def __init__(self, planjobs, configs, all_planjobs, same_start=None, same_finish=None):
        self.planjobs = planjobs
        self.configs = configs
        self.all_planjobs = all_planjobs
        self.same_start = True if same_start is None and same_finish is None else same_start
        self.same_finish = False if same_start is None and same_finish is None else same_finish
        self.eval_function = self.choose_eval_function()

    def filter(self):
        '''
        Filtra os available slots dos recursos alocados pra os planjobs
        :return:
        '''
        self.change_scheduler_by_predecessors()
        self.change_scheduler_by_intervals_fraction()
        self.adjust_scheduler_to_planjobs_nonstop()

    def define_correspondent_start_times(self):
        dates = set([])
        for p in range(len(self.planjobs)):
            planjob = self.planjobs[p]
            for r in range(len(planjob.allocated_resources)):
                resource = planjob.allocated_resources[r]
                if p == r == 0: dates = set(resource.available_slots.keys())
                dates.intersection_update(resource.available_slots.keys())

        if len(dates) == 0: return None

        times = {}
        for date in dates:
            all_slots_on_date = []
            for planjob in self.planjobs:
                for resource in planjob.allocated_resources:
                    all_slots_on_date.append(resource.available_slots[date])
            times[date] = all_slots_on_date

        return sorted(list(dates))

    def define_correspondent_slots(self):
        '''
        Define os slots de interseção em potencial dos planjobs passados no construtor
        :return: potential_slots:
            { date1: {slot_intersection1: {task1: [resources_slots], ..., taskn:[resources_slots]}
                     slot_intersection2: {task1: [resources_slots], ..., taskn:[resources_slots]}
             ...
             date_n:{...}
            }
        '''
        self.filter()

        resources_allocation = {}
        for planjob in self.planjobs:
            resources_allocation[planjob] = []
            for resource in planjob.allocated_resources:
                resources_allocation[planjob].append(resource.available_slots)

        potential_slots = None
        for planjob in self.planjobs:
            for i in range(0, len(resources_allocation[planjob])):
                if potential_slots is None:
                    potential_slots = scheduler_utils.get_initial_potential_slots(
                        resources_allocation[planjob][i],
                        planjob, self.eval_function, self.configs)
                else:
                    potential_slots = scheduler_utils.define_correspondent_slots(
                        potential_slots, resources_allocation[planjob][i],
                        planjob, self.configs, self.eval_function)

        return potential_slots

    def change_scheduler_by_predecessors(self):
        """
        Modifica o calendario dos recursos disponíveis removendo as datas e times de acordo com o horário de alocação dos
        predecessores de cada planjob
        :return:
        """
        for planjob in self.planjobs:
            max_finish_date = None
            if len(planjob.predecessors) > 0:
                first_predecessor = self.get_planjob_by_id(planjob.predecessors[0])
                max_finish_date = first_predecessor.execution_slots[-1].finish_time
                for i in range(1, len(planjob.predecessors)):
                    predecessor = self.get_planjob_by_id(planjob.predecessors[i])
                    if predecessor.execution_slots[-1].finish_time > max_finish_date:
                        max_finish_date = predecessor.execution_slots[-1].finish_time
                if planjob.configs.not_in_same_day_predecessor:
                    max_finish_date = max_finish_date + timedelta(days=1)
                    max_finish_date = datetime(year=max_finish_date.year, month=max_finish_date.month, day=max_finish_date.day)

            for resource in planjob.allocated_resources:
                if planjob.min_start_date is not None:
                    max_finish_date = planjob.min_start_date if max_finish_date is None else max(planjob.min_start_date,
                                                                                                 max_finish_date)
                if max_finish_date is not None:
                    task_date = max_finish_date.date()
                    dates = resource.available_slots.keys()
                    for date_str in sorted(dates):
                        date = datetime.strptime(date_str, utils.DATE_FORMAT).date()
                        if date < task_date:
                            resource.available_slots.pop(date_str)
                        elif date == task_date:
                            resource.available_slots[date_str] = utils.get_superior_intervals(resource.available_slots[date_str],
                                                                                              max_finish_date)

    def change_scheduler_by_intervals_fraction(self):
        '''
        Modifica os available slots dos recursos alocados nos planjobs se o planjob pode ser fracionado entre intervalos
        :return:
        '''
        for planjob in self.planjobs:
            if planjob.configs.fractioned_between_intervals or planjob.configs.nonstop_infinity:
                for resource in planjob.allocated_resources:
                    dates_to_remove = []
                    for date_str, slots in resource.available_slots.items():
                        for slot in slots:
                            if slot.complement is None:
                                self.build_complementary_slots(resource, date_str, slot)

                        resource.available_slots[date_str] = [slot for slot in slots
                            if scheduler_config_evaluating.evaluate_slot(slot, planjob, self.configs)]

                        if len(resource.available_slots[date_str]) == 0: dates_to_remove.append(date_str)

                    for date_str in dates_to_remove: #shift
                        resource.available_slots.pop(date_str)

    def adjust_scheduler_to_planjobs_nonstop(self):
        '''
        Faz o ajuste criando novos slots que suportam a restrição de planjobs nonstop infinity.
        Exige que os slots complementares já tenham sido inseridos nos slots alvo
        :return:
        '''
        for planjob in self.planjobs:
            if planjob.configs.nonstop_infinity:
                for resource in planjob.allocated_resources:
                    self.adjust_resource_scheduler(planjob, resource)
                    if resource.available_slots == {}:
                        pass #ToDo LoadBalancer or exception?

    def adjust_resource_scheduler(self, planjob, resource):
        dates_to_remove = []
        for (date, slots) in resource.available_slots.items():
            slots_to_remove = []
            for i in range(len(slots)):
                slot = slots[i]
                if slot.minutes() < planjob.time + planjob.setup:
                    if not self.interval_is_allowed(resource, slot, slot.complement[0]):
                        slots_to_remove.append(i)
                        continue

                    new_slot = Slot(slot.start_time, slot.start_time, slot.complement[0].finish_time)
                    new_slot.builders = [slot]
                    if len(slot.complement) == 1 and new_slot.minutes() < planjob.time + planjob.setup:
                        slots_to_remove.append(i)
                        continue

                    to_remove = False
                    for j in range(1, len(slot.complement)):
                        if not self.interval_is_allowed(resource, slot.complement[j-1], slot.complement[j]):
                            if new_slot.minutes() < planjob.time + planjob.setup:
                                slots_to_remove.append(i)
                                to_remove = True
                            break
                        else:
                            new_slot.finish_time = slot.complement[j].finish_time
                            new_slot.builders.append(slot.complement[j])

                    if not to_remove:
                        slots[i] = new_slot

            for i in sorted(slots_to_remove, reverse=True): resource.available_slots[date].pop(i)
            if resource.available_slots[date] == []: dates_to_remove.append(date)

        for date in dates_to_remove: resource.available_slots.pop(date)

    def build_complementary_slots(self, resource, date_str, slot):
        '''
        Constroi os slots complementares dos available slots do recursos passado como parâmetro
        :param resource:
        :param date_str:
        :param slot:
        :return:
        '''
        next_slot = self.get_slot_after_interval(slot, resource, date_str)
        if next_slot is None:
            return [slot.light_copy()]
        else:
            new_date_str = next_slot.start_time.strftime(utils.DATE_FORMAT)
            complementary = self.build_complementary_slots(resource, new_date_str, next_slot)
            slot.complement = copy.deepcopy(complementary)
            complementary.insert(0, slot.light_copy())
            return complementary

    def get_slot_after_interval(self, slot, resource, date_str):
        interval = self.get_interval_neighbor(resource, slot)
        if interval is not None:
            index = resource.available_slots[date_str].index(slot)
            for next_slot in resource.available_slots[date_str][index:]:
                if utils.time(interval.finish_time) == utils.time(next_slot.start_time):
                    return next_slot
        else:
            if resource.is_slot_on_the_tail(slot):
                tomorrow_str = (slot.finish_time.date() + timedelta(days=1)).strftime(utils.DATE_FORMAT)
                if tomorrow_str in resource.available_slots.keys() and len(resource.available_slots[tomorrow_str]) > 0:
                    first_available = resource.available_slots[tomorrow_str][0]
                    if resource.is_slot_on_the_head(first_available):
                        return first_available

    def slot_is_enough_same_start(self, slot_intersection, all_planjobs_slots, configs):
        """
        Verifica se o slot de interseção é suficiente para todas as tarefas considerando a restrição de começarem
        no mesmo instante

        O formato do segundo parâmetro é
        all_tasks_slots = {task1: [(datetime, datetime), (datetime, datetime)]}

        :param slot_intersection: slot de interseção de tempo dos planjob
        :param all_planjobs_slots: dicionario de planjob por lista de slots de tempo
        :return: True se é suficiente, False caso contrário
        """
        # ToDo: pensar sobre slot_allowed. só preciso checar a intercessão mo primeiro slot que será usados
        for (planjob, resources_slot) in all_planjobs_slots.items():
            if planjob.configs.fractioned_between_intervals and \
                    not self.is_complement_slots_concomitant(planjob, resources_slot, slot_intersection[0]):
                return False

            for slot in resources_slot:
                if planjob.configs.fractioned_between_planjobs or planjob.configs.fractioned_between_intervals:
                    slot_allowed = Slot(slot_intersection[0], slot_intersection[0], slot.finish_time)
                    slot_allowed.complement = slot.complement
                    if not scheduler_config_evaluating.evaluate_slot(slot_allowed, planjob, configs):
                        return False
                else:
                    allowed_time = (slot.finish_time - slot_intersection[0]).total_seconds() / 60
                    lower_than_limits = LoadBalancer.slot_is_allowed(slot, planjob, configs)
                    if (allowed_time < planjob.time + planjob.setup and not planjob.configs.is_deadline) \
                            or (not lower_than_limits) \
                            or (planjob.configs.is_deadline and allowed_time == 0):
                        return False
        return True

    def slot_is_enough_same_finish(self, slot_intersection, all_tasks_slots, configs):
        """
            Verifica se o slot de interseção é suficiente para todas as tarefas considerando a restrição de terminarem
            no mesmo instante

            O formato do segundo parâmetro é
            all_tasks_slots = {task1: [(datetime, datetime), (datetime, datetime)]}

            :param slot_intersection: slot de interseção de tempo das tarefas
            :param all_tasks_slots: dicionario de tarefas por lista de slots de tempo
            :return: True se é suficiente, False caso contrário
            """
        for (planjob, resources_slot) in all_tasks_slots.items():
            for slot in resources_slot:
                # if planjob.configs.fractioned_between_planjobs:
                #    return scheduler_config_evaluating.evaluate_slot(slot, planjob, configs)
                # else:
                lower_than_limits = LoadBalancer.slot_is_allowed(slot, planjob, configs)
                allowed_time = (slot_intersection[1] - slot.start_time).total_seconds() / 60
                if allowed_time < planjob.time + planjob.setup or not lower_than_limits:
                    return False

        return True

    def slot_is_enough_same_start_and_finish(self, slot_intersection, all_tasks_slots, configs=[]):
        '''
        Analisa se um slot de interseção é satisfatório para todos os planjobs respeitando suas limitações
        de inicio-inicio e/ou fim-fim
        :param slot_intersection:
        :param all_tasks_slots:
        :param configs:
        :return:
        '''
        for (planjob, resources_slot) in all_tasks_slots.items():
            for slot in resources_slot:
                if len(planjob.same_start) > 0 and len(planjob.same_finish) > 0:
                    duration = (slot_intersection[1] - slot_intersection[0]).total_seconds() / 60
                    if duration < planjob.time + planjob.setup: return False
                elif len(planjob.same_start) > 0:
                    allowed_time = (slot.finish_time - slot_intersection[0]).total_seconds() / 60
                    if allowed_time < planjob.time + planjob.setup: return False
                elif len(planjob.same_finish) > 0:
                    allowed_time = (slot_intersection[1] - slot.start_time).total_seconds() / 60
                    if allowed_time < planjob.time + planjob.setup: return False
        return True

    def get_interval_neighbor(self, resource, slot):
        '''
        Retorna, se existir, o intervalo que segue após o slot passado como parâmetro do recurso fornecido
        :param resource:
        :param slot:
        :return:
        '''
        date = slot.start_time.date()
        for interval in resource.get_intervals_by_journey_date(date):
            if utils.time(slot.finish_time) == utils.time(interval.start_time):
                return interval

    def get_planjob_by_id(self, id):
        '''
        Retorna um planjob pelo seu id
        :param id:
        :return:
        '''
        for planjob in self.all_planjobs:
            if planjob.id == id:
                return planjob

    def is_complement_slots_concomitant(self, planjob, resources_slot, new_start_time):
        '''
        Verifica se os slots complementares e o slot raiz dos resources slots acontecem de maneira concomitante
        :param planjob:
        :param resources_slot:
        :param new_start_time:
        :return:
        '''
        complements = []
        min_len = None
        finish_time = resources_slot[0].finish_time
        all_finish_time_equals = True
        all_slots_are_enough = True
        for slot in resources_slot:
            if slot.finish_time != finish_time: all_finish_time_equals = False

            current_duration = (slot.finish_time - new_start_time).total_seconds() // 60
            if current_duration < planjob.time + planjob.setup: all_slots_are_enough = False

            if min_len is None: min_len = len(slot.complement)
            if len(slot.complement) < min_len: min_len = len(slot.complement)
            complements.append(slot.complement)

        if all_slots_are_enough: return True
        if not all_slots_are_enough and not all_finish_time_equals: return False

        total_duration = (finish_time - new_start_time).total_seconds() // 60
        for i in range(min_len):
            slots = set([complement[i] for complement in complements])
            min_slot = min(slots)
            duration = (min_slot.finish_time - min_slot.start_time).total_seconds() // 60
            partial = total_duration + duration

            if len(slots) != 1 and partial < planjob.time + (i * planjob.setup):
                return False
            elif partial >= planjob.time + (i * planjob.setup):
                return True
            total_duration = partial

        return False

    def interval_is_allowed(self, resource, slot, next_slot):
        return resource.has_util_interval_allowed_btw_slots(slot, next_slot)

    def is_nonstop_infinity_slot_valid(self, resource, date_str, slot, planjob, start_time):
        '''
        Reecebe um slot, constroi os complementos dele e verifica se ele com seus complementos são
        suficientes para comportar o tempo demandado pelo planjob
        :param resource: recurso a que pertence o slot
        :param date_str: data desejada na forma string
        :param slot: slot a ser verifcado
        :param planjob: planjob com o tempo a ser alocado
        :param start_time: data agendada desse planjob
        :return:
        '''
        self.build_complementary_slots(resource, date_str, slot)

        duration = slot.minutes()
        if duration < planjob.time + planjob.setup:
            if slot.complement is None or not self.interval_is_allowed(resource, slot, slot.complement[0]): return False

            new_slot = Slot(start_time, start_time, slot.complement[0].finish_time)
            new_slot.builders = [slot]
            if len(slot.complement) == 1 and new_slot.minutes() < planjob.time + planjob.setup: return False

            for j in range(1, len(slot.complement)):
                if not self.interval_is_allowed(resource, slot.complement[j - 1], slot.complement[j]):
                    if new_slot.minutes() < planjob.time + planjob.setup:
                        return False
                else:
                    new_slot.finish_time = slot.complement[j].finish_time
                    new_slot.builders.append(slot.complement[j])

        return True

    def is_fractioned_intervals_slot_valid(self, resource, date_str, slot, planjob, start_time=None):
        '''
        Reecebe um slot, constroi os complementos dele e verifica se ele com seus complementos são
        suficientes para comportar o tempo demandado pelo planjob
        :param resource: recurso a que pertence o slot
        :param date_str: data desejada na forma string
        :param slot: slot a ser verifcado
        :param planjob: planjob com o tempo a ser alocado
        :param start_time: data agendada desse planjob
        :return:
        '''
        self.build_complementary_slots(resource, date_str, slot)
        if start_time is not None: slot.start_time = start_time
        return scheduler_config_evaluating.evaluate_slot(slot, planjob, self.configs)

    def choose_eval_function(self):
        '''
        Escolhe a função de avaliação correta de acordo com os relacionamento que os planjobs têm entre si
        -- apenas inicio-inicio
        -- apenas fim-fim
        -- inicio-inicio e fim-fim
        :return:
        '''
        if self.same_start and self.same_finish:
            return self.slot_is_enough_same_start_and_finish
        elif self.same_start:
            return self.slot_is_enough_same_start
        else:
            return self.slot_is_enough_same_finish

    def get_start_dates_same_start_finish_planjobs(self):
        '''
        Seleciona os datetimes que existem em todos os recursos alocados aos planjobs que satisfazem os tempos de
        execução desses mesmos planjobs
        :return: uma lista ordenada do menor para o maior com os datetimes encontrados
        '''
        for i in range(len(self.planjobs)):
            planjob = self.planjobs[i]
            for j in range(len(planjob.allocated_resources)):
                resource = planjob.allocated_resources[j]
                if i == j == 0:
                    start_dates_pj = self.get_initial_start_dates(resource, planjob)
                else:
                    for date_str in start_dates_pj.keys():
                        if date_str in resource.available_slots.keys():
                            starts = set([])
                            for slot in resource.available_slots[date_str]:
                                if slot.minutes() >= planjob.time + planjob.setup:
                                    start = slot.finish_time - timedelta(minutes=planjob.time + planjob.setup)
                                    while start >= slot.start_time:
                                        starts.add(start)
                                        start = start - timedelta(minutes=self.configs.same_start_finish_dates_range)
                            start_dates_pj[date_str].intersection_update(starts)

                        else:
                            start_dates_pj.pop(date_str)

        return sorted([start_date for date_str in start_dates_pj.keys() for start_date in start_dates_pj[date_str]])

    def get_initial_start_dates(self, resource, planjob):
        '''
        Monta o conjunto inicial de start dates a partir do recurso passado como parâmetro.
        Por questões de complexidade quando um slot de tempo é maior que a duração do planjob, em vez de de pegar os
        start times com diferença de 1 minuto entre um e outro, se pega a diferença a cada 10 minutos.
        :param resource: recurso de onde serão pegas as datas iniciais
        :param planjob: planjob ao qual esse resource está alocado
        :return: um dict onde as chaves são as datas em string e os values os start time em datetime
        '''
        start_dates_pj = {}
        for (date_str, slots) in resource.available_slots.items():
            start_dates_pj[date_str] = set([])
            for slot in slots:
                if slot.minutes() >= planjob.time+planjob.setup:
                    start = slot.finish_time - timedelta(minutes=planjob.time + planjob.setup)
                    while start >= slot.start_time:
                        start_dates_pj[date_str].add(start)
                        start = start - timedelta(minutes=self.configs.same_start_finish_dates_range)

        return start_dates_pj

    @staticmethod
    def filter_resource_by_date(resource, inferior_limit):
        date_limit = inferior_limit.date()
        dates = resource.available_slots.keys()
        for date_str in sorted(dates):
            date = datetime.strptime(date_str, utils.DATE_FORMAT).date()
            if date < date_limit:
                resource.available_slots.pop(date_str)
            elif date == date_limit:
                resource.available_slots[date_str] = utils.get_superior_intervals(resource.available_slots[date_str],
                                                                                  inferior_limit)