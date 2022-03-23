# coding: utf-8
import numpy as np
import pandas as pd
import random
import copy
from pcp_scheduler.src.model.Deepness import TasksDeepness
from pcp_scheduler.src.model.Planjob import Planjob
from datetime import datetime

'''
Entrada:
 - listas de planjobs com seu tempo de duração e suas dependencias
 - matriz de alocação de recursos no tempo
'''


def generate_allocation(grid, tasks, configs, non_working_days):
    # organiza planjobs conforme linha do tempo
    tasks_per_deepness = get_tasks_per_deepness(tasks)
    # quantidade de processos indo desde o início até o último conforme tempo e planjobs realizados simultâneamente
    deepness = len(tasks_per_deepness.keys())
    # tempo máximo total conforme deepness
    greater_path = get_greater_path(tasks_per_deepness, tasks)

    population = generate_initial_population(configs, grid, tasks_per_deepness, non_working_days)
    best_allocation = set_best_allocation(None, population[0])

    for i in range(configs.allocator_params["gens_num"]): # 5 tasks, 11 process: 5!*11 = 1320 possibilidades
        # Crossover
        specimens = get_best_specimens(population, configs)
        for j in range(len(specimens), len(population)):
            changes_num = deepness
            sun_order = crossover(random.choice(specimens), random.choice(specimens), changes_num)
            population[j] = TasksDeepness(grid=copy.deepcopy(grid), configs=copy.deepcopy(configs),
                                          non_working_days=copy.deepcopy(non_working_days))
            population[j].tasks_deepness = sun_order
            population[j].crossover(grid, configs)

        # mutation
        rate = best_allocation[1] if best_allocation is not None else 1
        mutation(population[len(specimens):], rate*5, grid, configs)

        # evaluating
        evaluate_population(population)

        # finish
        if should_finish(population, best_allocation, greater_path, configs):
            break

        best_allocation = set_best_allocation(best_allocation, population[0])

    return build_response(best_allocation, population[0])


def generate_initial_population(configs, grid, tasks_per_deepness, non_working_days):
    population = []
    # população formada por "pop_size" (número de indivíduos)
    for i in range(configs.allocator_params["pop_size"]):
        memo = {}
        new_tasks = copy.deepcopy(tasks_per_deepness, memo)
        population.append(TasksDeepness(new_tasks, copy.deepcopy(grid), configs, non_working_days))

    evaluate_population(population)
    return population


def evaluate_population(population):
    for specimen in population:
        specimen.calc_fitness()


def get_best_specimens(population, configs):
    population.sort(key=lambda task_deepness: task_deepness.fitness)
    cut = len(population) // configs.allocator_params["elitism"]
    return population[:cut]


def crossover(dad, mom, changes_num):
    parents_order = [dad.tasks_deepness, mom.tasks_deepness]
    sun_order = copy.copy(random.choice(parents_order))

    indexes = len(dad.tasks_deepness) - 1
    for i in range(changes_num):
        choosed_index = random.randint(0, indexes)
        sun_order[choosed_index] = random.choice(parents_order)[choosed_index]

    result = []
    for deep in sun_order:
        deepness = []
        for t in deep:
            pj = Planjob(t.time, t.id, t.desired_resources, t.configs, t.setup)
            pj.clone(t)
            deepness.append(pj)
        result.append(deepness)
    return result


def mutation(population, rate, grid, configs):
    for specimen in population:
        specimen.mutation(rate, grid, configs)


def set_best_allocation(best_allocation, best_individual_on_round):
    if best_allocation is None and not best_individual_on_round.raise_exception():
        best_allocation = (best_individual_on_round, 1)
    elif best_allocation is not None and best_allocation[0].fitness <= best_individual_on_round.fitness:
        best_allocation = (best_allocation[0], best_allocation[1] + 1)
    elif best_allocation is not None and best_individual_on_round.fitness < best_allocation[0].fitness:
        best_allocation = (best_individual_on_round, 1)
    else:
        best_allocation = None
    return best_allocation


def should_finish(population, best_allocation, greater_path, configs):
    if population[0].fitness <= greater_path and not population[0].raise_exception():
        return True
    if best_allocation is not None and best_allocation[1] == configs.allocator_params["early_stop"]:
        return True
    # Aqui posso colocar uma condição de parada, por exemplo se estou na 20º geração e o best aallocation ainda é None
    # é sinal de problema, isso impediria o algoritmo de rodar ate a ultima geração só pra ver se tem algo errado
    return False


def get_greater_path(tasks_per_deepness, all_planjobs):
    times = []
    for root in tasks_per_deepness.get(0):
        times.append(calc_task_time(root, all_planjobs))
    return max(times)


def calc_task_time(task, all_planjobs):
    if len(task.successors) == 0:
        return task.time

    times = []
    for successor_id in task.successors:
        successor = get_task_by_id(successor_id, all_planjobs)
        times.append(calc_task_time(successor, all_planjobs))
    return max(times) + task.time


def get_tasks_per_deepness(planjobs):
    set_task_deepness(planjobs)
    tasks_per_deepness = {}

    for task in planjobs:
        tasks_per_deepness[task.deepness] = tasks_per_deepness.get(task.deepness, [])
        tasks_per_deepness[task.deepness].append(task)

    return tasks_per_deepness


def set_task_deepness(planjobs):
    roots = [task for task in planjobs if len(task.predecessors) == 0]
    for root in roots:
        root.deepness = 0
        for successor_id in root.successors:
            successor = get_task_by_id(successor_id, planjobs)
            set_deepness(successor, root.deepness, planjobs)


def set_deepness(task, parent_deepness, all_planjobs):
    current_deepness = parent_deepness + 1
    task.deepness = current_deepness if current_deepness > task.deepness else task.deepness

    if len(task.successors) == 0 or current_deepness < task.deepness:
        return

    for successor_id in task.successors:
        successor = get_task_by_id(successor_id, all_planjobs)
        set_deepness(successor, task.deepness, all_planjobs)


def get_task_by_id(id, tasks):
    for task in tasks:
        if task.id == id:
            return task


def build_response(best_allocation, best_individual_on_round):
    if best_allocation is not None and not best_individual_on_round.raise_exception():
        if best_allocation[0].fitness <= best_individual_on_round.fitness:
            return format_planjobs(best_allocation[0].tasks)
        else:
            return format_planjobs(best_individual_on_round.tasks)

    elif best_allocation is None and not best_individual_on_round.raise_exception():
        return format_planjobs(best_individual_on_round.tasks)

    elif best_allocation is not None and best_individual_on_round.raise_exception():
        return format_planjobs(best_allocation[0].tasks)

    else:
        exception = best_individual_on_round.exception
        raise exception['cause'](exception['value'])


def format_planjobs(planjobs):
    planjobs_response = []
    for planjob in planjobs:
        planjob_response = Planjob(planjob.time, planjob.id)
        planjob_response.allocated_resources_id = [resource.id for resource in planjob.allocated_resources]
        planjob_response.execution_slots = planjob.execution_slots
        planjobs_response.append(planjob_response)
    return planjobs_response
