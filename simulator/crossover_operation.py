import random
from threading import Thread

from simulator.chromossome import Chromossome


class CrossoverOperation(Thread):
    children = None

    def __init__(self, chromossome_leading, chromossome_number):
        self.chromossome_leading = chromossome_leading
        self.chromossome_number = chromossome_number
        super(CrossoverOperation, self).__init__()

    def run(self):
        children = Chromossome(self.chromossome_leading.rect_list, self.chromossome_leading.bins_list,
                               self.chromossome_leading.minimum_cut, self.chromossome_leading.bins_margins,
                               self.chromossome_leading.reel_costs, self.chromossome_leading.reel_suppliers,
                               self.chromossome_leading.same_supplier, self.chromossome_leading.machine_info,
                               self.chromossome_leading.horizontal_cut, self.chromossome_leading.vertical_cut,
                               self.chromossome_leading.amendment_dict, self.chromossome_leading.inks_list,
                               self.chromossome_leading.amendment_list)
        # pack_algorithm random between parents
        children.pack_algorithm = self.chromossome_leading.pack_algorithm
        # sort_algorithm random between parets
        children.sort_algorithm = self.chromossome_leading.sort_algorithm
        children.cutting_number = self.chromossome_leading.cutting_number
        # crossover rectangle list n times
        for i in range(self.chromossome_number):
            index1 = random.randint(0, len(self.chromossome_leading.rect_list) - 1)
            index2 = random.randint(0, len(self.chromossome_leading.rect_list) - 1)
            tmp_list = children.rect_list
            aux_value = tmp_list[index1]
            tmp_list[index1] = tmp_list[index2]
            tmp_list[index2] = aux_value
            children.rect_list = tmp_list
        # crossover bins list n times
        for i in range(self.chromossome_number):
            index1 = random.randint(0, len(self.chromossome_leading.bins_list) - 1)
            index2 = random.randint(0, len(self.chromossome_leading.bins_list) - 1)
            tmp_list = children.bins_list
            aux_value = tmp_list[index1]
            tmp_list[index1] = tmp_list[index2]
            tmp_list[index2] = aux_value
            children.bins_list = tmp_list
        self.children = children
