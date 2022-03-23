import uuid

from pint import UnitRegistry
import time

from budget_calculator.src.exceptions.Exceptions import HPLExecutionException
from budget_calculator.src.model.ProductionCost import ProductionCost
from budget_calculator.src.model.ProcessFeedstockFormula import ProcessFeedstockFormula
from budget_calculator.src.model.PrintingCost import PrintingCost
from budget_calculator.src.model.PrintingCost import Reel
from budget_calculator.src.model.PrintingCost import Ink
from budget_calculator.src.model.Feedstock import Feedstock
from budget_calculator.src.error_codes import error_codes

ur = UnitRegistry()
Q_ = ur.Quantity


class Process:
    def __init__(self):
        self.unique_local_id = str(uuid.uuid4())
        self.feedstocks = []
        self.processes = []
        self.simulator_hpl_script = {}
        self.pre_hpl_scripts = []
        self.feedstock_formulas = []
        self.time_spent_formula = {}
        self.feedstock_spent_formulas = []
        self.total_time_spent_formula = []
        self.total_feedstock_spent_formula = []
        self.choose_feedstock_formula = []
        self.choose_midia_feedstock_formula = {}
        self.sub_total_formula = {}
        self.post_hpl_scripts = []
        self.production_cost = ProductionCost()
        self.printing_costs = PrintingCost()
        self.used_reels = []
        self.entry_variables = {}
        self.return_variables = {}
        self.cost_center = 0.0
        self.time_spent = 0.0
        self.context = {}
        self.automap_variables = {}
        self.product_block_feedstocks = []

    def convert_to_local_context(self, context):
        for key, value in self.entry_variables.items():
            if value in context:
                self.context[key] = context[value]

    def convert_to_external_context(self, context):
        for key, value in self.return_variables.items():
            if value in self.context:
                context[key] = self.context[value]
        return context

    def execute_pre_hpl_scripts(self):
        if self.pre_hpl_scripts is not None:
            for script in self.pre_hpl_scripts:
                try:
                    self.context = script.run_script_storing(self.context, "execute_pre_hpl_scripts",
                                                             self.automap_variables)
                except Exception as e:
                    e.value['method'] = "execute_pre_hpl_scripts"
                    raise

    def set_product_block_feedstock(self, context):
        for feedstock_formula in self.feedstock_formulas:
            feedstock = Feedstock()

    def calc_production_cost(self, context):
        self.convert_to_local_context(context)
        self.production_cost = ProductionCost()
        self.execute_pre_hpl_scripts()
        self.execute_simulator_hpl_script()
        self.context = self.choose_feedstock(self.context)
        self.context = self.calc_feedstocks_quantity_spent(self.context)
        self.context = self.calc_time_spent(self.context)
        self.context = self.calc_time_cost(self.context)
        self.context = self.calc_printing_cost(context)

        return self.convert_to_external_context(context)

    def calc_printing_cost(self, context):
        if self.simulator_hpl_script:
            self.printing_costs = PrintingCost()
            self.context = self.calc_ink_cost(self.context)
            self.context = self.calc_ink_quantity(self.context)
            self.context = self.calc_inks_quantities(self.context)
            self.context = self.calc_total_loss(self.context)
            self.context = self.calc_printing_area(self.context)
            self.context = self.calc_percent_loss(self.context)
            self.context = self.choose_machine(self.context)
            self.context = self.choose_printing_profile(self.context)
            self.context = self.choose_reels(self.context)
            self.context = self.calc_total_bins_area(self.context)
            self.time_spent = self.time_spent / 60
            self.printing_costs.time_spent = self.time_spent
            self.context = self.load_allocation_map(self.context)
            self.context = self.load_amendment_list(self.context)
            self.context = self.load_obj(self.context)

        return context

    def choose_reels(self, context):
        if self.choose_midia_feedstock_formula:
            try:
                context = self.choose_midia_feedstock_formula.run_script_storing(context,
                                                                                 "choose_midia_feedstock_formula",
                                                                                 self.automap_variables)
            except Exception as e:
                e.value['method'] = "choose_midia"
                raise

            choose_used_reels = context[self.choose_midia_feedstock_formula.context_variable]
            for i in range(len(choose_used_reels)):
                used_reel = choose_used_reels[i]
                reel = Reel()
                reel.option_id = used_reel[0]
                reel.percent_loss = used_reel[1]
                reel.comercial_id = used_reel[2]
                reel.feedstock_id = used_reel[3]
                reel.version = used_reel[4]
                self.printing_costs.used_reels.append(reel)

        return context

    def execute_simulator_hpl_script(self):
        if self.simulator_hpl_script:
            try:
                self.simulator_hpl_script.run_script_storing(self.context, "execute_simulator_hpl_script",
                                                             self.automap_variables)
                feedstock_formula = ProcessFeedstockFormula()

                for choose_feedstock in self.context[self.simulator_hpl_script.context_variable]['choose_feedstocks']:
                    try:
                        choose_feedstock["quantity"] = self.context[self.simulator_hpl_script.context_variable][
                            'bins_area']
                        feedstock_formula.quantity = choose_feedstock["quantity"]
                        feedstock_formula.calc_total(choose_feedstock)
                        feedstock_formula.choose_feedstocks.append(choose_feedstock)

                    except Exception as e:
                        e.value['method'] = "choose_simulator_feedstock"
                        raise

                feedstock_formula.choose_min_cost_feedstock()
                self.feedstock_formulas.append(feedstock_formula)

            except Exception as e:
                e.value['method'] = "execute_simulator_hpl_script"
                raise

    def choose_feedstock(self, context):
        try:
            if not self.simulator_hpl_script:
                for feedstock_formula in self.feedstock_formulas:
                    feedstock_formula.choose_feedstock_formula.run_script_storing(context, "choose_feedstock",
                                                                                  self.automap_variables)

                    if not feedstock_formula.choose_feedstocks:
                        feedstock_formula.choose_feedstocks = context[
                            feedstock_formula.choose_feedstock_formula.context_variable]

                        self.calc_choose_feedstocks_quantity(context, feedstock_formula)

            return context
        except Exception as e:
            e.value['method'] = "choose_feedstock"
            raise

    def calc_choose_feedstocks_quantity(self, context, feedstock_formula):
        try:
            context = feedstock_formula.run_scripts(context, self.automap_variables)
            self.production_cost.feedstock_production_cost += feedstock_formula.total

            feedstock = Feedstock().create_by_feedstock_formula(feedstock_formula, context)

            if feedstock.choose_feedstock.total > 0:
                self.product_block_feedstocks.append(feedstock)
        except Exception as e:
            e.value['method'] = "calc_feedstocks_quantity_spent"
            raise

    def calc_feedstocks_quantity_spent(self, context):
        for feedstock in self.feedstocks:
            context = feedstock.calc_production_cost(context)
            self.production_cost.feedstock_production_cost += feedstock.production_cost.feedstock_production_cost

        return context

    def calc_ink_cost(self, context):
        if self.ink_cost_formula:
            try:
                context = self.ink_cost_formula.run_script_storing(context, "ink_cost_formula", self.automap_variables)
            except Exception as e:
                e.value['method'] = "calc_ink_cost"
                raise

            hpl_formula_result = context[self.ink_cost_formula.context_variable]
            self.printing_costs.ink_cost = Q_(hpl_formula_result).magnitude

        return context

    def calc_ink_quantity(self, context):
        if self.ink_quantity_formula:
            try:
                context = self.ink_quantity_formula.run_script_storing(context, "ink_quantity_formula",
                                                                       self.automap_variables)
            except Exception as e:
                e.value['method'] = "calc_ink_quantity"
                raise

            hpl_formula_result = context[self.ink_quantity_formula.context_variable]
            self.printing_costs.ink_quantity = Q_(hpl_formula_result).magnitude

        return context

    def calc_inks_quantities(self, context):
        if self.inks_quantities_formula:
            try:
                context = self.inks_quantities_formula.run_script_storing(context, "inks_quantities_formula",
                                                                          self.automap_variables)
            except Exception as e:
                e.value['method'] = "calc_inks_quantities"
                raise

            self.printing_costs.inks_quantities = []
            inks_quantities = context[self.inks_quantities_formula.context_variable]
            for used_ink in inks_quantities:
                ink = Ink()
                ink.feedstock_id = used_ink[0]
                ink.option_id = used_ink[1]
                ink.quantity_spent = used_ink[2]
                ink.version = used_ink[3]
                self.printing_costs.inks_quantities.append(ink)

        return context

    def calc_total_loss(self, context):
        if self.total_loss_formula:
            try:
                context = self.total_loss_formula.run_script_storing(context, "total_loss_formula",
                                                                     self.automap_variables)
            except Exception as e:
                e.value['method'] = "calc_total_loss"
                raise
            self.printing_costs.total_loss = context[self.total_loss_formula.context_variable]

        return context

    def calc_printing_area(self, context):
        if self.printing_area_formula:
            try:
                context = self.printing_area_formula.run_script_storing(context, "printing_area_formula",
                                                                        self.automap_variables)
            except Exception as e:
                e.value['method'] = "calc_printing_area"
                raise

            self.printing_costs.printing_area = context[self.printing_area_formula.context_variable]

        return context

    def calc_total_bins_area(self, context):
        for feedstock_formula in self.feedstock_formulas:
            try:
                self.printing_costs.bins_area = feedstock_formula.quantity
            except Exception as e:
                e.value['method'] = "calc_total_bins_area"
                raise

        return context

    def calc_percent_loss(self, context):
        if self.percent_loss_formula:
            try:
                context = self.percent_loss_formula.run_script_storing(context, "percent_loss_formula",
                                                                       self.automap_variables)
            except Exception as e:
                e.value['method'] = "calc_percent_loss"
                raise

            self.printing_costs.percent_loss = context[self.percent_loss_formula.context_variable]

        return context

    def choose_machine(self, context):
        if self.choose_machine_id_formula:
            try:
                context = self.choose_machine_id_formula.run_script_storing(context, "choose_machine_id_formula",
                                                                            self.automap_variables)
            except Exception as e:
                e.value['method'] = "choose_machine"
                raise

            self.printing_costs.machine_info = context[self.choose_machine_id_formula.context_variable]

        return context

    def choose_printing_profile(self, context):
        if self.choose_profile_index_formula:
            try:
                context = self.choose_profile_index_formula.run_script_storing(context, "choose_profile_index_formula",
                                                                               self.automap_variables)
            except Exception as e:
                e.value['method'] = "choose_profile_index_formula"
                raise

            self.printing_costs.printing_profile_index = context[self.choose_profile_index_formula.context_variable]

        return context

    def load_allocation_map(self, context):
        if self.allocation_map_formula:
            try:
                context = self.allocation_map_formula.run_script_storing(context, "allocation_map_formula",
                                                                         self.automap_variables)
            except Exception as e:
                e.value['method'] = "load_allocation_map"
                raise

            self.printing_costs.allocation_map = context[self.allocation_map_formula.context_variable]

        return context

    def load_amendment_list(self, context):
        if self.amendment_list_formula:
            try:
                context = self.amendment_list_formula.run_script_storing(context, "amendment_list_formula",
                                                                         self.automap_variables)
            except Exception as e:
                e.value['method'] = "load_amendment_list"
                raise

            self.printing_costs.amendment_list = context[self.amendment_list_formula.context_variable]

        return context

    def load_obj(self, context):
        if self.obj_formula:
            try:
                context = self.obj_formula.run_script_storing(context, "obj_formula", self.automap_variables)
            except Exception as e:
                e.value['method'] = "obj"
                raise

            self.printing_costs.obj = context[self.obj_formula.context_variable]

        return context

    def calc_time_spent(self, context):
        if not self.time_spent_formula:
            raise HPLExecutionException(
                {
                    "message": "HPLExecutionError",
                    "variable": {
                        "error_code": error_codes.CODES["FORMULA_NOT_FOUND"],
                        "message_error": {
                            "error_value": "time_spent_formula"
                        }
                    },
                    "method": "calc_time_spent"
                })
        try:
            context = self.time_spent_formula.run_script_storing(context, "calc_time_spent", self.automap_variables)
        except Exception as e:
            e.value['method'] = "calc_time_spent"
            raise

        hpl_formula_result = Q_(context[self.time_spent_formula.context_variable])
        if hpl_formula_result.unitless:
            self.time_spent = Q_(hpl_formula_result).magnitude
        else:
            try:
                self.time_spent = Q_(hpl_formula_result).to("min").magnitude
            except Exception:
                raise HPLExecutionException(
                    {
                        "message": "HPLExecutionError",
                        "variable": {
                            "error_code": error_codes.CODES["CAST_TO_HOUR_NOT_POSSIBLE"],
                            "message_error": {
                                "error_value": Q_(hpl_formula_result)
                            }
                        },
                        "method": "calc_time_spent"
                    })
        return context

    def calc_time_cost(self, context):
        if (not self.total_time_spent_formula):
            raise HPLExecutionException(
                {
                    "message": "HPLExecutionError",
                    "variable": {
                        "error_code": error_codes.CODES["FORMULA_NOT_FOUND"],
                        "message_error": {
                            "error_value": "total_time_spent_formula"
                        }
                    },
                    "method": "choose_feedstock"
                })
        try:
            context = self.total_time_spent_formula.run_script_storing(context, "calc_time_cost",
                                                                       self.automap_variables)
        except Exception as e:
            e.value['method'] = "calc_time_cost"
            raise

        hpl_formula_result = context[self.total_time_spent_formula.context_variable]
        self.production_cost.labor_production_cost = Q_(hpl_formula_result).magnitude

        return context

    def execute_post_hpl_scripts(self):
        for script in self.post_hpl_scripts:
            try:
                self.context = script.run_script_storing(self.context, "execute_post_hpl_scripts",
                                                         self.automap_variables)
            except Exception as e:
                e.value['method'] = "execute_post_hpl_scripts"
                raise
