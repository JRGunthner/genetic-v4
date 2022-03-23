import copy
import sys

from simulator.population import Population
from utils.dictionary import get_dict_value_by_index


class HoldSimulator:

    def __init__(self, elements, machines, constraints, genetic_configurations, media_remains):
        self.apply_media_remains_to_elements(media_remains, elements)
        self.elements = [tuple(x) for x in elements]
        self.machines = copy.deepcopy(machines)
        self.constraints = constraints
        self.genetic_configurations = genetic_configurations

    def simulate(self):
        elements_to_simulate = []

        # constraints treatment
        for machine in self.machines:
            for reel_midia in machine["bins"]:
                reel_midia[0] = reel_midia[0] - (machine["margins"]["right"] + machine["margins"]["left"])
                reel_midia[1] = reel_midia[1] - (machine["margins"]["top"] + machine["margins"]["bottom"])

            if self.constraints["infinite_height"]:
                machine["bins"] = [(x[0], sys.float_info.max, x[2], x[3], x[4], x[5], x[6], x[7]) for x in machine["bins"]]

            reel_costs = {}
            reel_suppliers = {}
            # reel_suppliers = {(width, height) = [option_id, comercial_index, feedstock_id, version]}

            for reel in machine["bins"]:
                reel_costs[tuple((reel[0], reel[1], reel[3]))] = reel[2]

                if self.constraints["same_supplier"]:
                    reel_suppliers[tuple((reel[0], reel[1]))] = [[reel[3]], reel[4], reel[5], reel[6], reel[7]] if tuple((reel[0], reel[1])) not in reel_suppliers \
                        else reel_suppliers[tuple((reel[0], reel[1]))] + [reel[3]]
                else:
                    tuples = [t for t in reel_costs.keys() if t[0] == reel[0] and t[1] == reel[1] and reel_costs[t] > reel[2]]
                    if tuples or tuple((reel[0], reel[1])) not in reel_suppliers.keys():
                        reel_suppliers[tuple((reel[0], reel[1]))] = [[reel[3]], reel[4], reel[5], reel[6], reel[7]]

            machine["bins"] = [tuple((x[0], x[1])) for x in machine["bins"]]
            machine["reel_costs"] = reel_costs
            machine["reel_suppliers"] = reel_suppliers

        amendment_dict = {}

        for element in self.elements:
            counter = 1
            for new_element in range(element[3]):
                elements_to_simulate.append((element[0], element[1], element[2] + " Item: "+str(counter)))
                amendment_dict[element[2] + " Item: "+str(counter)] = {
                    "size": element[4],
                    "vertical_amendment": element[5],
                    "horizontal_amendment": element[6]
                }
                counter = counter + 1

        population = Population(list(elements_to_simulate),
                                self.machines, self.constraints,
                                self.genetic_configurations, amendment_dict)
        population.evolve()
        return population.population

    def apply_media_remains_to_elements(self, media_remains, elements):
        measure_index = 0
        measure_length_index = 0
        measure_width_index = 1
        measure_description_index = 3

        element_width_index = 0
        element_length_index = 1
        element_description_index = 2

        media_remains_superior_index = 2
        media_remains_bottom_index = 3
        media_remains_left_index = 4
        media_remains_right_index = 5

        for element in elements:
            element_length = element[element_length_index]
            element_width = element[element_width_index]
            element_description = element[element_description_index]

            for media_remain in media_remains:
                measure = get_dict_value_by_index(media_remain, measure_index)
                measure_length = get_dict_value_by_index(measure, measure_length_index)
                measure_width = get_dict_value_by_index(measure, measure_width_index)
                measure_description = get_dict_value_by_index(measure, measure_description_index)

                if element_length == measure_length and \
                        element_width == measure_width and \
                        element_description == measure_description:

                    media_remain_left = get_dict_value_by_index(media_remain, media_remains_left_index)
                    media_remain_right = get_dict_value_by_index(media_remain, media_remains_right_index)
                    media_remain_superior = get_dict_value_by_index(media_remain, media_remains_superior_index)
                    media_remain_bottom = get_dict_value_by_index(media_remain, media_remains_bottom_index)

                    element[element_width_index] += (media_remain_left + media_remain_right)
                    element[element_length_index] += (media_remain_superior + media_remain_bottom)
