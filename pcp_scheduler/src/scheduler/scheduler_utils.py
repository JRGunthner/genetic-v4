# coding: utf-8

from datetime import timedelta, datetime
import copy
from pcp_scheduler.utils import utils

def slot_is_enough(slot_intersection, all_tasks_slots, configs):
    return True


def define_correspondent_slots(current_slots, sibling_slots, sibling, configs, eval_function=slot_is_enough):
    """
    Encontra todos os slots em que existe interseção de disponibilidade entre dois recursos
    Retorna slots em potenciais no formato:
        potential_slots:
            { date1: {slot_intersection1: {task1: [resources_slots], ..., taskn:[resources_slots]}
                     slot_intersection2: {task1: [resources_slots], ..., taskn:[resources_slots]}
             ...
             daten:{...}

    :param current_slots: Slots de interseção em potencial definidos até agora
    :param sibling_slots: grade de alocação de um recurso
    :param sibling: tarefa para definir os slots correspondentes com aqueles já existente
    :param eval_function: função de avaliação se um slot de interseção é satisfatório para todas as tarefas envolvidas
    :return: slots de interseçao entre todas as tarefas apresentadas até agora.
    """
    intersect_dates = set(current_slots.keys()).intersection(sibling_slots.keys())
    potential_slots = {}

    for date in sorted(intersect_dates): #ordenar?
        pointer_sibling = 0
        pointer_current = 0
        sibling_slots_on_date = sibling_slots[date]
        current_slots_on_date = sorted(current_slots[date].keys())

        while True:
            if (pointer_sibling >= len(sibling_slots_on_date)) or (pointer_current >= len(current_slots_on_date)): #ToDO rever isso aqui, se as listas forem de tamanho diferente, como se comprta?
                break

            slot_sibling = sibling_slots_on_date[pointer_sibling]
            slot_current = current_slots_on_date[pointer_current]

            min_time_bound = max(slot_sibling.start_time, slot_current[0])
            max_time_bound = min(slot_sibling.finish_time, slot_current[1])

            if (max_time_bound - min_time_bound).total_seconds() > 0:
                slot_intersection = (min_time_bound, max_time_bound)
                all_tasks_slots = {}
                for (planjob, slot_lists) in current_slots[date][slot_current].items():
                    all_tasks_slots[planjob] = copy.deepcopy(slot_lists)
                all_tasks_slots[sibling] = all_tasks_slots.get(sibling, []) #do_copy
                all_tasks_slots[sibling].append(slot_sibling)

                if eval_function(slot_intersection, all_tasks_slots, configs):
                    potential_slots[date] = potential_slots.get(date, {})
                    potential_slots[date][slot_intersection] = all_tasks_slots

            if slot_sibling.finish_time <= slot_current[1]: pointer_sibling += 1
            if slot_current[1] <= slot_sibling.finish_time: pointer_current += 1

    return potential_slots


def get_initial_potential_slots(resources_desired, task, eval_function, configs):
    if eval_function is None: eval_function = slot_is_enough

    potential_slots = {}
    for (date, slots) in resources_desired.items():
        for slot in slots:
            if slot.minutes() == 0: continue

            slot_tuple = (slot.start_time, slot.finish_time)
            task_slot = {task: [slot]}
            if eval_function(slot_tuple, task_slot, configs):
                potential_slots[date] = potential_slots.get(date, {})
                potential_slots[date][slot_tuple] = task_slot

    # {date_str: {(slot_intersection): {task: [slot]}}}
    return potential_slots


def get_all_allocated_resources(planjobs):
    return set([resource for planjob in planjobs for resource in planjob.allocated_resources])


def get_resources_copy(resoources):
    resources_copy = []
    for resource in resoources:
        brothers = resource.brothers
        resource.brothers = None
        new_resource = copy.deepcopy(resource)
        new_resource.brothers = brothers
        resources_copy.append(new_resource)
    return resources_copy


def get_dates_in_slot(slot):
    days = (slot.finish_time - slot.start_time).days
    return [slot.start_time + timedelta(days=d) for d in range(days+1)]


def get_dates_in_interval(start_date, finish_date):
    days = (finish_date - start_date).days
    return [start_date + timedelta(days=d) for d in range(days+1)]


def get_dates_in_tuple(couple):
    days = (couple[1] - couple[0]).days
    return [couple[0] + timedelta(days=d) for d in range(days+1)]


def get_max_finish_time_predecessor(planjob, predecessors):
    if len(predecessors) > 0:
        first_predecessor = predecessors[0]
        max_finish_date = first_predecessor.execution_slots[-1].finish_time
        for i in range(1, len(predecessors)):
            predecessor = predecessors[i]
            if predecessor.execution_slots[-1].finish_time > max_finish_date:
                max_finish_date = predecessor.execution_slots[-1].finish_time
        return max_finish_date


def choose_finish_time_planjob_deadline(planjob, start_time, non_working_days=[]):
    finish_time = start_time + timedelta(minutes=planjob.time)

    if planjob.configs.only_working_days:
        for day in get_dates_in_interval(start_time, finish_time):
            if day.strftime(utils.DATE_FORMAT) in non_working_days:
                finish_time = finish_time + timedelta(days=1)

    min_date_allowed = finish_time.strftime(utils.DATE_FORMAT)

    dates = set([])
    for i in range(len(planjob.allocated_resources)):
        if i == 0:
            dates = set([date for date in planjob.allocated_resources[i].available_slots.keys() if date >= min_date_allowed])
        else:
            dates.intersection(planjob.allocated_resources[i].available_slots.keys())

    if len(dates) == 0: return None
    finish_date = datetime.strptime(sorted(dates)[0], utils.DATE_FORMAT)
    finish_time = finish_time.replace(year=finish_date.year, month=finish_date.month, day=finish_date.day)
    return finish_time
