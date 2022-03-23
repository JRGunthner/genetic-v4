import unittest

from hpl.parser.hplparser import parser
from hpl.exceptions.Exceptions import ParserException
from hpl.engine import error_codes


class HPLParserTest(unittest.TestCase):

    def test_DECLARATION_WITHOUT_VALUE(self):
       result = parser.parse('''
       inteiro x
       ''')
       self.assertEqual(result, ('DECLARING', 'INTEGER', 'x', None))

    def test_DECLARATION_WITHOUT_IDENTIFIER(self):
        try:
            result = parser.parse('''
                      inteiro
                      ''')
            self.assertFail()
        except ParserException as e:
            self.assertEqual(e.value['error_code'], error_codes.CODES["EOI_ERROR"])

    def test_DECLARATION_WITH_VALUE(self):
       result = parser.parse('''
              inteiro x = 5
              ''')
       self.assertEqual(result, ('DECLARING', 'INTEGER', 'x',
                                 ('INTEGER', 5)))

    def test_DECLARATION_WITH_NEGATIVE_VALUE(self):
       result = parser.parse('''
              inteiro x = -45
              ''')
       self.assertEqual(result, ('DECLARING', 'INTEGER', 'x',
                                 ('INTEGER', '-', 45)))

    def test_DECLARATION_WITH_VARIABLE_REUSE(self):
        result = parser.parse('''
             inteiro x = 5
             inteiro y = 5
             x = y
             ''')
        self.assertEqual(result, ('DECLARING', 'INTEGER', 'x',
                                  ('INTEGER', 5),
                                  ('DECLARING', 'INTEGER', 'y',
                                   ('INTEGER', 5),
                                   ('ATTRIBUITION', 'x',
                                    ('IDENTIFIER', 'y')))))

    def test_DECLARATION_WITH_VARIABLE_OPERATION(self):
        result = parser.parse('''
             inteiro x = 5
             inteiro y = 5
             x = (y + x)
             ''')
        self.assertEqual(result, ('DECLARING', 'INTEGER', 'x',
                                  ('INTEGER', 5),
                                  ('DECLARING', 'INTEGER', 'y',
                                   ('INTEGER', 5),
                                   ('ATTRIBUITION', 'x',
                                    ('PLUS',
                                     ('IDENTIFIER', 'y'),
                                     ('IDENTIFIER', 'x'))))))

    def test_DECLARATION_ARRAY(self):
        result = parser.parse('''
            sequência nova_sequencia = [10;20;30]
        ''')
        self.assertEqual(result, ('DECLARING', 'ARRAY', 'nova_sequencia', ('ARRAY', (('INTEGER', 10), ('INTEGER', 20), ('INTEGER', 30)))))

    def test_DECLARATION_ARRAY_WITHOUT_CLOSE(self):
        try:
            result = parser.parse('''
                        sequência nova_sequencia = [10;20;30
                    ''')
            self.assertFail()
        except ParserException as e:
            self.assertEqual(e.value['error_code'], error_codes.CODES["EOI_ERROR"])

    def test_DECLARATION_ARRAY_WITH_COMA(self):
        try:
            result = parser.parse('''
                        sequência nova_sequencia = [10,20,30]
                    ''')
            self.assertFail()
        except ParserException as e:
            self.assertEqual(e.value['error_code'], error_codes.CODES["SINTAX_ERROR"])
            self.assertEqual(e.value['error_value'], 0.3)

    def test_DECLARATION_ARRAY_WITH_STRING(self):
        result = parser.parse('''
            sequência nova_sequencia = ["teste";"2";30]
        ''')
        self.assertEqual(result, ('DECLARING', 'ARRAY', 'nova_sequencia', ('ARRAY', (('STRING', 'teste'), ('STRING', '2'), ('INTEGER', 30)))))

    def test_DECLARATION_ARRAY_WITH_EXPRESSION(self):
        result = parser.parse('''
            sequência nova_sequencia = [10;20;30+3]
        ''')
        self.assertEqual(result, ('DECLARING',
                                  'ARRAY',
                                  'nova_sequencia',
                                  ('ARRAY',
                                  (('INTEGER', 10),
                                   ('INTEGER', 20),
                                   ('PLUS', ('INTEGER', 30), ('INTEGER', 3))))))

    def test_IF_1(self):
        result = parser.parse('''
                     se (verdadeiro) {
                        10
                     }
                     ''')
        self.assertEqual(result, ('IF', ('BOOL', True), ('INTEGER', 10), None))

    def test_IF_2(self):
        result = parser.parse('''
                     se (falso) {
                        10
                     } senão {
                        11
                     }
                     ''')
        self.assertEqual(result, ('IF', ('BOOL', False), ('INTEGER', 10), ('INTEGER',11)))

    def test_IF_3(self):
        result = parser.parse('''
                     se (falso) {
                        10
                     } senão se (falso) {
                        11
                     } senão {
                        5
                     }
                     ''')
        self.assertEqual(result, ('IF', ('BOOL', False), ('INTEGER', 10), ('IF',('BOOL', False), ('INTEGER', 11), ('INTEGER', 5))))

    def test_IF_4(self):
        result = parser.parse('''
                     booleano teste = (5m maiorOuIgual (10cm * 12))
                     se (teste) {
                        10
                     } senão se (teste) {
                        11
                     } senão {
                        5
                     }
                     ''')
        self.assertEqual(result, ('DECLARING', 'BOOLEAN', 'teste',
                                  ('GREAT_EQUAL',
                                   ('MEASUREMENT_UNIT_CAST',
                                    ('INTEGER', 5),
                                    'm'),
                                   ('TIMES',
                                    ('MEASUREMENT_UNIT_CAST',
                                     ('INTEGER',10),
                                     'cm'),
                                    ('INTEGER', 12)
                                    )
                                   ),
                                  ('IF',
                                   ('IDENTIFIER', 'teste'),
                                   ('INTEGER', 10),
                                   ('IF',('IDENTIFIER', 'teste'),
                                    ('INTEGER', 11),
                                    ('INTEGER', 5)))))

    def test_EXPRESSION_EVALUATION_ORDER_1(self):
        result = parser.parse('''
                    1 + 2 + 3
                ''')
        self.assertEqual(result, ('PLUS', ('INTEGER', 1), ('PLUS', ('INTEGER', 2), ('INTEGER', 3))))

    def test_EXPRESSION_EVALUATION_ORDER_2(self):
        result = parser.parse('''
                    1 + (2 + 3)
                ''')
        self.assertEqual(result, ('PLUS', ('INTEGER', 1), ('PLUS', ('INTEGER', 2), ('INTEGER', 3))))

    def test_EXPRESSION_EVALUATION_ORDER_3(self):
        result = parser.parse('''
                    1 + 2 * 3
                ''')
        self.assertEqual(result, ('PLUS', ('INTEGER', 1), ('TIMES', ('INTEGER', 2), ('INTEGER', 3))))

    def test_EXPRESSION_EVALUATION_ORDER_4(self):
        result = parser.parse('''
                    1 * 2 + 3
                ''')
        self.assertEqual(result, ('PLUS', ('TIMES', ('INTEGER', 1), ('INTEGER', 2)), ('INTEGER', 3)))

    def test_EXPRESSION_EVALUATION_ORDER_5(self):
        result = parser.parse('''
                    1 * 2 / 3
                ''')
        self.assertEqual(result, ('DIVIDE', ('TIMES', ('INTEGER', 1), ('INTEGER', 2)), ('INTEGER', 3)))

    def test_MEASUREMENT_UNIT_EXPRESSIONS(self):
        result = parser.parse('''
                            5 km + (3 m) / 50 cm
                        ''')
        self.assertEqual(result, ('PLUS', ('MEASUREMENT_UNIT_CAST',
                                             ('INTEGER', 5), 'km'),
                                          ('DIVIDE',
                                             ('MEASUREMENT_UNIT_CAST', ('INTEGER', 3), 'm'),
                                          ('MEASUREMENT_UNIT_CAST', ('INTEGER', 50), 'cm'))))

    def test_BOOLEAN_EXPRESSION_OR(self):
        result = parser.parse('''
            falso ou verdadeiro
        ''')
        self.assertEqual(result, ('OR', ('BOOL', False), ('BOOL', True)))

    def test_BOOLEAN_EXPRESSION_AND(self):
        result = parser.parse('''
            falso e verdadeiro
        ''')
        self.assertEqual(result, ('AND', ('BOOL', False), ('BOOL', True)))

    def test_BOOLEAN_EXPRESSION_EQUALS(self):
        result = parser.parse('''
            falso igual verdadeiro
        ''')
        self.assertEqual(result, ('EQUAL', ('BOOL', False), ('BOOL', True)))

    def test_BOOLEAN_EXPRESSION_NOT_EQUAL(self):
        result = parser.parse('''
            falso diferente verdadeiro
        ''')
        self.assertEqual(result, ('NOT_EQUAL', ('BOOL', False), ('BOOL', True)))

    def test_BOOLEAN_EXPRESSION_GREAT(self):
        result = parser.parse('''
            10 maior 11,2
        ''')
        self.assertEqual(result, ('GREAT', ('INTEGER', 10), ('FLOAT', 11.2)))

    def test_BOOLEAN_EXPRESSION_LESS(self):
        result = parser.parse('''
            10 menor 11,2
        ''')
        self.assertEqual(result, ('LESS', ('INTEGER', 10), ('FLOAT', 11.2)))

    def test_BOOLEAN_EXPRESSION_GREAT_EQUAL(self):
        result = parser.parse('''
            10 maiorouigual 11,2
        ''')
        self.assertEqual(result, ('GREAT_EQUAL', ('INTEGER', 10), ('FLOAT', 11.2)))

    def test_BOOLEAN_EXPRESSION_LESS_EQUAL(self):
        result = parser.parse('''
            10 menorouigual 11,2
        ''')
        self.assertEqual(result, ('LESS_EQUAL', ('INTEGER', 10), ('FLOAT', 11.2)))

    def test_WHILE_1(self):
        result = parser.parse('''
                    enquanto (1 maiorouigual 2) faz {
                        contador + 1
                    }
                ''')
        self.assertEqual(result, ('WHILE', ('GREAT_EQUAL', ('INTEGER', 1),
                                            ('INTEGER', 2)), ('PLUS', ('IDENTIFIER', 'contador'), ('INTEGER', 1))))

    def test_ATTRIBUITION_ARRAY(self):
        result = parser.parse('''
                           teste{1} = 20
                       ''')
        self.assertEqual(result, ('ATTRIBUITION_ARRAY', 'teste', ('INTEGER', 20), ('INTEGER', 1)))

    def test_SUBPROPERTY(self):
        result = parser.parse('''
                                  teste.tamanho
                              ''')
        self.assertEqual(result, ('ACCESS_SUBPROPERTY', ('IDENTIFIER','teste'), 'tamanho'))

    def test_SUBPROPERTY_2(self):
        result = parser.parse('''
                                  teste.arredonda(2)
                              ''')
        self.assertEqual(result, ('ACCESS_SUBPROPERTY', ('IDENTIFIER','teste'), 'arredonda', ('INTEGER', 2)))

    def test_SUBPROPERTY_3(self):
        result = parser.parse('''
                                medidas.adiciona(medida)
                            ''')
        self.assertEqual(result, ('ACCESS_SUBPROPERTY', ('IDENTIFIER', 'medidas'), 'adiciona', ('IDENTIFIER', 'medida')))

    def test_OBJECT_DEFINITION(self):
        result = parser.parse('''
            teste = {
               numero1 : "numero 1"
            }
        ''')
        self.assertEqual(result,
                         ('ATTRIBUITION',
                          'teste',
                          ('OBJECT', ('OBJECT_DEFINITION', 'numero1', ('STRING', 'numero 1')))))

    def test_OBJECT_DEFINITION_2(self):
        result = parser.parse('''
            teste = {
               numero1 : "numero 1";
               numero2 : 2
            }
        ''')
        self.assertEqual(result,
                         ('ATTRIBUITION',
                          'teste',
                          ('OBJECT',
                           ('OBJECT_DEFINITION',
                            'numero1',
                            ('STRING', 'numero 1'),
                            ('OBJECT_DEFINITION', 'numero2', ('INTEGER', 2))))))

    def test_THROW_ERROR(self):
        result = parser.parse('''
            lança erro ("mensagem de erro")
        ''')
        self.assertEqual(result , ('ERROR', "mensagem de erro"))

    def test_THROW_ERROR_2(self):
        try:
            result = parser.parse('''
                        lança erro (2 + 2)
                    ''')
            self.assertFail()
        except ParserException as e:
            self.assertEqual(e.value['error_code'], error_codes.CODES["SINTAX_ERROR"])
            self.assertEqual(e.value['error_value'], 2)

    def test_THROW_ERROR_3(self):
        try:
            result = parser.parse('''
                           lança nada
                       ''')
            self.assertFail()
        except ParserException as e:
            self.assertEqual(e.value['error_code'], error_codes.CODES["SINTAX_ERROR"])
            self.assertEqual(e.value['error_value'], "nada")


    def test_PRINT_SIMULATOR_FUNCTION(self):
        result = parser.parse('''
                    simulador_impressao([[300; 400; "1"; 4; 100; "right"; "bottom"]; [400; 500; "2"; 3; 100; "right"; "bottom"]]; 
                                        [{
                                            RIP_time: 180;
                                            bins: [[3200; 50000; 0,000006; 0]; [1500; 50000; 0,000006; 1]];
                                            calc_type: "openess_calc";
                                            init_time: 180;
                                            inset_reels: falso;
                                            margins: {
                                               top: 0; 
                                               left: 0;
                                               right: 0;
                                               bottom: 0
                                            };
                                            max_parallel_reels: 100;
                                            openess: 3200;
                                            produtivity: 11111,12;
                                            space_between_reels: 100;
                                            time_cost:0
                                        }]; 
                                        {
                                            generations : 300;
                                            max_stablement: 30;
                                            population: 10
                                        }; 
                                        {
                                            consider_amendments_number: verdadeiro;
                                            consider_bins_number: falso;
                                            horizontal_cut: verdadeiro;
                                            infinite_height: falso;
                                            minimum_cut: 1000;
                                            overwrite_itens_amendments_configurations: falso;
                                            printed_amendment: verdadeiro;
                                            reuse_bins: verdadeiro;
                                            same_supplier: falso;
                                            vertical_cut: verdadeiro
                                        })
                ''')
        self.assertEqual(result, ('PRINT_SIMULATOR_FUNCTION',
 ('ARRAY',
  (('ARRAY',
    (('INTEGER', 300),
     ('INTEGER', 400),
     ('STRING', '1'),
     ('INTEGER', 4),
     ('INTEGER', 100),
     ('STRING', 'right'),
     ('STRING', 'bottom'))),
   ('ARRAY',
    (('INTEGER', 400),
     ('INTEGER', 500),
     ('STRING', '2'),
     ('INTEGER', 3),
     ('INTEGER', 100),
     ('STRING', 'right'),
     ('STRING', 'bottom'))))),
 ('ARRAY',
  (('OBJECT',
    ('OBJECT_DEFINITION',
     'RIP_time',
     ('INTEGER', 180),
     ('OBJECT_DEFINITION',
      'bins',
      ('ARRAY',
       (('ARRAY',
         (('INTEGER', 3200),
          ('INTEGER', 50000),
          ('FLOAT', 6e-06),
          ('INTEGER', 0))),
        ('ARRAY',
         (('INTEGER', 1500),
          ('INTEGER', 50000),
          ('FLOAT', 6e-06),
          ('INTEGER', 1))))),
      ('OBJECT_DEFINITION',
       'calc_type',
       ('STRING', 'openess_calc'),
       ('OBJECT_DEFINITION',
        'init_time',
        ('INTEGER', 180),
        ('OBJECT_DEFINITION',
         'inset_reels',
         ('BOOL', False),
         ('OBJECT_DEFINITION',
          'margins',
          ('OBJECT',
           ('OBJECT_DEFINITION',
            'top',
            ('INTEGER', 0),
            ('OBJECT_DEFINITION',
             'left',
             ('INTEGER', 0),
             ('OBJECT_DEFINITION',
              'right',
              ('INTEGER', 0),
              ('OBJECT_DEFINITION', 'bottom', ('INTEGER', 0)))))),
          ('OBJECT_DEFINITION',
           'max_parallel_reels',
           ('INTEGER', 100),
           ('OBJECT_DEFINITION',
            'openess',
            ('INTEGER', 3200),
            ('OBJECT_DEFINITION',
             'produtivity',
             ('FLOAT', 11111.12),
             ('OBJECT_DEFINITION',
              'space_between_reels',
              ('INTEGER', 100),
              ('OBJECT_DEFINITION', 'time_cost', ('INTEGER', 0))))))))))))),)),
 ('OBJECT',
  ('OBJECT_DEFINITION',
   'generations',
   ('INTEGER', 300),
   ('OBJECT_DEFINITION',
    'max_stablement',
    ('INTEGER', 30),
    ('OBJECT_DEFINITION', 'population', ('INTEGER', 10))))),
 ('OBJECT',
  ('OBJECT_DEFINITION',
   'consider_amendments_number',
   ('BOOL', True),
   ('OBJECT_DEFINITION',
    'consider_bins_number',
    ('BOOL', False),
    ('OBJECT_DEFINITION',
     'horizontal_cut',
     ('BOOL', True),
     ('OBJECT_DEFINITION',
      'infinite_height',
      ('BOOL', False),
      ('OBJECT_DEFINITION',
       'minimum_cut',
       ('INTEGER', 1000),
       ('OBJECT_DEFINITION',
        'overwrite_itens_amendments_configurations',
        ('BOOL', False),
        ('OBJECT_DEFINITION',
         'printed_amendment',
         ('BOOL', True),
         ('OBJECT_DEFINITION',
          'reuse_bins',
          ('BOOL', True),
          ('OBJECT_DEFINITION',
           'same_supplier',
           ('BOOL', False),
           ('OBJECT_DEFINITION', 'vertical_cut', ('BOOL', True))))))))))))))

    def test_EXIST_FUNCTION(self):
        result = parser.parse('''
                              existe(novo_valor)
                              ''')
        self.assertEqual(result, ('EXISTS_FUNCTION', 'novo_valor'))

    def test_CHECKLIST(self):
        result = parser.parse('''
                                      checklist{"testando_valor"}
                                      ''')
        self.assertEqual(result, ('CHECKLIST', 'testando_valor'))

    def test_CHECKLIST_2(self):
        result = parser.parse('''
                                      checklist{"testando_valor"} + checklist{"testando_valor_2"}
                                      ''')
        self.assertEqual(result, ('PLUS', ('CHECKLIST', 'testando_valor'), ('CHECKLIST', 'testando_valor_2')))
