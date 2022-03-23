import unittest

from hpl.engine.variables_validator import get_external_variables


class HPLVariablesValidatorTests(unittest.TestCase):
    def test_declaring_variable_1(self):
        program = '''
            inteiro x = 1
        '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual([], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_declaring_variable_2(self):
        program = '''
            inteiro x = 1
            y
        '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['y'], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_with_if_1(self):
        program = '''
                    inteiro x = 1
                    se (x maiorOuIgual 3){
                        x = x + 1
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual([], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_with_if_2(self):
        program = '''
                    inteiro x = 1
                    se (y maiorOuIgual 3){
                        x = x + 1
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['y'], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_with_if_3(self):
        program = '''
                    inteiro x = 1
                    se (x maiorOuIgual 3){
                        x = y + 1
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['y'], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_with_if_else_1(self):
        program = '''
                    inteiro x = 1
                    se (x maiorOuIgual 3){
                        x = x + 1
                    } senão{
                        x = y + k
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['y', 'k'], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_with_if_else_2(self):
        program = '''
                    inteiro x = 1
                    inteiro k
                    inteiro y
                    se (x maiorOuIgual 3){
                        x = x + 1
                    } senão{
                        x = y + k
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual([], undeclared_variables)
        self.assertEqual(['x', 'k', 'y'], declared_variables)

    def test_with_if_else_3(self):
        program = '''
                    inteiro x = 1
                    inteiro k
                    inteiro y
                    se (x maiorOuIgual 3){
                        x = x + 1
                    } senão{
                        x = y + k
                    }
                    p
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['p'], undeclared_variables)
        self.assertEqual(['x', 'k', 'y'], declared_variables)

    def test_with_array_1(self):
        program = '''
                    inteiro x = 1
                    sequência y = [x; x+1; x+2]
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual([], undeclared_variables)
        self.assertEqual(['x', 'y'], declared_variables)

    def test_with_array_2(self):
        program = '''
                    inteiro x = 1
                    sequência y = [k; x+1; x+2]
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['k'], undeclared_variables)
        self.assertEqual(['x', 'y'], declared_variables)

    def test_with_while_1(self):
        program = '''
                    inteiro x = 1
                    enquanto(x maiorOuIgual 3) faz{
                        x = x + 1
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual([], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_with_while_2(self):
        program = '''
                    inteiro x = 1
                    enquanto(x maiorOuIgual 3) faz{
                        x = y + 1
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['y'], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_with_while_3(self):
        program = '''
                    inteiro x = 1
                    enquanto(k maiorOuIgual 3) faz{
                        x = y + 1
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['k', 'y'], undeclared_variables)
        self.assertEqual(['x'], declared_variables)

    def test_object_1(self):
        program = '''
                    objeto x = {
                        teste : y;
                        teste2 : "123"
                    }
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['y'], undeclared_variables)
        self.assertEqual(['x', 'x.teste', 'x.teste2'], declared_variables)

    def test_object_2(self):
        program = '''
                    objeto x = {
                        teste : y;
                        teste2 : "123"
                    }
                    
                    x.teste2
                '''
        declared_variables, undeclared_variables = get_external_variables(program, [])
        self.assertEqual(['y'], undeclared_variables)
        self.assertEqual(['x', 'x.teste', 'x.teste2'], declared_variables)