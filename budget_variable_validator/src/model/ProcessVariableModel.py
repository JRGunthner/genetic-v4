import copy

from budget_variable_validator.src.model.VariableAutomapModel import VariableAutomapModel
from hpl.engine.variables_validator import get_external_variables


class ProcessVariableModel:
    def __init__(self):
        self.pre_scripts = []
        self.post_scripts = []
        self.simulator_hpl_script = {}
        self.feedstock_formulas = []
        self.ink_cost_script = {}
        self.ink_quantity_script = {}
        self.ink_quantities_script = {}
        self.total_loss_script = {}
        self.percent_loss_script = {}
        self.print_area_script = {}
        self.time_spent_script = {}
        self.total_time_spent_script = {}
        self.feedstock_spent_script = []
        self.total_feedstock_spent_script = []
        self.subtotal_script = {}
        self.declared_variables = []
        self.undeclared_variables = []
        self.mapped_variables = []
        self.external_variables = []

    def validate_pre_scripts(self):
        for script in self.pre_scripts:
            old_declared_variables = self.declared_variables.copy()
            declared_variables, undeclared_variables = get_external_variables(script.script, self.declared_variables)
            if len(undeclared_variables) > 0:
                for var in undeclared_variables:
                    new_map = VariableAutomapModel()
                    new_map.mapping_to_variable(var, old_declared_variables)
                    self.mapped_variables.append(new_map)
            if self.undeclared_variables is None:
                self.undeclared_variables = []
            self.undeclared_variables = self.undeclared_variables + undeclared_variables
            self.declared_variables.append(script.context_variable)
            self.external_variables.append(script.context_variable)

    def validate_post_scripts(self):
        for script in self.post_scripts:
            old_declared_variables = self.declared_variables.copy()
            declared_variables, undeclared_variables = get_external_variables(script.script, self.declared_variables)
            if len(undeclared_variables) > 0:
                for var in undeclared_variables:
                    new_map = VariableAutomapModel()
                    new_map.mapping_to_variable(var, old_declared_variables)
                    self.mapped_variables.append(new_map)
            if self.undeclared_variables is None:
                self.undeclared_variables = []
            self.undeclared_variables = self.undeclared_variables + undeclared_variables
            self.declared_variables.append(script.context_variable)
            self.external_variables.append(script.context_variable)

    def execute_script_validation(self, script):
        old_declared_variables = self.declared_variables.copy()
        declared_variables, undeclared_variables = get_external_variables(script.script,
                               self.declared_variables)
        if len(undeclared_variables) > 0:
            for var in undeclared_variables:
                new_map = VariableAutomapModel()
                new_map.mapping_to_variable(var, old_declared_variables)
                self.mapped_variables.append(new_map)
        if self.undeclared_variables is None:
            self.undeclared_variables = []
        self.undeclared_variables = self.undeclared_variables + undeclared_variables
        self.declared_variables.append(script.context_variable)
        self.external_variables.append(script.context_variable)

    def validate_variables(self, declared_variables):
        if self.declared_variables is None:
            self.declared_variables = []
        self.declared_variables = self.declared_variables + declared_variables
        if self.simulator_hpl_script:
            self.execute_script_validation(self.simulator_hpl_script)
        if self.feedstock_formulas:
            for script in self.feedstock_formulas:
                self.execute_script_validation(script.choose_feedstock_script)
                self.execute_script_validation(script.feedstock_spent_script)
        self.validate_pre_scripts()
        self.validate_process_scripts()
        self.validate_post_scripts()

    def validate_process_scripts(self):
        if self.time_spent_script:
            self.execute_script_validation(self.time_spent_script)
        if self.total_time_spent_script:
            self.execute_script_validation(self.total_time_spent_script)
        if self.feedstock_spent_script:
            for script in self.feedstock_spent_script:
                self.execute_script_validation(script)
        if self.total_feedstock_spent_script:
            for script in self.total_feedstock_spent_script:
                self.execute_script_validation(script)
        self.validate_printing_scripts()

    def validate_printing_scripts(self):
        if self.ink_cost_script:
            self.execute_script_validation(self.ink_cost_script)
        if self.ink_quantity_script:
            self.execute_script_validation(self.ink_quantity_script)
        if self.ink_quantities_script:
            self.execute_script_validation(self.ink_quantities_script)
        if self.total_loss_script:
            self.execute_script_validation(self.total_loss_script)
        if self.print_area_script:
            self.execute_script_validation(self.print_area_script)
        if self.percent_loss_script:
            self.execute_script_validation(self.percent_loss_script)