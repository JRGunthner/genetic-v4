# coding: utf-8

from datetime import timedelta

from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler import scheduler_utils, scheduler_config_evaluating
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourcesException
from pcp_scheduler.utils import utils

class RelayStrategy:
    def __init__(self, planjob, solutions, configs, predecessors=[]):
        self.planjob = planjob
        self.solutions = solutions
        self.configs = configs
        self.predecessors = predecessors

    def allocate(self):
        """
        Faz a alocação do planjob passado no construtor usando a estratégia de revezamento
        :return:
        """
        self.allocate_simple_planjob(self.planjob, self.predecessors)

    def allocate_simple_planjob(self, planjob, predecessors):
        '''
        Faz a alocação do planjob passado como parâmetro, ou lança InsufficientResourceCalendarException caso não
        consiga alocar este planjob
        :param planjob: planjob a ser alocado
        :param predecessors: predecessores desse planjob a ser alocado
        :return:
        '''

        start_times = self.get_start_times(planjob, predecessors)
        desired_resources = self.build_desired_resources()
        allocation_found = False
        slots = []

        for start_time in start_times:
            start = start_time
            slots = []
            remainder = planjob.time
            while True:
                if remainder == 0:
                    allocation_found = True
                    break

                slot_found = self.find_next_slot(start, remainder, planjob, desired_resources)
                if slot_found is None: break

                slots.append(slot_found)
                remainder -= (slot_found.minutes() - planjob.setup)
                start = slot_found.finish_time

            if allocation_found: break

        if not allocation_found:
            value = {'planjobs': [planjob.id],
                     'resources': [r.id for desired_resource in desired_resources for r in desired_resource]}
            raise InsufficientResourceCalendarException(value)
        elif not self.scheduled_date_respected(slots, planjob):
            value = {'planjobs': [planjob.id],
                     'resources': [r.id for desired_resource in desired_resources for r in desired_resource]}
            raise InsufficientResourceCalendarException(value)
        else:
            planjob.execution_slots = slots
            planjob.allocated_resources = list(set([resource for slot in slots for resource in slot.resources]))

    def find_next_slot(self, start_time, remainder, planjob, desired_resources):
        '''
        Encontra o próximo slot que inicia a partir de start_time em que os desired resources do planjob possam operá-lo
        :param start_time: datetime a partir do qual procurar o próximo slot
        :param remainder: tempo restante para concluir o planjob
        :param planjob: planjob que deseja o slot
        :param desired_resources: lista de lista de recursos que contém os desired resources do planjob
        :return: o próximo slot que será executado este planjob
        '''
        potential_slots = self.find_potential_slots(start_time, planjob, desired_resources)
        potential_slots.sort(key=lambda s: s.start_time)

        for slot in potential_slots:
            if slot.minutes() >= remainder + planjob.setup:
                slot.finish_time = slot.start_time + timedelta(minutes=remainder+planjob.setup)
                return slot
            else:
                rest_time = remainder - (slot.minutes() - planjob.setup)
                rest_slot = Slot(slot.finish_time, slot.finish_time, slot.finish_time + timedelta(minutes=rest_time))
                if scheduler_config_evaluating.is_relay_slot_valid(rest_slot, planjob, self.configs):
                    return slot
                else:
                    diff = scheduler_config_evaluating.get_diff_to_be_valid_relay_slot(rest_slot, planjob, self.configs)
                    slot_temp = slot.light_copy()
                    slot_temp.finish_time = slot_temp.finish_time - timedelta(minutes=diff)
                    if scheduler_config_evaluating.is_relay_slot_valid(slot_temp, planjob, self.configs):
                        slot_temp.resources = slot.resources
                        return slot_temp

    def find_potential_slots(self, start_time, planjob, desired_resources):
        '''
        Encontra os slots que satisfazem a necessidade de alocação do planjob a partir da start_time usando os
        desired resources passados como parâmetros
        :param start_time: tempo a partir do qual se necessita formar opções de potential_slots
        :param planjob: planjob que deseja os potential slots
        :param desired_resources: recursos que podem satisfazer as necessidade de encontrar os potential slots
        :return:
        '''
        potential_slots = []
        try_match = False
        for desired_resource in desired_resources:
            new_potential_slots = []
            for resource in desired_resource:
                if not try_match:
                    slot = self.find_first_slot_valid(resource, start_time, planjob)
                    slot.resources = [resource]
                    potential_slots.append(slot)
                else:
                    new_potential_slots.extend(self.search_match_potential_slots(potential_slots, resource, planjob))

            if try_match:
                if len(new_potential_slots) == 0: return []
                potential_slots = []
                potential_slots.extend(new_potential_slots)
            try_match = True

        return potential_slots

    def find_first_slot_valid(self, resource, start_time, planjob):
        '''
        Encontra o primeiro slot do resource, após o start_time, que satisfaz as restrições de um relay_slot
        :param resource: recurso a fornecer o slot
        :param start_time: datetime a partir do qual procurar o slot
        :param planjob: planjob a qual o resource está alocado
        :return:
        '''
        min_date_str = start_time.strftime(utils.DATE_FORMAT)
        for date_str in sorted(resource.available_slots.keys()):
            if date_str >= min_date_str:
                for slot in resource.available_slots[date_str]:
                    if self.slot_is_enough(slot, start_time, planjob):
                        new_slot = slot.light_copy()
                        if new_slot.start_time < start_time: new_slot.start_time = start_time
                        return new_slot

    def search_match_potential_slots(self, potential_slots, resource, planjob):
        '''
        Procura quais slots em resource ocorrem concomitante aos slots em potential_slots
        :param potential_slots: slots a se tentar fazer o match
        :param resource: recurso cujos slots serão analisados
        :param planjob: planjob ao qual o recursos está alocado
        :return: retorna todos os slots cuja interseção geram relay slots válidos.
        '''
        slots_matched = []
        for potential_slot in potential_slots:
            date_str = potential_slot.date.strftime(utils.DATE_FORMAT)
            if date_str not in resource.available_slots or resource in potential_slot.resources: continue

            for slot in resource.available_slots[date_str]:
                max_start = max(slot.start_time, potential_slot.start_time)
                min_finish = min(slot.finish_time, potential_slot.finish_time)
                if min_finish > max_start:
                    intersection = Slot(max_start, max_start, min_finish)
                    if scheduler_config_evaluating.is_relay_slot_valid(intersection, planjob, self.configs):
                        intersection.resources = potential_slot.resources[::]
                        intersection.resources.append(resource)
                        slots_matched.append(intersection)
        return slots_matched

    def slot_is_enough(self, slot, start_time, planjob):
        '''
        Verifica se o slot passado como parâmetro satisfaz a restrição de ocorrer a partir do start_time e ter duração
        suficiente para ser um relay slot válido
        :param slot: slot a analisar
        :param start_time: datetime que deve começar o slot
        :param planjob: planjob a qual esse slot será útil
        :return: True se é válido, False caso contrário
        '''
        if slot.finish_time <= start_time:
            return False

        elif slot.start_time <= start_time < slot.finish_time:
            tmp = slot.light_copy()
            tmp.start_time = start_time
            return scheduler_config_evaluating.is_relay_slot_valid(tmp, planjob, self.configs)

        return scheduler_config_evaluating.is_relay_slot_valid(slot, planjob, self.configs)

    def build_desired_resources(self):
        '''
        Constroi os desired_resources do planjob que foram fornecidos nas solutions recebidas no construtor
        :return: desired_resources
        '''
        desired_resources = []
        for solution in self.solutions:
            for j in range(len(solution)):
                if len(desired_resources) < j + 1:
                    desired_resources.insert(j, set([]))
                desired_resources[j].add(solution[j])

        return desired_resources

    def get_start_times(self, planjob, predecessors):
        if planjob.scheduled_date is not None: return [planjob.scheduled_date]

        start_times = set([])
        max_finish_time_predecessor = scheduler_utils.get_max_finish_time_predecessor(planjob, predecessors)
        date_limit = max_finish_time_predecessor.strftime(utils.DATE_FORMAT) if max_finish_time_predecessor is not None \
            else None

        resources_visited = []
        for solution in self.solutions:
            for resource in solution:
                if resource.id in resources_visited:
                    continue
                else: resources_visited.append(resource.id)

                for date_str in resource.available_slots.keys():
                    if date_limit is None or (date_limit is not None and date_str >= date_limit):
                        for slot in resource.available_slots[date_str]:
                            start_time = max_finish_time_predecessor if max_finish_time_predecessor is not None else slot.start_time
                            if self.slot_is_enough(slot, start_time, planjob):
                                start_times.add(start_time)

        return sorted(list(start_times))

    def scheduled_date_respected(self, slots, planjob):
        '''
        Verifica se o planjob tem data agendada e se tem verifica se ela foi respeitada na alocação
        :param slots: slots a analisar
        :param planjob: planjob alvo
        :return:
        '''
        if planjob.scheduled_date is not None:
            return planjob.scheduled_date in [slot.start_time for slot in slots]
        return True