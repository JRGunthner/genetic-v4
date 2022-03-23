import uuid

from budget_calculator.src.model.ProductionCost import ProductionCost
from pint import UnitRegistry

ur = UnitRegistry()
Q_ = ur.Quantity


class Product:
    def __init__(self):
        self.unique_local_id = str(uuid.uuid4())
        self.processes = []
        self.feedstocks = []
        self.production_cost = {}
        self.pre_hpl_scripts = []
        self.post_hpl_scripts = []
        self.selling_cost = 0.0
        self.apportionment_value = 0.0
        self.price_method = {}
        self.total_value = 0.0
        self.total_quantity = 0.0
        self.income_selling_cost = {}
        self.context = {}
        self.automap_variables = {}
        self.total_quantity_formulas = []

    def __getitem__(self, key):
        return getattr(self, key)

    def execute_pre_hpl_scripts(self):
        if self.pre_hpl_scripts is not None:
            for script in self.pre_hpl_scripts:
                script.run_script_storing(self.context, "execute_pre_hpl_scripts", self.automap_variables)

    def calc_production_cost(self, context):
        new_context = {**context, **self.context}
        self.production_cost = ProductionCost()
        process_index = 0
        for process in self.processes:
            try:
                context = process.calc_production_cost(new_context)
            except Exception as e:
                e.value['variable']["message_error"]["process_index"] = process_index
                raise
            process_index += 1
            self.production_cost.labor_production_cost += process.production_cost.labor_production_cost
            self.production_cost.feedstock_production_cost += process.production_cost.feedstock_production_cost

        feedstock_index = 0
        for feedstock in self.feedstocks:
            try:
                context = feedstock.calc_production_cost(context)
                self.production_cost.feedstock_production_cost += feedstock.production_cost.feedstock_production_cost
            except Exception as e:
                e.value['variable']["message_error"]["feedstock_index"] = feedstock_index
                raise
            feedstock_index += 1

    def calc_total_value(self, context):
        self.context[self.price_method.hpl_formula.context_variable] = self.production_cost.sum_total()
        new_context = {**context, **self.context, **self.income_selling_cost.generate_subcontext()}

        self.price_method.run_pre_hpl_scripts(new_context)
        self.total_value = self.price_method.run_budget_price_method(new_context)

    def calc_total_quantity(self, measurement_unit_hpl_symbol):
        self.total_quantity = float(0.0)

        if self.total_quantity_formulas is not None:
            for total_quantity_formula in self.total_quantity_formulas:
                try:
                    if total_quantity_formula["measurement_unit_hpl_symbol"] == measurement_unit_hpl_symbol and total_quantity_formula['hpl_script'] is not None:
                        hpl_script = total_quantity_formula['hpl_script']

                        self.context = hpl_script.run_script_storing(self.context, "total_quantity_formula", self.automap_variables)
                        self.total_quantity = Q_(self.context[hpl_script.context_variable]).magnitude
                except Exception as e:
                    e.value['method'] = "total_quantity_formula"
                    raise

    def set_apportionment(self, value):
        self.apportionment_value = value
        self.production_cost.distribute_apportionment_value(value)

    def execute_post_hpl_scripts(self):
        for script in self.post_hpl_scripts:
            script.run_script(self.context, self.automap_variables)
