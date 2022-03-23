# coding: utf-8

import random

from pcp_scheduler.src.scheduler import scheduler_utils

from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourcesException
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler.SchedulerFilter import SchedulerFilter
from pcp_scheduler.utils import utils
from .strategies.SameDayStrategy import SameDayStrategy
from .strategies.SchedledDateStrategy import ScheduledDateStrategy
from .strategies.OrdinaryStrategy import OrdinaryStrategy
from .strategies.NonstopVigilStrategy import NonstopVigilyStrategy
from .strategies.RelayStrategy import RelayStrategy
from .strategies.SameStartFinishStrategy import SameStartFinishStrategy
from .resource_filter import ResourceFilter

'''
Entrada:
 - listas de planjobs com seu tempo de duração e suas dependencias
 - matriz de alocação de recursos no tempo
'''


class Scheduler:
    def __init__(self, grid, planjobs, configs, non_working_days=[]):
        self.grid = grid
        self.configs = configs
        self.planjobs = self.define_planjobs_dict(planjobs)
        self.non_working_days = non_working_days

    def can_allocate_planjob(self, planjob):
        '''
        Verifica se um planjob pode ser alocado. Se o planjob é simples ele pode ser alocado se todos os seus predecessores
        já o foram. Se ele tem alguma restrição de inicio-inicio e/ou fim-fim ele pode ser alocado quando é o mais profundo
        entre seus siblings e quando seus predecessores e os predecessores de seus siblings já estão alocados
        :param planjob: planjob a analisar
        :return: True se pode alocar, False caso contrário
        '''

        if len(planjob.execution_slots) > 0:
            return False

        planjob.visited = True
        is_simple_planjob = False
        all_planjobs = set([planjob])
        ids = set([])

        if len(planjob.same_start) == 0 and len(planjob.same_finish) == 0:
            is_simple_planjob = True

        elif self.is_same_start_and_same_finish(planjob):
            ids.update([sibling for sibling in planjob.same_start])
            ids.update([sibling for sibling in planjob.same_finish])
            ids.update(
                [other_id for sibling_id in planjob.same_start for other_id in self.get_planjob_by_id(sibling_id).same_finish])
            ids.update(
                [other_id for sibling_id in planjob.same_finish for other_id in self.get_planjob_by_id(sibling_id).same_start])

        elif len(planjob.same_start) > 0:
            ids.update([sibling for sibling in planjob.same_start])

        elif len(planjob.same_finish) > 0:
            ids.update([sibling for sibling in planjob.same_finish])

        if not is_simple_planjob:
            all_planjobs.update([self.get_planjob_by_id(id) for id in ids])
            max_deepness = max([pj.deepness for pj in all_planjobs])
            if planjob.deepness < max_deepness:
                return False

        for pj in all_planjobs:
            for predecessor_id in pj.predecessors:
                predecessor = self.get_planjob_by_id(predecessor_id)
                if len(predecessor.execution_slots) == 0:
                    return False

        return True

    def allocate_planjob(self, planjob):
        if self.can_allocate_planjob(planjob):
            if self.is_same_start_and_same_finish(planjob):
                allocated_tasks = self.allocate_same_start_and_finish_planjob(planjob)
                self.update_grid(allocated_tasks)
                self.update_visited_successor(allocated_tasks)
            elif len(planjob.same_start) > 0:
                allocated_tasks = self.allocate_same_start_planjob(planjob)
                self.update_grid(allocated_tasks)
                self.update_visited_successor(allocated_tasks)
            elif len(planjob.same_finish) > 0:
                allocated_tasks = self.allocate_same_finish_planjob(planjob)
                self.update_grid(allocated_tasks)
                self.update_visited_successor(allocated_tasks)
            else:
                allocated_tasks = self.allocate_simple_planjob(planjob)
                self.update_grid(allocated_tasks)
                # Todo será que não precisa? update_visited_successor(allocated_tasks, configs)

    def allocate_simple_planjob(self, planjob):
        """
        Faz a alocação de uma tarefa simples, ou seja, que não tem restrição de inicio-inicio ou
        fim-fim com outra tarefa
        :param planjob: planjob a ser alocado
        :param grid: grade de alocação de recursos
        :param configs: configurações
        :return: lista dos planjobs alocados
        """
        resource_filter = ResourceFilter(self.get_planjobs(), self.configs, self.grid)
        solutions = resource_filter.get_desired_resources(planjob)
        if solutions == []:
            values = {"planjobs": [planjob.id]}
            raise InsufficientResourcesException(values)

        if planjob.configs.nonstop_vigily_mode:
            predecessors = [self.get_planjob_by_id(id) for id in planjob.predecessors]
            strategy = NonstopVigilyStrategy(planjob, solutions, self.configs, predecessors)
            strategy.allocate()

        elif planjob.configs.relay:
            predecessors = [self.get_planjob_by_id(id) for id in planjob.predecessors]
            strategy = RelayStrategy(planjob, solutions, self.configs, predecessors)
            strategy.allocate()

        elif planjob.scheduled_date is not None:
            chosen_solution = scheduler_utils.get_resources_copy(random.choice(solutions))
            planjob.allocated_resources = chosen_solution
            strategy = ScheduledDateStrategy([planjob], self.configs, all_planjobs=self.get_planjobs())
            strategy.allocate()

        else:
            chosen_solution = scheduler_utils.get_resources_copy(random.choice(solutions))
            planjob.allocated_resources = chosen_solution

            filter = SchedulerFilter([planjob], self.configs, self.get_planjobs())
            potential_slots = filter.define_correspondent_slots()

            if len(potential_slots) == 0:
                resources = [resource.id for resource in planjob.allocated_resources]
                raise InsufficientResourceCalendarException({'planjobs': [planjob.id], 'resources': resources})

            if planjob.configs.same_day:
                strategy = SameDayStrategy([planjob], potential_slots, self.configs)
            else:
                strategy = OrdinaryStrategy([planjob], potential_slots, self.configs, same_start=True, all_planjobs=self.get_planjobs(), non_working_days=self.non_working_days)
            strategy.allocate()

        return [planjob]

    def allocate_same_start_planjob(self, planjob):
        """
        Aloca na grade de horários uma tarefa com todas as tarefas irmãs dela que têm restrição
        de inicio-inicio
        :param planjob: tarefa a ser alocada junto com suas irmãs
        :param grid: grade de alocação de recursos
        :param configs: configurações
        :return: uma lista dos planjobs
        """
        planjobs = self.choose_planjobs_resources(planjob, planjob.same_start)

        if utils.has_any_planjob_scheduled(planjobs):
            strategy = ScheduledDateStrategy(planjobs, self.configs, all_planjobs=self.get_planjobs())
            strategy.allocate()
        else:
            filter = SchedulerFilter(planjobs, self.configs, self.get_planjobs(), same_start=True)
            potential_slots = filter.define_correspondent_slots()

            if potential_slots == {}:
                resources = [resource.id for planjob in planjobs for resource in planjob.allocated_resources]
                planjobs = planjob.same_start[::]
                planjobs.append(planjob.id)
                raise InsufficientResourceCalendarException({'planjobs': planjobs, 'resources': resources})

            if utils.has_planjob_same_day(planjobs):
                strategy = SameDayStrategy(planjobs, potential_slots, self.configs)
            else:
                strategy = OrdinaryStrategy(planjobs, potential_slots, self.configs, same_start=True)

            strategy.allocate()

        return planjobs

    def allocate_same_finish_planjob(self, planjob):
        """
        Aloca na grade de horários uma tarefa com todas as tarefas irmãos dela que têm restrição
        de fim-fim
        :param planjob: tarefa a ser alocada junto com suas irmãs
        :param grid: grade de alocação de recursos
        :param configs: configurações
        :return: uma lista dos planjobs
        """
        # Todo: colocar um validador aqui
        # não pode ter nonstop_infinity
        planjobs = self.choose_planjobs_resources(planjob, planjob.same_finish)

        filter = SchedulerFilter(planjobs, self.configs, self.get_planjobs(), same_finish=True)
        potential_slots = filter.define_correspondent_slots()

        if potential_slots == {}:
            resources = [resource.id for planjob in planjobs for resource in planjob.allocated_resources]
            planjobs = planjob.same_finish[::]
            planjobs.append(planjob.id)
            raise InsufficientResourceCalendarException({'planjobs': planjobs, 'resources': resources})

        if utils.has_planjob_same_day(planjobs):
            strategy = SameDayStrategy(planjobs, potential_slots, self.configs)
        else:
            strategy = OrdinaryStrategy(planjobs, potential_slots, self.configs, same_finish=True)

        strategy.allocate()

        return planjobs

    def allocate_same_start_and_finish_planjob(self, planjob):
        siblings = set([])
        siblings.update([sibling_id for sibling_id in planjob.same_start])
        siblings.update([sibling_id for sibling_id in planjob.same_finish])
        siblings.update(
            [other_id for sibling_id in planjob.same_start for other_id in self.get_planjob_by_id(sibling_id).same_finish])
        siblings.update(
            [other_id for sibling_id in planjob.same_finish for other_id in self.get_planjob_by_id(sibling_id).same_start])
        siblings.discard(planjob.id)

        planjobs = self.choose_planjobs_resources(planjob, siblings)
        strategy = SameStartFinishStrategy(planjobs, self.configs, self.get_planjobs())
        strategy.allocate()
        return planjobs

    def update_grid(self, planjobs):
        for planjob in planjobs:
            if not planjob.configs.is_deadline:
                for allocated_resource in planjob.allocated_resources:
                    resource = self.get_resource_by_id(allocated_resource.id)
                    self.update_scheduled_resource(planjob, resource)

    def update_scheduled_resource(self, planjob, resource):
        for execution_slot in planjob.execution_slots:
            if execution_slot.resources is not None and resource not in execution_slot.resources:
                continue
            dates = scheduler_utils.get_dates_in_slot(execution_slot)
            for date in dates:
                date_str = date.strftime(utils.DATE_FORMAT)
                indexes_to_remove = []
                for i in range(len(resource.available_slots[date_str])):
                    slot = resource.available_slots[date_str][i]
                    max_start = max(slot.start_time, execution_slot.start_time)
                    min_finish = min(slot.finish_time, execution_slot.finish_time)

                    if max_start < min_finish:
                        if slot.start_time == max_start and slot.finish_time == min_finish:
                            indexes_to_remove.append(i)
                        elif slot.start_time == max_start:
                            if min_finish.date() == date:
                                resource.available_slots[date_str][i] = Slot(date, min_finish, slot.finish_time)
                            else:
                                new_slot = Slot(min_finish, min_finish, slot.finish_time)
                                indexes_to_remove.append(i)
                                self.add_slot_in_correct_date(new_slot, resource)
                        elif slot.finish_time == min_finish:
                            resource.available_slots[date_str][i] = Slot(date, slot.start_time, max_start)
                        else:
                            resource.available_slots[date_str][i] = Slot(date, slot.start_time, max_start)
                            if min_finish.date() == date:
                                resource.available_slots[date_str].insert(i + 1,
                                                                          Slot(date, min_finish, slot.finish_time))
                            else:
                                new_slot = Slot(min_finish, min_finish, slot.finish_time)
                                indexes_to_remove.append(i)
                                self.add_slot_in_correct_date(new_slot, resource)

                        if max_start == execution_slot.start_time and min_finish == execution_slot.finish_time: break

                for index in sorted(indexes_to_remove, reverse=True):
                    resource.available_slots[date_str].pop(index)

                if resource.available_slots[date_str] == []:
                    resource.available_slots.pop(date_str)

    def update_visited_successor(self, allocated_tasks):
        for allocated_task in allocated_tasks:
            for successor_id in allocated_task.successors:
                successor = self.get_planjob_by_id(successor_id)
                if successor.visited:
                    self.allocate_planjob(successor)

    def add_slot_in_correct_date(self, new_slot, resource):
        date_str = new_slot.date.strftime(utils.DATE_FORMAT)
        resource.available_slots[date_str] = resource.available_slots.get(date_str, [])
        resource.available_slots[date_str].append(new_slot)
        resource.available_slots[date_str].sort()

    def is_same_start_and_same_finish(self, planjob):
        '''
        Verifica se um planjob, ou algum de seus siblings, tem ao mesmo tempo restrições de inicio-incio e fim-fim
        :param planjob:
        :return:
        '''
        if len(planjob.same_start) > 0 and len(planjob.same_finish) > 0:
            return True
        elif len(planjob.same_start) > 0:
            for sibling_id in planjob.same_start:
                sibling = self.get_planjob_by_id(sibling_id)
                if len(sibling.same_finish) > 0:
                    return True
        elif len(planjob.same_finish) > 0:
            for sibling_id in planjob.same_finish:
                sibling = self.get_planjob_by_id(sibling_id)
                if len(sibling.same_start) > 0:
                    return True
        return False

    def choose_planjobs_resources(self, planjob_root, siblings_id):
        resource_filter = ResourceFilter(self.get_planjobs(), self.configs, self.grid)
        allocation = resource_filter.get_tasks_per_desired_resources(siblings_id, planjob_root)
        for (planjob, resources_list) in allocation.items():
            planjob.allocated_resources = scheduler_utils.get_resources_copy(resources_list)
        return list(allocation.keys())

    def get_resource_by_id(self, id):
        for resource in self.grid:
            if resource.id == id:
                return resource

    def get_planjob_by_id(self, id):
        return self.planjobs[id]

    def get_planjobs(self):
        return list(self.planjobs.values())

    def define_planjobs_dict(self, planjobs):
        planjobs_dict = {}
        for planjob in planjobs:
            planjobs_dict[planjob.id] = planjob
        return planjobs_dict


