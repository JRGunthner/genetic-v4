import uuid

from pint import UnitRegistry
from budget_calculator.src.model.ProductionCost import ProductionCost
from budget_calculator.src.model.ChooseFeedstock import ChooseFeedstock

ur = UnitRegistry()
Q_ = ur.Quantity


class Feedstock:
    def __init__(self):
        self.unique_local_id = str(uuid.uuid4())
        self.hpl_formula = ""
        self.unit_price = 0.0
        self.quantity_spent = 0.0
        self.use_measurement_unit = ""
        self.context = []
        self.math_function = {}
        self.automap_variables = {}
        self.options = []
        self.total = 0.0
        self.production_cost = ProductionCost()
        self.comercial_id = 0
        self.choose_feedstock = ChooseFeedstock()

    def __getitem__(self, key):
        return getattr(self, key)

    def calc_production_cost(self, context):
        self.calc_feedstock_total(context)
        self.choose_min_price_feedstock(context)
        return context

    def choose_min_price_feedstock(self, context):
        if self.options:
            self.choose_feedstock.total = self.options[0]["total"]
            self.choose_feedstock.selected_option = self.options[0]["option_id"]
            self.choose_feedstock.quantity_spent = self.options[0]["quantity_spent"]
            self.choose_feedstock.unit_price = self.options[0]["price"]

            for option in self.options:
                if option["total"] < self.choose_feedstock.total:
                    self.choose_feedstock.total = option["total"]
                    self.choose_feedstock.quantity_spent = option["quantity_spent"]
                    self.choose_feedstock.unit_price = option["price"]
                    self.choose_feedstock.selected_option = option["option_id"]

            self.production_cost.feedstock_production_cost = self.choose_feedstock.total

    def calc_feedstock_total(self, context):
        for feedstock_context in self.context:
            new_context = {**context, **feedstock_context}
            hpl_formula_result = self.execute_math_function_script(new_context, self.automap_variables)

            if self.choose_feedstock.quantity_spent_changed:
                feedstock_context["quantity_spent"] = self.choose_feedstock.quantity_spent

            if self.choose_feedstock.unit_price_changed:
                feedstock_context["price"] = self.choose_feedstock.unit_price

            if self.math_function and not self.choose_feedstock.quantity_spent_changed:
                feedstock_context["quantity_spent"] = Q_(str(hpl_formula_result[self.math_function.context_variable])).magnitude
            elif not self.choose_feedstock.quantity_spent_changed:
                feedstock_context["quantity_spent"] = 0
                feedstock_context["total"] = 0

            feedstock_context["total"] = Q_(str(feedstock_context["quantity_spent"])).magnitude * feedstock_context["price"]
            feedstock_context["quantity_spent_changed"] = self.choose_feedstock.quantity_spent_changed
            feedstock_context["unit_price_changed"] = self.choose_feedstock.unit_price_changed

            self.options.append(feedstock_context)

    def get_price(self):
        return self.choose_feedstock.quantity_spent * self.choose_feedstock.unit_price

    def execute_math_function_script(self, context, automap_variables):
        try:
            if self.math_function:
                context = self.math_function.run_script_storing(context, "execute_math_function_script", automap_variables)
        except Exception as e:
            e.value['method'] = "execute_pre_hpl_scripts"
            raise

        return context

    def create_by_feedstock_formula(self, feedstock_formula, context):
        feedstock = Feedstock()
        min_cost_feedstock = feedstock_formula.get_min_cost_feedstock()

        if min_cost_feedstock:
            feedstock.total = feedstock_formula["total"]
            feedstock.unit_price = min_cost_feedstock["price"]
            feedstock.choose_feedstock.quantity_spent = Q_(str(min_cost_feedstock["quantity"])).magnitude
            feedstock.choose_feedstock.selected_option = min_cost_feedstock["option_id"]
            feedstock.choose_feedstock.unit_price = min_cost_feedstock["price"]
            feedstock.choose_feedstock.id = min_cost_feedstock["id"]
            feedstock.choose_feedstock.total = min_cost_feedstock["total"]

            if 'comercial_id' in min_cost_feedstock:
                feedstock.comercial_id = min_cost_feedstock["comercial_id"]

            context[feedstock_formula.choose_feedstock_formula.context_variable] = min_cost_feedstock

        if feedstock_formula.choose_feedstock_formula:
            context[feedstock_formula.choose_feedstock_formula.context_variable]['chosen_one'] = min_cost_feedstock

        return feedstock
