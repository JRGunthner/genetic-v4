import re
from budget_variable_validator.src.tfidf import TfIdf


class VariableAutomapModel:
    def __init__(self):
        self.hpl_script_variable = ""
        self.mapped_variable = ""

    def mapping_to_variable(self, variable, declared_variables):
        if len(declared_variables) > 0:
            table = TfIdf.TfIdf()
            for var in declared_variables:
                table.add_document(var, self.variable_to_array(var))
            doc_similarities = table.similarities(self.variable_to_array(variable))
            doc_similarities.sort(key=lambda x: x[1], reverse=True)
            self.hpl_script_variable = variable
            self.mapped_variable = doc_similarities[0][0]
        else:
            self.hpl_script_variable = variable
            self.mapped_variable = None

    def variable_to_array(self, string):
        strings = re.split("_|\.", string)
        return strings
