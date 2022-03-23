import unittest

from budget_variable_validator.src.model import VariableAutomapModel


class VariableAutomapModelTests(unittest.TestCase):

    def test_case_1(self):
        declared_variables = ['medidas_do_trabalho.altura', 'medidas_do_trabalho.largura', 'medidas_do_trabalho.descricao']
        undeclared_variable = 'altura'
        automap = VariableAutomapModel.VariableAutomapModel()
        automap.mapping_to_variable(undeclared_variable, declared_variables)
        self.assertEqual(automap.hpl_script_variable, 'altura')
        self.assertEqual(automap.mapped_variable, 'medidas_do_trabalho.altura')

    def test_case_2(self):
        declared_variables = ['medidas_do_trabalho.altura', 'medidas_do_trabalho.largura', 'medidas_do_trabalho.descricao']
        undeclared_variable = 'medidas.altura'
        automap = VariableAutomapModel.VariableAutomapModel()
        automap.mapping_to_variable(undeclared_variable, declared_variables)
        self.assertEqual(automap.hpl_script_variable, 'medidas.altura')
        self.assertEqual(automap.mapped_variable, 'medidas_do_trabalho.altura')

    def test_case_3(self):
        declared_variables = ['medidas_do_trabalho.altura', 'medidas_do_trabalho.largura', 'medidas_do_trabalho.descricao']
        undeclared_variable = 'descricao'
        automap = VariableAutomapModel.VariableAutomapModel()
        automap.mapping_to_variable(undeclared_variable, declared_variables)
        self.assertEqual(automap.hpl_script_variable, 'descricao')
        self.assertEqual(automap.mapped_variable, 'medidas_do_trabalho.descricao')

    def test_case_4(self):
        declared_variables = ['medidas_do_trabalho.altura', 'medidas_do_trabalho.largura', 'medidas_do_trabalho.descricao', 'descricao']
        undeclared_variable = 'descricao'
        automap = VariableAutomapModel.VariableAutomapModel()
        automap.mapping_to_variable(undeclared_variable, declared_variables)
        self.assertEqual(automap.hpl_script_variable, 'descricao')
        self.assertEqual(automap.mapped_variable, 'descricao')