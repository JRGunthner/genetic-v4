# coding: utf-8

import random

from pcp_scheduler.utils import utils
from . import scheduler_config_evaluating
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Tree import find_allocations
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourcesException
from pcp_scheduler.src.scheduler.SchedulerFilter import SchedulerFilter


class ResourceFilter:
    def __init__(self, planjobs, configs, grid):
        self.planjobs = self.set_planjobs(planjobs)
        self.configs = configs
        self.grid = grid

    def get_desired_resources(self, planjob):
        """
        Retorna uma lista de todos os recursos desejados por uma task
        :param planjob: planjob
        :param grid: grade de alocação de recursos
        :return: uma lista de recursos
        """
        planjobs = []
        for desired_resource in planjob.desired_resources:
            planjob_fake = Planjob(0, "planjob_fake", [])
            planjob_fake.resources = self.get_all_desired_resources(desired_resource)
            planjobs.append(planjob_fake)

        solutions = find_allocations(planjobs)
        solutions_allowed = [solution for solution in solutions
            if self.solution_is_allowed([planjob]*len(solution), solution)]

        return solutions_allowed

    def get_tasks_per_desired_resources(self, siblings_id, task_root):
        """
        Escolhe um recurso para a task passada como parâmetro e cada um de
        seus irmãos.
        Se não foi possível alocar um recurso para cada taks é lançada a exceção InsufficientResourcesException

        :param grid: tabela com os slots de disponibilidade de cada recurso
        :param siblings_id: lista de id de planjobs com restrição inicio-inicio ou fim-fim
        :param task_root: planjob com maior número de predecessores entre ela e seus siblings
        :param configs: configuraçoes globais do cenário
        :return: um dicionário onde as chaves são as tarefas e os valores os recursos que elas devem usar
        """
        tasks = []

        for desired_resource in task_root.desired_resources:
            task_fake = Planjob(task_root.time, task_root.id, [])
            task_fake.resources = self.get_all_desired_resources(desired_resource)
            task_fake.rate = len(task_fake.resources)
            tasks.append(task_fake)

        for sibling_id in siblings_id:
            sibling = self.get_planjob_by_id(sibling_id)
            for desired_resource in sibling.desired_resources:
                sibling_fake = Planjob(sibling.time, sibling.id, [])
                sibling_fake.resources = self.get_all_desired_resources(desired_resource)
                sibling_fake.rate = len(sibling_fake.resources)
                tasks.append(sibling_fake)

        tasks.sort(key=lambda t: t.rate)

        chosen_allocation = None
        chosen_perm = None
        permutacoes = utils.get_all_permutations(tasks)
        for perm in permutacoes:
            allocations = find_allocations(perm)
            if len(allocations) > 0:
                chosen_allocation = self.choose_resources_by_parameters(perm, allocations)
                chosen_perm = perm
                if chosen_allocation != []: break

        if chosen_allocation is None:
            tasks_exception = siblings_id
            tasks_exception.append(task_root.id)
            raise InsufficientResourcesException({'planjobs': tasks_exception})
        elif chosen_allocation == []:
            pass
            # TODO: tentei todas as perms e não consegui, preciso lançar exceção

        allocation = {task_root: []}
        for sibling_id in siblings_id:
            sibling = self.get_planjob_by_id(sibling_id)
            allocation[sibling] = []

        for task in allocation.keys():
            for i in range(len(chosen_perm)):
                if chosen_perm[i].id == task.id:
                    allocation[task].append(chosen_allocation[i])

        return allocation

    def choose_resources_by_parameters(self, perm, solutions):
        """
        Escolhe os recursos para cada jobplan baseado  nas configurações de prioridade de escolha de recursos
        :param perm: lista ordenada com os planjobs a serem alocados
        :param solutions: lista de listas que representa o conjunto de escolhas de recursos possíveis para cada jobplan,
         cada escolha esta ordenada de acordo com o planjob a que se destina.
        :return: uma solução de alocação de jobplans e recursos
        """
        num = random.randint(0, 99)
        metric = ""
        floor = 0
        for type_, prob in self.configs.prob_to_choose_between_resource.items():
            ceil = prob*100 + floor
            if floor <= num <= ceil:
                metric = type_
                break
            floor = ceil

        chosen = []
        mean = 100
        for solution in solutions:
            if self.solution_is_allowed(perm, solution):
                priorities = self.calc_factor(solution, metric)
                solution_mean = utils.median_low(priorities)
                if solution_mean < mean:
                    chosen = solution
                    mean = solution_mean
        return chosen

    def calc_factor(self, solution, chosen_type):
        """
        Recebe uma lista de recursos e uma métrica e calcula o valor dessa métrica para cada recurso
        :param solution:
        :param chosen_type:
        :return:
        """
        if chosen_type == "priority":
            return [resource.priority for resource in solution]
        elif chosen_type == "cost":
            pass
        elif chosen_type == "availability":
            pass
        else:
            pass

    def solution_is_allowed(self, ordered_planjobs, ordered_solution):
        """
        Recebe uma lista de planjobs e uma lista de recursos, onde o planjob na posição ordered_planjobs[i] deseja
            alocar o recurso na posição solution[i]
        :param ordered_planjobs: lista de planjobs que serão alocados aos recursos de solution
        :param ordered_solution: lista de recursos desejado
        :return: verdadeiro ou false, se estes planjobs podem ou não ser alocados a estes recursos
        """
        if len(ordered_planjobs) != len(ordered_solution): return False

        if utils.has_any_planjob_scheduled(ordered_planjobs):
            # TODO: Aqui é um bom momento para validar se tem mais de uma scheduled_date. Mas talvez já tenha feito
            #  isso antes. Pensar sobre isso
            start_time = min([p.scheduled_date for p in ordered_planjobs if p.scheduled_date is not None])

            for i in range(len(ordered_planjobs)):
                planjob, resource = ordered_planjobs[i], ordered_solution[i]
                if not self.resource_is_suitable(resource, planjob, start_time):
                    return False
        return True

    def get_all_desired_resources(self, desired_resource):
        """
        Dada as caracteristicas dos recursos desejados e a grade de horários dos recursos, retorna uma lista de recursos
        :param grid: Grade de horários dos recursos
        :param desired_resource: Especificações do recurso desejado por uma Planjob
        :return: Uma lista de recursos que se enquadram nas especificações desejadas
        """
        selected_resources = []
        for resource_characteristic in desired_resource.resources_characteristic:
            if resource_characteristic.priority <= self.configs.max_priority_allowed:
                if len(resource_characteristic.resources) > 0:
                    resources = self.choose_by_resource(resource_characteristic.resources)
                elif len(resource_characteristic.groups) > 0:
                    resources = self.choose_by_group(resource_characteristic.groups, resource_characteristic.hour_type)
                elif len(resource_characteristic.sectors) > 0:
                    resources = self.choose_by_sector(resource_characteristic.sectors, resource_characteristic.hour_type)
                else:
                    resources = self.choose_by_hour_type(resource_characteristic.hour_type)

                for resource in resources:
                    index = utils.get_index_by_id(selected_resources, resource)
                    if index is None:
                        resource.priority = resource_characteristic.priority
                        resource.brothers = set(resources).difference([resource])
                        selected_resources.append(resource)
                    else:
                        selected_resources[index].priority = min(selected_resources[index].priority, resource.priority)
                        resource.brothers.update(set(resources).difference([resource]))

        return selected_resources

    def choose_by_resource(self, resourcesId):
        """
        Recebe uma lista de ids de recursos e retorna os recursos correspondentes a estes ids
        :param resourcesId: Lista de ids de recursos
        :param grid: grade de alocação de horários dos recursos
        :return: Uma lista de recursos
        """
        pre_selected_resources = []
        for resource in self.grid:
            if resource.id in resourcesId:
                pre_selected_resources.append(resource)

        return pre_selected_resources

    def choose_by_group(self, groups, hour_type):
        """
        Recebe uma lista de grupos, um tipo de hora de trabalho e grade de horários de recursos e verifica
        quais recursos estão em algum grupo da lista de grupos passada
        :param groups: lista de grupos de interesse
        :param hour_type: tipo de hora de trabalho de interesse
        :param grid: grade de horários dos recursos
        :param configs: configurações da alocação
        :return: Uma lista dos recursos que estão em pelo menos um grupo na lista de grupos passada.
        """
        pre_selected_resources = []
        for resource in self.grid:
            if resource.hour_type == hour_type:
                if self.configs.groups_as_subset:
                    if set(groups).issubset(resource.groups):
                        pre_selected_resources.append(resource)
                else:
                    if len(set(groups).intersection(resource.groups)) > 0:
                        pre_selected_resources.append(resource)

        return pre_selected_resources

    def choose_by_sector(self, sectors, hour_type):
        """
        Recebe uma lista de setores, um tipo de hora de trabalho e grade de horários de recursos e verifica
        quais recursos estão em algum setor, da lista de setores passada
        :param sectors: lista de setores de interesse
        :param hour_type: tipo de hora de trabalho de interesse
        :param grid: grade de horários dos recursos
        :return: Uma lista dos recursos que estão em pelo menos um setor na lista de setores passada.
        """
        pre_selected_resources = []
        for resource in self.grid:
            if resource.hour_type == hour_type and len(set(sectors).intersection(resource.sectors)) > 0:
                pre_selected_resources.append(resource)

        return pre_selected_resources

    def choose_by_hour_type(self, hour_type):
        """
         Recebe um tipo de hora de trabalho e grade de horários de recursos e verifica
         quais recursos tem a hora de trabalho como aquela passada como parâmetro
        :param hour_type: tipo de hora de trabalho de interesse
        :param grid: grade de horários dos recursos
        :return: Uma lista dos recursos com cujo o tipo de hora de trabalho é igual àquela passada como parâmetro.
        """
        pre_selected_resources = []
        for resource in self.grid:
            if resource.hour_type == hour_type:
                pre_selected_resources.append(resource)

        return pre_selected_resources

    def resource_is_suitable(self, resource, planjob, start_time):
        if planjob.configs.relay:
            return True

        date_str = start_time.strftime(utils.DATE_FORMAT)
        if date_str in resource.available_slots:
            for slot in resource.available_slots[date_str]:
                if slot.start_time <= start_time <= slot.finish_time:
                    if planjob.configs.nonstop_vigily_mode:
                        slot_temp = Slot(start_time, start_time, slot.finish_time)
                        return scheduler_config_evaluating.is_slot_nonstop_vigily_valid(slot_temp, planjob, self.configs)

                    elif planjob.configs.fractioned_between_planjobs:
                        slot_temp = Slot(start_time, start_time, slot.finish_time)
                        return scheduler_config_evaluating.evaluate_slot(slot_temp, planjob, self.configs)

                    elif planjob.configs.fractioned_between_intervals:
                        scheduler_filter = SchedulerFilter([planjob], self.configs, self.get_planjobs())
                        return scheduler_filter.is_fractioned_intervals_slot_valid(resource, date_str, slot, planjob,
                                                                                   start_time)
                    elif planjob.configs.nonstop_infinity:
                        scheduler_filter = SchedulerFilter([planjob], self.configs, self.get_planjobs())
                        return scheduler_filter.is_nonstop_infinity_slot_valid(resource, date_str, slot, planjob,
                                                                               start_time)
                    elif planjob.configs.is_deadline:
                        return True

                    else:
                        return scheduler_config_evaluating.evaluate_slot(slot, planjob, self.configs)
        return False

    def slot_is_enough_same_start(self, slot_intersection, all_planjobs_slots):
        """
        Verifica se o slot de interseção é suficiente para todas as tarefas considerando a restrição de começarem
        no mesmo instante
        O formato do segundo parâmetro é
        all_tasks_slots = {task1: [(datetime, datetime), (datetime, datetime)]}
        :param slot_intersection: slot de interseção de tempo dos planjob
        :param all_planjobs_slots: dicionario de planjob por lista de slots de tempo
        :return: True se é suficiente, False caso contrário
        """

        filter = SchedulerFilter(list(all_planjobs_slots.keys()), self.configs, self.get_planjobs())
        return filter.slot_is_enough_same_start(slot_intersection, all_planjobs_slots, self.configs)

    def get_planjobs(self):
        return list(self.planjobs.keys())

    def get_planjob_by_id(self, id):
        return self.planjobs[id]

    def set_planjobs(self, planjobs):
        planjobs_dict = {}
        for planjob in planjobs:
            planjobs_dict[planjob.id] = planjob
        return planjobs_dict