class Allocator:
    def __init__(self, grid, planjobs, configs):
        self.grid = grid
        self.configs = configs
        self.planjobs = self.define_planjobs_dict(planjobs)

    def generate_allocation(self):
        scheduler = Scheduler(self.grid, self.get_planjobs(), self.configs)
        planjobs_per_deepness = self.get_planjobs_per_deepness(self.get_planjobs())

        for deepness in sorted(planjobs_per_deepness.keys()):
            for planjob in planjobs_per_deepness[deepness]:
                scheduler.allocate_planjob(planjob)

    def get_planjobs_per_deepness(self, planjobs):
        self.set_planjob_deepness(planjobs)
        planjobs_per_deepness = {}

        for planjob in planjobs:
            planjobs_per_deepness[planjob.deepness] = planjobs_per_deepness.get(planjob.deepness, [])
            planjobs_per_deepness[planjob.deepness].append(planjob)

        return planjobs_per_deepness

    def set_planjob_deepness(self, planjobs):
        roots = [planjob for planjob in planjobs if len(planjob.predecessors) == 0]
        for root in roots:
            root.deepness = 0
            for successor_id in root.successors:
                successor = self.get_planjob_by_id(successor_id)
                self.set_deepness(successor, root.deepness)

    def set_deepness(self, planjob, parent_deepness):
        current_deepness = parent_deepness + 1
        planjob.deepness = current_deepness if current_deepness > planjob.deepness else planjob.deepness

        if len(planjob.successors) == 0 or current_deepness < planjob.deepness:
            return

        for successor_id in planjob.successors:
            successor = self.get_planjob_by_id(successor_id)
            self.set_deepness(successor, planjob.deepness)

    def get_planjob_by_id(self, id):
        return self.planjobs[id]

    def get_planjobs(self):
        return list(self.planjobs.values())

    def define_planjobs_dict(self, planjobs):
        planjobs_dict = {}
        for planjob in planjobs:
            planjobs_dict[planjob.id] = planjob
        return planjobs_dict
