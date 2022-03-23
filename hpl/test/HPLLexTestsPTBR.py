import unittest

from hpl.exceptions.Exceptions import TokenizerException
from hpl.tokenizer.hpllexpt import lex
from hpl.engine import error_codes


class HPLlexTest(unittest.TestCase):
    def test_TP_INTEGER(self):
       lex.input("inteiro")
       tok = lex.token()
       self.assertEqual(tok.type, 'TP_INTEGER')
       self.assertEqual(tok.value, 'inteiro')

    def test_TP_FLOAT(self):
        lex.input("flutuante")
        tok = lex.token()
        self.assertEqual(tok.type, 'TP_FLOAT')
        self.assertEqual(tok.value, 'flutuante')

    def test_TP_BOOL(self):
        lex.input("booleano")
        tok = lex.token()
        self.assertEqual(tok.type, 'TP_BOOL')
        self.assertEqual(tok.value, 'booleano')

    def test_TP_ARRAY(self):
        lex.input("sequência")
        tok = lex.token()
        self.assertEqual(tok.type, 'TP_ARRAY')
        self.assertEqual(tok.value, 'sequência')

    def test_TP_CHAR(self):
        lex.input("caracter")
        tok = lex.token()
        self.assertEqual(tok.type, 'TP_CHAR')
        self.assertEqual(tok.value, 'caracter')

    def test_TP_STRING(self):
        lex.input("texto")
        tok = lex.token()
        self.assertEqual(tok.type, 'TP_STRING')
        self.assertEqual(tok.value, 'texto')

    def test_IF(self):
        lex.input("se")
        tok = lex.token()
        self.assertEqual(tok.type, 'IF')
        self.assertEqual(tok.value, 'se')

    def test_THEN(self):
        lex.input("então")
        tok = lex.token()
        self.assertEqual(tok.value, 'então')
        self.assertEqual(tok.type, 'THEN')

    def test_ELSE(self):
        lex.input("senão")
        tok = lex.token()
        self.assertEqual(tok.value, 'senão')
        self.assertEqual(tok.type, 'ELSE')

    def test_WHILE(self):
        lex.input("enquanto")
        tok = lex.token()
        self.assertEqual(tok.type, 'WHILE')
        self.assertEqual(tok.value, 'enquanto')

    def test_DO(self):
        lex.input("faz")
        tok = lex.token()
        self.assertEqual(tok.value, 'faz')
        self.assertEqual(tok.type, 'DO')

    def test_LOAD(self):
        lex.input("carregue")
        tok = lex.token()
        self.assertEqual(tok.type, 'LOAD')
        self.assertEqual(tok.value, 'carregue')

    def test_FROM(self):
        lex.input("de")
        tok = lex.token()
        self.assertEqual(tok.type, 'FROM')
        self.assertEqual(tok.value, 'de')

    def test_LESS(self):
        lex.input("menor")
        tok = lex.token()
        self.assertEqual(tok.type, 'LESS')
        self.assertEqual(tok.value, 'menor')

    def test_GREAT(self):
        lex.input("maior")
        tok = lex.token()
        self.assertEqual(tok.type, 'GREAT')
        self.assertEqual(tok.value, 'maior')

    def test_LESS_EQUAL(self):
        lex.input("menorOuIgual")
        tok = lex.token()
        self.assertEqual(tok.type, 'LESS_EQUAL')
        self.assertEqual(tok.value, 'menorOuIgual')

    def test_GREAT_EQUAL(self):
        lex.input("maiorOuIgual")
        tok = lex.token()
        self.assertEqual(tok.type, 'GREAT_EQUAL')
        self.assertEqual(tok.value, 'maiorOuIgual')

    def test_EQUAL(self):
        lex.input("igual")
        tok = lex.token()
        self.assertEqual(tok.type, 'EQUAL')
        self.assertEqual(tok.value, 'igual')

    def test_NOT_EQUAL(self):
        lex.input("diferente")
        tok = lex.token()
        self.assertEqual(tok.type, 'NOT_EQUAL')
        self.assertEqual(tok.value, 'diferente')

    def test_AND(self):
        lex.input("e")
        tok = lex.token()
        self.assertEqual(tok.type, 'AND')
        self.assertEqual(tok.value, 'e')

    def test_OR(self):
        lex.input("ou")
        tok = lex.token()
        self.assertEqual(tok.type, 'OR')
        self.assertEqual(tok.value, 'ou')

    def test_CHECKLSIT(self):
        lex.input("checklist")
        tok = lex.token()
        self.assertEqual(tok.type, 'CHECKLIST')
        self.assertEqual(tok.value, 'checklist')

    def test_TP_OBJECT(self):
        lex.input("objeto")
        tok = lex.token()
        self.assertEqual(tok.type, 'TP_OBJECT')
        self.assertEqual(tok.value, 'objeto')

    def test_WHERE(self):
        lex.input("onde")
        tok = lex.token()
        self.assertEqual(tok.type, 'WHERE')
        self.assertEqual(tok.value, 'onde')

    def test_INTEGER(self):
        lex.input("12345")
        tok = lex.token()
        self.assertEqual(tok.type, 'INTEGER')
        self.assertEqual(tok.value, 12345)

    def test_FLOAT(self):
        with open('resources/hpl-lex-pt/TestProgram22.hpl', 'r+') as f:
            read_data = f.read()
            f.close()
            lex.input(read_data)
            tok = lex.token()
            self.assertEqual(tok.type, 'FLOAT')
            self.assertEqual(tok.value, 44.11)

    def test_FLOAT_2(self):
        lex.input("0,0003")
        tok = lex.token()
        self.assertEqual(tok.type, 'FLOAT')
        self.assertEqual(tok.value, 0.0003)

    def test_BOOL(self):
        lex.input("verdadeiro falso")
        tok = lex.token()
        self.assertEqual(tok.type, 'BOOL')
        self.assertEqual(tok.value, True)
        tok = lex.token()
        self.assertEqual(tok.type, 'BOOL')
        self.assertEqual(tok.value, False)

    def test_CHAR(self):
        lex.input("\'c\'")
        tok = lex.token()
        self.assertEqual(tok.type, 'CHAR')
        self.assertEqual(tok.value, 'c')

    def test_STRING(self):
        lex.input("\"Teste de texto\"")
        tok = lex.token()
        self.assertEqual(tok.type, 'STRING')
        self.assertEqual(tok.value, "Teste de texto")

    def test_STRING_2(self):
        lex.input("\"2\"")
        tok = lex.token()
        self.assertEqual(tok.type, 'STRING')
        self.assertEqual(tok.value, "2")

    def test_PLUS(self):
        lex.input("+")
        tok = lex.token()
        self.assertEqual(tok.type, 'PLUS')
        self.assertEqual(tok.value, "+")

    def test_MINUS(self):
        lex.input("-")
        tok = lex.token()
        self.assertEqual(tok.type, 'MINUS')
        self.assertEqual(tok.value, "-")

    def test_TIMES(self):
        lex.input("*")
        tok = lex.token()
        self.assertEqual(tok.type, 'TIMES')
        self.assertEqual(tok.value, "*")

    def test_DIVIDE(self):
        lex.input("/")
        tok = lex.token()
        self.assertEqual(tok.type, 'DIVIDE')
        self.assertEqual(tok.value, "/")

    def test_LPAREN(self):
       lex.input("(")
       tok = lex.token()
       self.assertEqual(tok.type, 'LPAREN')
       self.assertEqual(tok.value, "(")

    def test_RPAREN(self):
        lex.input(")")
        tok = lex.token()
        self.assertEqual(tok.type, 'RPAREN')
        self.assertEqual(tok.value, ")")

    def test_RBRACKET(self):
        lex.input("}")
        tok = lex.token()
        self.assertEqual(tok.type, 'RBRACKET')
        self.assertEqual(tok.value, "}")

    def test_LBRACKET(self):
        lex.input("{")
        tok = lex.token()
        self.assertEqual(tok.type, 'LBRACKET')
        self.assertEqual(tok.value, "{")

    def test_SUBPROPERTY(self):
        lex.input(".tamanho")
        tok = lex.token()
        self.assertEqual(tok.type, 'SUBPROPERTY')
        self.assertEqual(tok.value, "tamanho")

    def test_SUBPROPERTY_2(self):
        lex.input(".adiciona")
        tok = lex.token()
        self.assertEqual(tok.type, 'SUBPROPERTY')
        self.assertEqual(tok.value, "adiciona")

    def test_IDENTIFIER(self):
        lex.input("TesteIdentificador")
        tok = lex.token()
        self.assertEqual(tok.type, 'IDENTIFIER')
        self.assertEqual(tok.value, "TesteIdentificador")

    def test_IDENTIFIER2(self):
        lex.input("teste_identificador")
        tok = lex.token()
        self.assertEqual(tok.type, 'IDENTIFIER')
        self.assertEqual(tok.value, "teste_identificador")

    def test_IDENTIFIER3(self):
        lex.input("good")
        tok = lex.token()
        self.assertEqual(tok.type, 'IDENTIFIER')
        self.assertEqual(tok.value, "good")

    def test_MEASURMENT_UNIT_1(self):
        lex.input("g")
        tok = lex.token()
        self.assertEqual(tok.type, 'MEASUREMENT_UNIT')
        self.assertEqual(tok.value, "g")

    def test_MEASURMENT_UNIT_2(self):
        lex.input("mg")
        tok = lex.token()
        self.assertEqual(tok.type, 'MEASUREMENT_UNIT')
        self.assertEqual(tok.value, "mg")

    def test_MEASURMENT_UNIT_3(self):
        lex.input("kg")
        tok = lex.token()
        self.assertEqual(tok.type, 'MEASUREMENT_UNIT')
        self.assertEqual(tok.value, "kg")


    def test_NOT(self):
        lex.input("não")
        tok = lex.token()
        self.assertEqual(tok.type, 'NOT')
        self.assertEqual(tok.value, "não")

    def test_TWO_POINTS(self):
        lex.input(":")
        tok = lex.token()
        self.assertEqual(tok.type, 'TWO_POINTS')
        self.assertEqual(tok.value, ":")

    def test_PRINT_SIMULATOR_FUNCTION(self):
        lex.input("simulador_impressao")
        tok = lex.token()
        self.assertEqual(tok.type, 'PRINT_SIMULATOR_FUNCTION')
        self.assertEqual(tok.value, "simulador_impressao")

    def test_EXISTS_FUNCTION(self):
        lex.input("existe")
        tok = lex.token()
        self.assertEqual(tok.type, 'EXISTS_FUNCTION')
        self.assertEqual(tok.value, "existe")

    def test_THROW(self):
        lex.input("lança")
        tok = lex.token()
        self.assertEqual(tok.type, 'THROW')
        self.assertEqual(tok.value, "lança")

    def test_ERROR(self):
        lex.input("erro")
        tok = lex.token()
        self.assertEqual(tok.type, 'ERROR')
        self.assertEqual(tok.value, "erro")

    def test_ADIMENSIONAL(self):
        lex.input("adimensional")
        tok = lex.token()
        self.assertEqual(tok.type, 'ADIMENSIONAL')
        self.assertEqual(tok.value, "adimensional")

    def test_EXCEPTION(self):
        try:
            lex.input("'")
            tok = lex.token()
            self.assertFail()
        except TokenizerException as e:
            self.assertEqual(e.value['error_code'], error_codes.CODES["LEXICAL_ERROR"])
            self.assertEqual(e.value['error_value'], "'")
            self.assertEqual(e.value['error_line'], 1)
            self.assertEqual(e.value['error_position'], 0)


    def test_EXCEPTION_1(self):
        try:
            lex.input("?")
            tok = lex.token()
            self.assertFail()
        except TokenizerException as e:
            self.assertEqual(e.value['error_code'], error_codes.CODES["LEXICAL_ERROR"])
            self.assertEqual(e.value['error_value'], "?")
            self.assertEqual(e.value['error_line'], 1)
            self.assertEqual(e.value['error_position'], 0)


if __name__ == '__main__':
    unittest.main()