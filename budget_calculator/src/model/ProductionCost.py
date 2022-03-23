class ProductionCost:
    def __init__(self):
        self.feedstock_production_cost = 0.0
        self.labor_production_cost = 0.0
        self.outsourcing_production_cost = 0.0
        self.feedstock_apportionment_value = 0.0
        self.labor_apportionment_value = 0.0
        self.outsourcing_apportionment_value = 0.0

    def __getitem__(self, key):
        return getattr(self, key)

    def sum_production_costs(self):
        return self.feedstock_production_cost + self.labor_production_cost + self.outsourcing_production_cost

    def distribute_apportionment_value(self, value):
        sum = self.sum_production_costs()
        self.feedstock_apportionment_value = (self.feedstock_production_cost / sum) * value
        self.labor_apportionment_value = (self.labor_production_cost / sum) * value
        self.outsourcing_apportionment_value = (self.outsourcing_production_cost / sum) * value

    def sum_total(self):
        return self.sum_production_costs() + self.labor_apportionment_value \
               + self.feedstock_apportionment_value + self.outsourcing_apportionment_value
