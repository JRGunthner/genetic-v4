from pint import UnitRegistry

ur = UnitRegistry()
Q_ = ur.Quantity


class BudgetPriceMethod:
    def __init__(self):
        self.context = {}
        self.hpl_formula = {}
        self.pre_hpl_scripts = []

    def __getitem__(self, key):
        return getattr(self, key)

    def run_budget_price_method(self, context):
        newcontext = {**self.context, **context}
        newcontext = self.hpl_formula.run_script_storing(newcontext, "run_budget_price_method", {})
        variable = self.hpl_formula["context_variable"]

        return Q_(newcontext[variable]).magnitude

    def run_pre_hpl_scripts(self, context):
        if self.pre_hpl_scripts is not None:
            newcontext = {**self.context, **context}

            for pre_hpl_script in self.pre_hpl_scripts:
                newcontext = pre_hpl_script.run_script_storing(newcontext, "run_budget_price_method_pre_hpl_scripts", {})
                variable = pre_hpl_script["context_variable"]
                context[variable] = newcontext[variable]
