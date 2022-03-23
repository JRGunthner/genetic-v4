from pint import UnitRegistry

ur = UnitRegistry()
Q_ = ur.Quantity

class ProcessFeedstockFormula:
    def __init__(self):
        self.choose_feedstock_formula = {}
        self.feedstock_spent_formula = {}
        self.choose_feedstocks = []
        self.total = 0
        self.quantity = 0
        self.price = 0
        self.measurement_unit = ''
        self.context = {}

    def __getitem__(self, key):
        return getattr(self, key)

    def run_scripts(self, context, automap_variables):
        new_context = {**context, **self.context}

        if self.feedstock_spent_formula:
            for choose_feedstock in self.choose_feedstocks:
                new_context[self.choose_feedstock_formula.context_variable] = choose_feedstock
                feedstock_spent_var_name = self.feedstock_spent_formula.context_variable

                self.feedstock_spent_formula.run_script_storing(new_context, "calc_feedstocks_quantity_spent", automap_variables)

                context[self.feedstock_spent_formula.context_variable] = new_context[self.feedstock_spent_formula.context_variable]
                choose_feedstock["quantity"] = context[feedstock_spent_var_name]
                self.calc_total(choose_feedstock)

        return context

    def calc_total(self, choose_feedstock):
        if choose_feedstock["quantity"] is None:
            choose_feedstock["total"] = None
        else:
            choose_feedstock["total"] = (choose_feedstock["price"] * Q_(choose_feedstock["quantity"])).magnitude

    def choose_min_cost_feedstock(self):
        self.total = self.choose_feedstocks[0]["total"]

        for choose_feedstock in self.choose_feedstocks:

            if choose_feedstock["total"] is not None and choose_feedstock["total"] < self.total:
                self.total = choose_feedstock["total"]

    def get_min_cost_feedstock(self):
        min_cost_feedstock = self.choose_feedstocks[0]

        if 'total' in min_cost_feedstock:
            self.total = min_cost_feedstock['total']

        for choose_feedstock in self.choose_feedstocks:
            if 'total' in choose_feedstock:
                if choose_feedstock is not None and choose_feedstock["total"] < self.total:
                    min_cost_feedstock = choose_feedstock
                    self.total = choose_feedstock["total"]

        return min_cost_feedstock
