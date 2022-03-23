class Reel:
    def __init__(self):
        self.option_id = None
        self.percent_loss = {}
        self.feedstock_id = ""
        self.comercial_id = -1
        self.version = 0

class Ink:
    def __init__(self):
        self.feedstock_id = ""
        self.option_id = None
        self.quantity_spent = 0
        self.version = 0

class PrintingCost:
    def __init__(self):
        self.ink_cost = 0.0
        self.time_spent = 0
        self.ink_quantity = 0.0
        self.inks_quantities = []
        self.printing_area = 0.0
        self.bins_area = 0.0
        self.total_loss = 0.0
        self.percent_loss = 0.0
        self.machine_public_id = -1
        self.printing_profile_index = 0
        self.used_reels = []
        self.allocation_map = {}
        self.amendment_list = {}
        self.machine_info = {}
        self.obj = []

    def __getitem__(self, key):
        return getattr(self, key)

