# coding: utf-8

import random
import sys

from copy import deepcopy
from datetime import datetime

from pcp_scheduler.src.scheduler.scheduler import Scheduler
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourcesException
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException
from pcp_scheduler.src.exceptions.Exceptions import LoadBalancerViolationException


class TasksDeepness():
    def __init__(self, deepness={}, grid=[], configs={}, non_working_days=[]):
        self.deepness = deepness
        self.grid = grid
        self.configs = configs
        self.non_working_days = non_working_days
        self.tasks_deepness = []
        self.fitness = 0
        self.tasks_allocation = []
        self.tasks = []
        self.exception = {}
        for tasks in deepness.values():
            self.tasks.extend(tasks)

        self.randomize_tasks_order()
        self.generate_allocation()

    def randomize_tasks_order(self):
        for deep in sorted(self.deepness.keys()):
            random.shuffle(self.deepness[deep])
            self.tasks_deepness.append(self.deepness[deep])

    def generate_allocation(self):
        scheduler = Scheduler(self.grid, self.tasks, self.configs, self.non_working_days)
        for deepness in range(len(self.tasks_deepness)):
            tasks = self.tasks_deepness[deepness]
            for planjob in tasks:
                try:
                    scheduler.allocate_planjob(planjob)
                except InsufficientResourcesException as e:
                    self.exception["cause"] = InsufficientResourcesException
                    self.exception["value"] = e.value
                    return
                except InsufficientResourceCalendarException as e:
                    self.exception["cause"] = InsufficientResourceCalendarException
                    self.exception["value"] = e.value
                    return
                except LoadBalancerViolationException as e:
                    self.exception["cause"] = LoadBalancerViolationException
                    self.exception["value"] = e.value
                    return

    def calc_fitness(self):
        if self.raise_exception():
            self.fitness = sys.maxsize
        else:
            global_start = datetime.max
            global_finish = datetime.min
            for deepness in range(len(self.tasks_deepness)):
                for task in self.tasks_deepness[deepness]:
                    if task.execution_slots[0].start_time < global_start:
                        global_start = task.execution_slots[0].start_time
                    if task.execution_slots[-1].finish_time > global_finish:
                        global_finish = task.execution_slots[-1].finish_time

            diff = (global_finish - global_start).total_seconds() / 60
            self.fitness = diff

    def crossover(self, grid, configs):
        self.grid = deepcopy(grid)
        self.configs = deepcopy(configs)
        for tasks_in_deepness in self.tasks_deepness:
            self.tasks.extend(tasks_in_deepness)

        for deepness in self.tasks_deepness:
            for task in deepness:
                self.clean_task(task)
        self.generate_allocation()

    def mutation(self, rate, grid, configs):
        muted = False
        for i in range(len(self.tasks_deepness)):
            num = random.randint(0, 100)
            rate = max(5, rate)
            if num <= rate:
                muted = True
                indexes = range(len(self.tasks_deepness[i]))
                if len(indexes) > 1:
                    pos1 = random.choice(indexes)
                    pos2 = random.choice(list(set(indexes).difference([pos1])))
                    temp = self.tasks_deepness[i][pos1]
                    self.tasks_deepness[i][pos1] = self.tasks_deepness[i][pos2]
                    self.tasks_deepness[i][pos2] = temp
        if muted:
            self.grid = deepcopy(grid)
            self.configs = deepcopy(configs)
            for deepness in self.tasks_deepness:
                for task in deepness:
                    self.clean_task(task)

            self.generate_allocation()

    def clean_task(self, task):
        task.execution_slots = []
        task.allocated_resources = None
        task.resources = None
        task.visited = False

    def raise_exception(self):
        return 'cause' in self.exception
