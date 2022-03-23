import copy
import random

from rectpack import GuillotineBafMaxas, SkylineBl, MaxRectsBaf, MaxRectsBl, MaxRectsBssf, MaxRectsBlsf, SkylineBlWm, \
    SkylineMwf, SkylineMwfl, SkylineMwflWm, GuillotineBssfSas, GuillotineBssfLas, GuillotineBssfSlas, \
    GuillotineBssfLlas, GuillotineBssfMaxas, GuillotineBssfMinas, GuillotineBlsfSas, GuillotineBlsfLas, \
    GuillotineBlsfSlas, GuillotineBlsfLlas, GuillotineBlsfMaxas, GuillotineBlsfMinas, GuillotineBafSas, \
    GuillotineBafLas, GuillotineBafSlas, GuillotineBafLlas, GuillotineBafMinas
from rectpack import SORT_NONE, SORT_AREA, SORT_PERI, SORT_DIFF, SORT_SSIDE, SORT_LSIDE, SORT_RATIO, newPacker
from simulator.shelf_algorithm import Shelf
from pint import UnitRegistry

ur = UnitRegistry()
Q_ = ur.Quantity


class Chromossome:
    def __init__(self, rect_list,
                 bins_list, minimum_cut,
                 bins_margins, reel_costs,
                 reel_suppliers, same_supplier,
                 machine_info, horizontal_cut,
                 vertical_cut, amendment_dict,
                 inks_list,
                 amendment_list={}):
        self.evaluate_result = None
        self.fitness = float("inf")
        self.retangle_area = None
        self.allocation_map = {}
        self.max_y = {}
        self.bins_area = 0.0
        self.print_height = 0
        self.print_time = 0.0
        self.print_time_cost = 0.0
        self.percent = 0
        self.suppliers = []
        self.rect_list = list(rect_list)
        self.bins_list = list(bins_list)
        self.inks_list = list(inks_list)
        self.bins_margins = bins_margins
        self.minimum_cut = minimum_cut
        self.reel_costs = reel_costs
        self.same_supplier = same_supplier
        self.machine_info = machine_info
        self.reel_suppliers = reel_suppliers
        self.vertical_cut = vertical_cut
        self.horizontal_cut = horizontal_cut
        self.amendment_dict = amendment_dict
        self.amendment_list = copy.deepcopy(amendment_list)
        self.used_bins = 0
        self.cutting_number = 0
        self.bin_cost = 0
        self.ink_cost = 0.0
        self.ink_quantity = 0.0
        self.inks_quantities = []
        self.total_loss = 0.0
        self.used_reels = []
        random.shuffle(rect_list)
        random.shuffle(bins_list)
        self.pack_algorithm = random.choice([GuillotineBafMaxas, GuillotineBssfSas, GuillotineBssfLas, GuillotineBssfSlas,
                                             GuillotineBssfLlas, GuillotineBssfMaxas, GuillotineBssfMinas,
                                             GuillotineBlsfSas, GuillotineBlsfLas, GuillotineBlsfSlas,
                                             GuillotineBlsfLlas, GuillotineBlsfMaxas, GuillotineBlsfMinas,
                                             GuillotineBafSas, GuillotineBafLas, GuillotineBafSlas, GuillotineBafLlas,
                                             GuillotineBafMinas])
        self.sort_algorithm = random.choice([SORT_NONE])

    def evaluate(self, reuse_bins, use_feedstock):
        # Evaluate if it's none, because itsn't already evaluated
        if self.evaluate_result is None:
            packer = newPacker(pack_algo=self.pack_algorithm,
                               sort_algo=self.sort_algorithm)
            # Add the rectangles
            for r in self.rect_list:
                packer.add_rect(*r)

            # Add the bins where the rectangles will be placed
            for b in self.bins_list:
                b += (float("inf"),)
                packer.add_bin(*b)

            # Start packing
            packer.pack()
            self.evaluate_result = packer
            self.cutting_rectangles_process()
            if self.evaluate_result is not None and self.fitness is not float("inf"):
                if self.machine_info["inset_reels"]:
                    reel_packer = newPacker(rotation=False)
                    reel_packer.add_bin(self.machine_info["openess"], float("inf"))
                else:
                    itens = []
                self.used_bins = len(packer)
                bins_area = 0
                sum_cost = 0
                self.retangle_area = 0
                self.suppliers = []
                for i in range(self.used_bins):
                    abin = packer[i]
                    used_rectangles = len(abin)
                    width, height = abin.width, abin.height
                    maxY = None
                    for j in range(used_rectangles):
                        x = abin[j].x
                        y = abin[j].y
                        w = abin[j].width
                        h = abin[j].height
                        rid = abin[j].rid
                        if maxY is None:
                            maxY = y + h
                        elif maxY < y + h:
                            maxY = y + h
                        # TODO: subtrair margens
                        self.retangle_area = self.retangle_area + (w*h)
                    self.max_y[i] = maxY
                    if self.machine_info["inset_reels"]:
                        reel_packer.add_rect(width, maxY, i)
                    else:
                        itens.append((width, maxY, i))
                    possibilities = self.reel_suppliers[tuple((width, height))][0]
                    if self.same_supplier:
                        if i>0:
                            possibilities = list(set(possibilities).intersection([self.suppliers[i-1]]))
                    if not possibilities:
                        self.evaluate_result = None
                        sum_cost = float("inf")
                        break
                    self.suppliers.append(random.choice(possibilities))
                    if reuse_bins and use_feedstock:
                        bin_area = self.calc_area(width, maxY, self.bins_margins)
                        bins_area = bins_area + bin_area
                        sum_cost = sum_cost + self.calc_cost(
                            self.reel_costs[tuple((width, height, self.suppliers[i]))],
                            self.reel_suppliers[tuple((width, height))][4],
                            bin_area)

                        bin_area_atual = ((width + self.bins_margins["right"] + self.bins_margins["left"]) * maxY)
                        retangle_area_atual = 0
                        for retangle in packer._open_bins[i].rectangles:
                            retangle_area_atual = retangle_area_atual + (retangle.width * retangle.height)
                        percent_loss = ((bin_area_atual - retangle_area_atual)/bin_area_atual) * 100
                        # option_id, percent_loss, comercial_index, version
                        used_reel = [self.suppliers[i], percent_loss, self.reel_suppliers[tuple((width, height))][1], self.reel_suppliers[tuple((width, height))][2], self.reel_suppliers[tuple((width, height))][3]]
                        self.used_reels.append(used_reel)
                    elif (not use_feedstock):
                        bins_area = 0.0
                        sum_cost = 0
                        self.used_reels = []
                    else:
                        bin_area = self.calc_area(width, height, self.bins_margins)
                        bins_area = bins_area + bin_area
                        sum_cost = sum_cost + self.calc_cost(
                            self.reel_costs[tuple((width, height, self.suppliers[i]))],
                            self.reel_suppliers[tuple((width, height))][4],
                            bin_area)

                        retangle_area_atual = 0
                        for retangle in packer._open_bins[i].rectangles:
                            retangle_area_atual = retangle_area_atual + (retangle.width * retangle.height)

                        percent_loss = ((bin_area - retangle_area_atual)/bin_area) * 100
                        # option_id, percent_loss, comercial_index, version
                        used_reel = [self.suppliers[i], percent_loss,  self.reel_suppliers[tuple((width, height))][1], self.reel_suppliers[tuple((width, height))][2], self.reel_suppliers[tuple((width, height))][3]]
                        self.used_reels.append(used_reel)

                if self.machine_info["inset_reels"]:
                    self.calc_time(reel_packer=reel_packer)
                else:
                    self.calc_time(itens=itens)

                if len(self.allocation_map) > 0:
                    self.calc_ink_consume()
                    self.fitness = sum_cost + self.print_time_cost + self.ink_cost
                    self.bins_area = bins_area
                    self.bin_cost = sum_cost
                    self.total_loss = self.bins_area - self.retangle_area

    def calc_area(self, width, height, bin_margins):
        return ((width + bin_margins["right"] + bin_margins["left"]) * (height + bin_margins["top"] + bin_margins["bottom"]))

    def calc_cost(self, feedstock_price, feedstock_measurement_unit, bin_area):
        converted_area = Q_(str(bin_area) + 'mm**2').to(feedstock_measurement_unit).magnitude
        return feedstock_price * converted_area

    def calc_ink_consume(self):
        # ink = [feedstock_id, price, consume in ml/m*m, option_id , version]
        for ink in self.inks_list:
            actual_ink_quantity = (ink[2]/1000000) * self.retangle_area
            actual_ink_cost = actual_ink_quantity * ink[1]
            self.inks_quantities.append([ink[0], ink[3], actual_ink_quantity, ink[4]])
            self.ink_quantity += actual_ink_quantity
            self.ink_cost += actual_ink_cost

    def calc_time(self, reel_packer = {}, itens = []):
        if self.machine_info["inset_reels"]:
            reel_packer.pack()
        else:
            shelf_algorithm = Shelf(self.machine_info["openess"], itens, self.machine_info["space_between_reels"],
                                    self.machine_info["max_parallel_reels"])
            allocation_map = shelf_algorithm.alocate()

            if len(allocation_map) > 1:
                self.allocation_map = allocation_map
                if self.machine_info["calc_type"] == "openess_calc":
                    self.print_height = self.machine_info["openess"] * max(allocation_map.keys())
                    self.print_time = (self.print_height / self.machine_info["produtivity"]) \
                                      +((len(allocation_map.keys())-1) * self.machine_info["RIP_time"])
                    if self.evaluate_result:
                        self.print_time += (len(self.evaluate_result) * self.machine_info["init_time"])
                    self.print_time_cost = self.print_time * self.machine_info["time_cost"]
                elif self.machine_info["calc_type"] == "print_area_calc":
                    for height in self.allocation_map:
                        ordered_allocation_map = sorted(self.allocation_map[height], key=lambda x: x[3], reverse=True)
                        left_x = None
                        right_x = None
                        last_index = None
                        for index in range(1, len(ordered_allocation_map)):
                            last_index = index
                            maior = {
                                "x1": (ordered_allocation_map[index - 1][0], ordered_allocation_map[index - 1][1]),
                                "x2": (ordered_allocation_map[index - 1][0] + ordered_allocation_map[index - 1][2],
                                       ordered_allocation_map[index - 1][1])
                            }
                            menor = {
                                "x1": (ordered_allocation_map[index][0], ordered_allocation_map[index][1]),
                                "x1": (ordered_allocation_map[index][0], ordered_allocation_map[index][1]),
                                "x2": (
                                    ordered_allocation_map[index][0] + ordered_allocation_map[index][2],
                                    ordered_allocation_map[index][1])
                            }
                            if not left_x and not right_x:
                                self.print_time = self.print_time + (ordered_allocation_map[index - 1][3] - ordered_allocation_map[index][3]) * \
                                              ordered_allocation_map[index - 1][2] / (self.machine_info["produtivity"] * (1 - (
                                (self.machine_info["openess"] - ordered_allocation_map[index - 1][2]) / self.machine_info["openess"]) * self.machine_info["reduction_percent"] / 100))
                            else:
                                self.print_time = self.print_time + (ordered_allocation_map[index - 1][3] - ordered_allocation_map[index][3]) * \
                                              (right_x - left_x) / (self.machine_info["produtivity"] * (
                                1 - ((self.machine_info["openess"] - (right_x - left_x)) / self.machine_info["openess"]) * self.machine_info["reduction_percent"] / 100))
                            if not left_x:
                                left_x = maior["x1"][0]
                            if not right_x:
                                right_x = maior["x2"][0]
                            if left_x > maior["x1"][0]:
                                left_x = maior["x1"][0]
                            if left_x > menor["x1"][0]:
                                left_x = menor["x1"][0]
                            if right_x < maior["x2"][0]:
                                right_x = maior["x2"][0]
                            if right_x < menor["x2"][0]:
                                right_x = maior["x2"][0]
                        if not left_x and not right_x and len(ordered_allocation_map) > 0:
                            self.print_time = self.print_time + ordered_allocation_map[0][3] * \
                                          ordered_allocation_map[0][2] / (self.machine_info["produtivity"] * (
                            1 - (
                                (self.machine_info["openess"] - ordered_allocation_map[0][2]) /
                                self.machine_info["openess"]) * self.machine_info["reduction_percent"] / 100
                            ))
                        elif len(ordered_allocation_map) > 0:
                            self.print_time = self.print_time + ordered_allocation_map[last_index][3] * \
                                          (right_x - left_x) / (self.machine_info["produtivity"] * (
                            1 - ((self.machine_info["openess"] - (right_x - left_x)) / self.machine_info["openess"]) * self.machine_info["reduction_percent"] / 100))
                    self.print_time = self.print_time +((len(allocation_map.keys())-1) * self.machine_info["RIP_time"])
                    if self.evaluate_result:
                        self.print_time += (len(self.evaluate_result) * self.machine_info["init_time"])
                    self.print_time_cost = self.print_time * self.machine_info["time_cost"]

    def cutting_rectangles_process(self):
        if len(self.rect_list) != len(self.evaluate_result.rect_list()):
            oversize_elements = []
            for i in self.rect_list:
                has_found = False
                for j in self.evaluate_result.rect_list():
                    if has_found:
                        break
                    if i[2] == j[5]:
                        has_found = True
                if not has_found:
                    oversize_elements.append(i)

            new_elements = []
            selected_oversize_axis = -1
            selected_bin = None
            selected_bin_axis = -1
            for i in range(len(oversize_elements), 0, -1):
                oversize_axis_set = []
                if self.horizontal_cut:
                    oversize_axis_set.append(1)
                if self.vertical_cut:
                    oversize_axis_set.append(0)
                selected_oversize_axis = random.choice(oversize_axis_set)
                selected_bin = sorted(self.bins_list, key=lambda tup: tup[0], reverse=True)[0]
                selected_bin_axis = random.choice([0, 1])
                if oversize_elements[i-1][selected_oversize_axis] < selected_bin[selected_bin_axis]:
                    continue
                else:
                    still_size = oversize_elements[i-1][selected_oversize_axis]
                    if selected_oversize_axis == 0:
                        selected_str = 'V'
                    else:
                        selected_str = 'H'
                    count = 1
                    while still_size > selected_bin[selected_bin_axis]:
                        self.cutting_number = self.cutting_number + 1
                        still_size = still_size - selected_bin[selected_bin_axis] + self.amendment_dict[oversize_elements[i-1][2]]["size"]
                        new_size = selected_bin[selected_bin_axis]
                        if still_size<self.minimum_cut:
                            new_size = new_size - (self.minimum_cut - still_size)
                            still_size = still_size + (self.minimum_cut - still_size)
                        if selected_oversize_axis == 0:
                            # Cria tupla (<novo valor>, <valor antigo>)
                            self.amendment_dict[oversize_elements[i-1][2]+"|"+selected_str+str(count)] = {
                                "size": self.amendment_dict[oversize_elements[i-1][2]]["size"],
                                "vertical_amendment": self.amendment_dict[oversize_elements[i-1][2]]["vertical_amendment"],
                                "horizontal_amendment": self.amendment_dict[oversize_elements[i-1][2]]["horizontal_amendment"]
                            }
                            new_id = oversize_elements[i-1][2]+"|"+selected_str+str(count)
                            self.amendment_list[new_id] = \
                                self.create_amendment('vertical',
                                                      self.amendment_dict[oversize_elements[i-1][2]]["vertical_amendment"],
                                                      oversize_elements[i - 1][1],
                                                      new_size,
                                                      first_one=(count==1),
                                                      last_one=(still_size==0),
                                                      old_amendment_element=self.amendment_list[oversize_elements[i-1][2]]
                                                      if oversize_elements[i-1][2] in self.amendment_list else {})

                            if (still_size == 0) and oversize_elements[i - 1][2] in self.amendment_list:
                                del self.amendment_list[oversize_elements[i - 1][2]]

                            new_elements.append((new_size, oversize_elements[i-1][1], oversize_elements[i-1][2]+"|"+selected_str+str(count)))

                        else:
                            self.amendment_dict[oversize_elements[i - 1][2] + "|" + selected_str + str(count)] = {
                                "size": self.amendment_dict[oversize_elements[i - 1][2]]["size"],
                                "vertical_amendment": self.amendment_dict[oversize_elements[i - 1][2]][
                                    "vertical_amendment"],
                                "horizontal_amendment": self.amendment_dict[oversize_elements[i - 1][2]][
                                    "horizontal_amendment"]
                            }

                            new_id = oversize_elements[i-1][2]+"|"+selected_str+str(count)
                            self.amendment_list[new_id] =\
                                self.create_amendment('horizontal',
                                                  self.amendment_dict[oversize_elements[i - 1][2]][
                                                      "horizontal_amendment"],
                                                  new_size,
                                                  oversize_elements[i - 1][0],
                                                  first_one=(count == 1),
                                                  last_one=(still_size == 0),
                                                  old_amendment_element=self.amendment_list[
                                                          oversize_elements[i - 1][2]]
                                                      if oversize_elements[i - 1][2] in self.amendment_list else {}
                                                      )
                            if (still_size == 0) and oversize_elements[i - 1][2] in self.amendment_list:
                                del self.amendment_list[oversize_elements[i - 1][2]]

                            # Cria tupla (<valor antigo>, <valor novo>)
                            new_elements.append((oversize_elements[i-1][0], new_size, oversize_elements[i-1][2]+"|"+selected_str+str(count)))
                        count = count+1
                    if still_size != 0:
                        self.cutting_number = self.cutting_number + 1
                        if (selected_oversize_axis == 0):
                            self.amendment_dict[oversize_elements[i - 1][2] + "|" + selected_str + str(count)] = {
                                "size": self.amendment_dict[oversize_elements[i - 1][2]]["size"],
                                "vertical_amendment": self.amendment_dict[oversize_elements[i - 1][2]][
                                    "vertical_amendment"],
                                "horizontal_amendment": self.amendment_dict[oversize_elements[i - 1][2]][
                                    "horizontal_amendment"]
                            }
                            new_id = oversize_elements[i - 1][2] + "|" + selected_str + str(count)
                            self.amendment_list[new_id] = self.create_amendment('vertical',
                                                  self.amendment_dict[oversize_elements[i - 1][2]][
                                                      "vertical_amendment"],
                                                  oversize_elements[i - 1][1],
                                                  still_size,
                                                  last_one=True,
                                                  old_amendment_element=self.amendment_list[
                                                                         oversize_elements[i - 1][2]]
                                                                        if oversize_elements[i - 1][
                                                                        2] in self.amendment_list else {}
                                                                                )
                            if oversize_elements[i - 1][2] in self.amendment_list:
                                del self.amendment_list[oversize_elements[i - 1][2]]

                            # Cria tupla (<novo valor>, <valor antigo>)
                            new_elements.append((still_size, oversize_elements[i-1][1], oversize_elements[i-1][2]+"|"+selected_str+str(count)))
                        else:
                            self.amendment_dict[oversize_elements[i - 1][2] + "|" + selected_str + str(count)] = {
                                "size": self.amendment_dict[oversize_elements[i - 1][2]]["size"],
                                "vertical_amendment": self.amendment_dict[oversize_elements[i - 1][2]][
                                    "vertical_amendment"],
                                "horizontal_amendment": self.amendment_dict[oversize_elements[i - 1][2]][
                                    "horizontal_amendment"]
                            }

                            new_id = oversize_elements[i - 1][2] + "|" + selected_str + str(count)
                            self.amendment_list[new_id] = self.create_amendment('horizontal',
                                                  self.amendment_dict[oversize_elements[i - 1][2]][
                                                      "horizontal_amendment"],
                                                  still_size,
                                                  oversize_elements[i - 1][0],
                                                  last_one=True,
                                                  old_amendment_element=self.amendment_list[
                                                      oversize_elements[i - 1][2]]
                                                  if oversize_elements[i - 1][2] in self.amendment_list else {}
                                                  )
                            if oversize_elements[i - 1][2] in self.amendment_list:
                                del self.amendment_list[oversize_elements[i - 1][2]]

                            # Cria tupla (<valor antigo>, <valor novo>)
                            new_elements.append((oversize_elements[i-1][0], still_size, oversize_elements[i-1][2]+"|"+selected_str+str(count)))
                    still_size = 0
                    self.rect_list.remove(oversize_elements[i-1])
            self.rect_list.extend(new_elements)
            self.evaluate_result = None
            self.fitness = float("inf")

    def create_amendment(self, type, amendment_side,
                         vertical_size, horizontal_size,
                         first_one=False, last_one=False,
                         old_amendment_element={}):
        new_element_emendment = {}
        if type == 'vertical':
            # lidando com emendas verticais
            if amendment_side == 'right':
                if not first_one:
                    # Se a emenda fica no elemento a direita, ficara a esquerda desse elemento
                    new_element_emendment[3] = vertical_size
            else:
                if not last_one:
                    new_element_emendment[1] = vertical_size
            if 0 in old_amendment_element:
                new_element_emendment[0] = horizontal_size
            if 2 in old_amendment_element:
                new_element_emendment[2] = horizontal_size
        else:
            # lidando com emendas horizontais
            if amendment_side == 'bottom':
                if not first_one:
                    # Se a emenda fica no elemento abaixo, ficara acima desse elemento
                    new_element_emendment[2] = horizontal_size
            else:
                if not last_one:
                    # Se a emenda fica no elemento acima, ficara abaixo desse elemento
                    new_element_emendment[0] = horizontal_size
            if 1 in old_amendment_element:
                new_element_emendment[1] = vertical_size
            if 3 in old_amendment_element:
                new_element_emendment[3] = vertical_size
        return new_element_emendment

    def mutation(self, stablement):
        pack_mutation = random.randint(0, 100)
        if pack_mutation <= 2 * (stablement + 1):
            self.pack_algorithm = random.choice(
                [GuillotineBafMaxas, SkylineBl, MaxRectsBaf, MaxRectsBl, MaxRectsBssf, MaxRectsBlsf, SkylineBlWm,
                 SkylineMwf, SkylineMwfl, SkylineMwfl, SkylineMwflWm, GuillotineBssfSas, GuillotineBssfLas,
                 GuillotineBssfSlas, GuillotineBssfLlas, GuillotineBssfMaxas, GuillotineBssfMinas, GuillotineBlsfSas,
                 GuillotineBlsfLas, GuillotineBlsfSlas, GuillotineBlsfLlas, GuillotineBlsfMaxas, GuillotineBlsfMinas,
                 GuillotineBafSas, GuillotineBafLas, GuillotineBafSlas, GuillotineBafLlas, GuillotineBafMinas])
            self.evaluate_result = None
        algorithm_mutation = random.randint(0, 100)
        if algorithm_mutation <= 2 * (stablement + 1):
            self.sort_algorithm = random.choice(
                [SORT_NONE, SORT_AREA, SORT_PERI, SORT_DIFF, SORT_SSIDE, SORT_LSIDE, SORT_RATIO])
            self.evaluate_result = None
        rotation_mutation = random.randint(0, 100)
        if rotation_mutation <= 20 * (stablement + 1):
            choosen_item = random.choice(self.rect_list)
            new_item = (choosen_item[1], choosen_item[0], choosen_item[2])
            self.rect_list.remove(choosen_item)
            self.rect_list.append(new_item)
            self.evaluate_result = None
