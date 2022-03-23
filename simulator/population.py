#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import math
import random
import sys
import threading

from simulator.chromossome import Chromossome

from simulator.crossover_operation import CrossoverOperation


class Population:
    def __init__(self,
                 items,
                 machines,
                 constraints,
                 genetic_configuration,
                 amendment_dict):
        self.genetic_configurations = genetic_configuration
        self.constraints = constraints
        self.machines = machines
        self.items = items
        self.amendment_dict = amendment_dict
        self.population=[]
        self.thread_pool = []
        self.generation = []
        self.stablement = 0
        print(not self.population, file=sys.stderr)
        #generate first population
        for i in range(self.genetic_configurations["population"]):
            machine = random.choice(machines)
            self.population.append(Chromossome(items, machine["bins"],
                                               constraints["minimum_cut"], machine["margins"],
                                               machine["reel_costs"], machine["reel_suppliers"],
                                               constraints["same_supplier"], machine,
                                               constraints["horizontal_cut"], constraints["vertical_cut"],
                                               self.amendment_dict, machine["inks"]))

    def evolve(self):
        for i in range(self.genetic_configurations["generations"]):
            #evaluate
            for individual in self.population:
                t1 = threading.Thread(target=individual.evaluate, args=(self.constraints["reuse_bins"], self.constraints["use_feedstock"], ))
                t1.start()
                self.thread_pool.append(t1)
            thread_pool_size = len(self.thread_pool)
            for k in range(thread_pool_size, 0, -1):
                self.thread_pool[k-1].join()
                del self.thread_pool[k-1]

            self.population = sorted(self.population, key=lambda x: x.fitness)
            self.generation.append(list(self.population))
            if i>0:
                if self.generation[i-1][0].fitness == self.generation[i][0].fitness:
                    self.stablement = self.stablement + 1
                else:
                    self.stablement = 0
            if self.stablement >= self.genetic_configurations["max_stablement"]:
                break
            print('R$ '+str(self.population[0].fitness))
            if i+1 in range(self.genetic_configurations["generations"]):
                # select the first 1/3 from the population
                max_id = math.floor(self.genetic_configurations["population"]/3)
                for j in self.population[int(max_id):int(self.genetic_configurations["population"])]:
                    self.population.remove(j)
                for k in range(int(max_id),self.genetic_configurations["population"]):
                    rand_value = random.randint(1,3)
                    if rand_value >= 2:
                        elit = random.choice(self.population)
                        t1 = CrossoverOperation(elit, 100 + self.stablement)
                        t1.start()
                        self.thread_pool.append(t1)
                    else:
                        machine = random.choice(self.machines)
                        self.population.append(
                            Chromossome(self.items, machine["bins"], self.constraints["minimum_cut"], machine["margins"],
                                        machine["reel_costs"], machine["reel_suppliers"],
                                        self.constraints["same_supplier"], machine, self.constraints["horizontal_cut"],
                                        self.constraints["vertical_cut"], self.amendment_dict, machine["inks"]))
                thread_pool_size = len(self.thread_pool)
                for k in range(thread_pool_size-1, 0, -1):
                    self.thread_pool[k].join()
                    if isinstance(self.thread_pool[k],CrossoverOperation):
                        self.thread_pool[k].children.mutation(self.stablement)
                        self.population.append(self.thread_pool[k].children)
                        del self.thread_pool[k]
