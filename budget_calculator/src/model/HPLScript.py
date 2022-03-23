from budget_calculator.src.exceptions.Exceptions import HPLExecutionException
from hpl.engine.interpreter import hpl_interpreter


class HPLScript:
    def __init__(self):
        self.context_variable = ""
        self.script = ""
        self.language = -1

    def __getitem__(self, key):
        return getattr(self, key)

    def run_script(self, context, automap):
        return hpl_interpreter({
            "program": self.script,
            "context": context,
            "automap": automap
        })

    def run_script_storing(self, context, method_name, automap):
        returned_obj = hpl_interpreter({
            "program": self.script,
            "context": context,
            "automap": automap
        })
        if 'measurement_unit' in returned_obj:
            context[self.context_variable] = str(returned_obj["value"]) + returned_obj["measurement_unit"]
        else:
            if "value" not in returned_obj:
                raise HPLExecutionException(
                    {
                        "message": "HPLExecutionError",
                        "variable": returned_obj,
                        "method": method_name
                    })

            context[self.context_variable] = returned_obj["value"]
        return context
