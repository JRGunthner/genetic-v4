import copy

from budget_variable_validator.src.model.VariableAutomapModel import VariableAutomapModel
from hpl.engine.variables_validator import get_external_variables


class ProductVariableModel:
    def __init__(self):
        self.pre_scripts = []
        self.post_scripts = []
        self.processes = []
        self.declared_variables = []
        self.external_variables = []
        self.undeclared_variables = []
        self.mapped_variables = []

    def validate_pre_scripts(self):
        for script in self.pre_scripts:
            old_declared_variables = copy.copy(self.declared_variables)
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
            old_declared_variables = copy.copy(self.declared_variables)
            result = get_external_variables(script.script, self.declared_variables)
            if len(result) > 0:
                for var in result:
                    new_map = VariableAutomapModel()
                    new_map.mapping_to_variable(var, old_declared_variables)
                    self.mapped_variables.append(new_map)
            self.undeclared_variables = self.undeclared_variables + result
            self.declared_variables.append(script.context_variable)
            self.external_variables.append(script.context_variable)

    def validate_variables(self):
        self.validate_pre_scripts()
        mapped_variables_internal = []
        for process in self.processes:
            process.mapped_variables = mapped_variables_internal
            process.validate_variables(self.declared_variables)
            self.declared_variables = self.declared_variables + process.external_variables
            mapped_variables_internal = process.mapped_variables
