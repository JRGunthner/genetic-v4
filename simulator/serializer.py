import time


class Serializer:
    def __init__(self, chromossome, reuse_bin, margins):
        self.return_obj = []
        self.fitness = chromossome.fitness
        self.amendment_list = chromossome.amendment_list
        self.amendment_dict = chromossome.amendment_dict
        self.print_time = chromossome.print_time
        self.bins_area = chromossome.bins_area
        self.retangle_area = chromossome.retangle_area
        self.allocation_map = chromossome.allocation_map
        self.print_time_cost = chromossome.print_time_cost
        self.suppliers = chromossome.suppliers
        self.packer = chromossome.evaluate_result
        self.bin_cost = chromossome.bin_cost
        self.ink_cost = chromossome.ink_cost
        self.ink_quantity = chromossome.ink_quantity
        self.inks_quantities = chromossome.inks_quantities
        self.total_loss = chromossome.total_loss
        self.machine_info = chromossome.machine_info
        self.used_reels = chromossome.used_reels
        if self.packer:
            used_bins = len(self.packer)
        else:
            used_bins = 0
        for i in range(used_bins):
            abin_obj = {}
            abin = self.packer[i]
            used_rectangles = len(abin)
            width, height = abin.width, abin.height
            abin_obj["width"] = width + margins["left"] + margins["right"]
            abin_obj["height"] = height
            abin_obj["items"] = []
            maxY = -1
            for j in range(used_rectangles):
                item = {}
                x = abin[j].x
                y = abin[j].y
                w = abin[j].width
                h = abin[j].height
                rid = abin[j].rid
                item["x"] = x
                item["y"] = y
                item["width"] = w
                item["height"] = h
                item["id"] = rid
                abin_obj["items"].append(item)
                if maxY < y + h:
                    maxY = y + h
            if reuse_bin:
                abin_obj["height"] = maxY + margins["top"] + margins["bottom"]
            self.return_obj.append(abin_obj)

    def mount_machine_information(self):
        info = {}
        info["margins"] = self.machine_info["margins"]
        info["openess"] = self.machine_info["openess"]
        info["machine_public_id"] = self.machine_info["machine_public_id"]
        info["printing_profile_index"] = self.machine_info["printing_profile_index"]
        info["version"] = self.machine_info["version"]
        return info

    def calc_percent(self):
        percent = 0

        if self.retangle_area and self.bins_area:
            percent = ((self.bins_area - self.retangle_area) / self.bins_area) * 100

        return percent

    def calc_amendment_area(self):
        if not self.amendment_list:
            return 0

        amendment_area = 0
        amendment_top = 0
        amendment_right = 1
        amendment_bottom = 2
        amendment_left = 3

        for abin_index in range(len(self.return_obj)):
            abin_obj = self.return_obj[abin_index]
            for item_index in range(len(abin_obj["items"])):
                item = abin_obj["items"][item_index]
                item_id = item["id"]
                item_width = item["width"]
                item_height = item["height"]

                if item_id in self.amendment_list and item_id in self.amendment_dict:
                    amendments = self.amendment_list[item_id]
                    amendment_size = self.amendment_dict[item_id]["size"]

                    if amendment_top in amendments:
                        amendment_area = amendment_area + (amendment_size * item_width)

                    if amendment_right in amendments:
                        amendment_area = amendment_area + (amendment_size * item_height)

                    if amendment_bottom in amendments:
                        amendment_area = amendment_area + (amendment_size * item_width)

                    if amendment_left in amendments:
                        amendment_area = amendment_area + (amendment_size * item_height)

        return amendment_area

    def calc_retangle_area(self):
        retangle_area = 0

        if self.retangle_area:
            amendment_area = self.calc_amendment_area()
            retangle_area = self.retangle_area - amendment_area

        return retangle_area

    def get_returned_obj(self):
        retangle_area = self.calc_retangle_area()

        return {
            "time": time.time(),
            "fitness": "R$ "+str(self.fitness),
            "amendment_list": self.amendment_list,
            "bins_area": self.bins_area / 1000000,
            "print_time_cost": self.print_time_cost,
            "allocation_map": self.allocation_map,
            "print_time": self.print_time,
            "suppliers": self.suppliers,
            "percent": self.calc_percent(),
            "obj": self.return_obj,
            "bin_cost": self.bin_cost,
            "ink_cost": self.ink_cost,
            "ink_quantity": str(self.ink_quantity) + " ml",
            "inks_quantities": self.inks_quantities,
            "total_loss": self.total_loss / 1000000,
            "retangle_area": retangle_area / 1000000 if retangle_area else 0,
            "machine_info": self.mount_machine_information(),
            "printing_profile_index": self.machine_info["printing_profile_index"],
            "used_reels": self.used_reels
        }
