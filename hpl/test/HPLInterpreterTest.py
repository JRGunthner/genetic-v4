import unittest

from hpl.engine.interpreter import hpl_interpreter
from hpl.engine import error_codes


class HPLInterpreterTestCase(unittest.TestCase):

    def test_int_return(self):
        data = {"context": {}, "program": "(10m + 10m)m"}
        result = hpl_interpreter(data)

        self.assertTrue("measurement_unit" in result)
        self.assertTrue("type" in result)
        self.assertTrue("value" in result)
        self.assertEqual(len(result.keys()), 3)
        self.assertTrue(result["value"] == 20)
        self.assertTrue(result["type"] == 'int')
        self.assertTrue(result["measurement_unit"] == 'm')

    def test_error_return(self):
        data = {"context": {}, "program": "(10inexistentMeasurementUnit + 10m)m"}
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["SINTAX_ERROR"])
        self.assertTrue(result["message_error"]["error_value"] == "inexistentMeasurementUnit")

    def test_not_declared_symbol_name(self):
        data = {
            "program": '''flutuante soma 
                          soma = soma + contador 
                          soma
                          ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["SYMBOL_NAME_NOT_FOUND"])
        self.assertTrue(result["message_error"]["error_value"] == "contador")

    def test_type_error_float_string(self):
        data = {
            "program": '''flutuante soma = \"uma string\" soma
                          ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["TYPE_ERROR"])
        self.assertTrue(result["message_error"]["expected_type"] == "flutuante")
        self.assertTrue(result["message_error"]["received_type"] == "texto")
        self.assertTrue(result["message_error"]["error_value"] == "uma string")

    def test_type_error_int_string(self):
        data = {
            "program": '''inteiro soma = "uma string"
                          ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["TYPE_ERROR"])
        self.assertTrue(result["message_error"]["expected_type"] == "inteiro")
        self.assertTrue(result["message_error"]["received_type"] == "texto")
        self.assertTrue(result["message_error"]["error_value"] == "uma string")

    def test_type_error_array_string(self):
        data = {
            "program": '''sequência soma = "uma string"
                          ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["TYPE_ERROR"])
        self.assertTrue(result["message_error"]["expected_type"] == "sequência")
        self.assertTrue(result["message_error"]["received_type"] == "texto")
        self.assertTrue(result["message_error"]["error_value"] == "uma string")

    def test_type_error_string_float(self):
        data = {
            "program": '''texto soma = 44
                          ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["TYPE_ERROR"])
        self.assertTrue(result["message_error"]["expected_type"] == "texto")
        self.assertTrue(result["message_error"]["error_value"]== 44)

    def test_type_float_int(self):
        data = {
            "program": '''flutuante soma = 44
                          soma
                          ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["value"] == 44)

    def test_type_float_int(self):
        data = {
            "program": '''flutuante soma = 44
                          soma
                          ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["value"] == 44)

    def test_array_1(self):
        data = {
            "program": '''sequência teste = [10;20;30] 
                          inteiro contador = 0 
                          flutuante soma 
                          enquanto (contador menorouigual 2) faz { 
                            soma = soma + teste{contador} 
                            contador = contador + 1 
                          } 
                          soma
                          ''',
            "context": {
                "hold_teste": 20
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertTrue(result["value"] == 60)

    def test_array_2(self):
        data = {
            "program": '''
                        sequência teste = [10;20;30] 
                        teste{1} = 50
                        teste 
                       ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "list")
        self.assertTrue(result["value"] == [10, 50, 30])


    def test_array_index_out_of_range(self):
        data = {
            "program": '''
                        sequência teste = [10;20;30] 
                        teste{8} = 50
                        teste 
                       ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["INDEX_OUT_OF_RANGE"])
        self.assertTrue(result["message_error"]["name_array"] == "teste")
        self.assertTrue(result["message_error"]["size_array"] == 3)
        self.assertTrue(result["message_error"]["error_value"] == 8)


    def test_subproperty(self):
        data = {
            "program": '''
                        sequência teste = [10;20;30] 
                        teste.tamanho 
                       ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertTrue(result["value"] == 3)

    def test_subproperty_2(self):
        data = {
            "program": '''
                        sequência teste = [10;20;30] 
                        inteiro tamanho = teste.tamanho - 1
                        flutuante soma
                        enquanto (tamanho maiorouigual 0) faz {
                            soma = soma + teste{tamanho}
                            tamanho = tamanho - 1
                        }
                        soma
                       ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertTrue(result["value"] == 60)

    def test_subproperty_not_found(self):
        data = {
            "program": '''
                        sequência teste = [10;20;30] 
                        teste.subpropriedadeinexistente 
                       ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == error_codes.CODES["SUBPROPERTY_NOT_FOUND"])
        self.assertTrue(result["message_error"]["error_value"] == "subpropriedadeinexistente")

    def test_defining_object(self):
        data = {
            "program": '''
                   {
                        numero1 : "numero 1";
                        numero2 : 2
                   }
                ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "object")
        self.assertEqual(result["value"], {
            "numero1": "numero 1",
            "numero2": 2
        })

    def test_defining_object_and_accessing(self):
        data = {
            "program": '''
                      {
                           numero1 : "numero 1";
                           numero2 : 2
                      }.numero2
                   ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 2)

    def test_object_and_keys(self):
        data = {
            "program": '''
                      objeto teste = {
                           numero1 : "numero 1";
                           numero2 : 2
                      }
                      teste.chaves
                   ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "list")
        self.assertEqual(result["value"], ['numero1', 'numero2'])

    def test_object_with_expressions(self):
        data = {
            "program": '''
                      inteiro x = 10
                      objeto teste = {
                           numero1 : x * 10;
                           numero2 : 2
                      }
                      teste.numero1
                   ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 100)

    def test_expression_minus(self):
        data = {
            "program": '''
                      inteiro x = 10
                      inteiro numero1 = x - 1
                      numero1
                   ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 9)

    def test_other_expression_minus(self):
        data = {
            "program": '''
                         inteiro x = (-3) + 4
                         x
                      ''',
            "context": {}
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 1)

    def test_object_within_context(self):
        data = {
            "program": '''
                      objeto novo_objeto = {
                        numero1: 100;
                        numero2: 200;
                        numero3: 500
                      }
                      sequência chaves = novo_objeto.chaves
                      inteiro tamanho_array = chaves.tamanho - 1
                      inteiro contador = 0
                      flutuante soma
                      texto novo_texto
                      enquanto (contador menorouigual tamanho_array) faz {
                        novo_texto = chaves{contador}
                        soma = soma + novo_objeto{novo_texto}
                        contador = contador + 1
                      }
                      soma
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(result["value"], 800)

    def test_round_expression(self):
        data = {
            "program": '''
                      flutuante teste = 222,66
                      teste.arredonda
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(result["value"], 223)

    def test_round_expression_2(self):
        data = {
            "program": '''
                      flutuante teste = 222,6656
                      teste.arredonda(2)
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(result["value"], 222.67)

    def test_truncate_expression(self):
        data = {
            "program": '''
                      flutuante teste = 222,66
                      teste.truncar
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(result["value"], 222)

    def test_truncate_expression_2(self):
        data = {
            "program": '''
                      flutuante teste = 222,6656
                      teste.truncar(2)
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(result["value"], 222.66)

    def test_tail_expression(self):
        data = {
            "program": '''
                      flutuante teste = 222,66
                      teste.teto
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 223)

    def test_ceil_expression(self):
        data = {
            "program": '''
                      flutuante teste = 222,66
                      teste.piso
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 222)

    def test_contains_expression(self):
        data = {
            "program": '''
                      sequência teste = [ "teste1"; "teste2"]
                      teste.contem("teste1")
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "bool")
        self.assertEqual(result["value"], "verdadeiro")

    def test_script_to__recover_object_without_comercial_id(self):
        data = {
            "program": '''
                      objeto novo_objeto = novo_objeto
                      sequência chaves = novo_objeto.chaves
                      booleano hascomercial = chaves.contem(["comercial_id"])
                      se (hascomercial) {
                      inteiro comercial = novo_objeto.comercial_id
                      } senão {
                      inteiro comercial = -1}
                      comercial
                   ''',
            "context": {
                'novo_objeto' : {
                    'preco': 20.0,
                    'id': '5c3344a6bdc16a1a28639600',
                    'option_id': 1,
                    'familia': [
                        "adesivos",
                        "brancos"
                    ]
                }
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], -1)

    def test_script_to__recover_object_with_comercial_id(self):
        data = {
            "program": '''
                      objeto novo_objeto = novo_objeto
                      sequência chaves = novo_objeto.chaves
                      booleano hascomercial = chaves.contem(["comercial_id"])
                      se (hascomercial) {
                      inteiro comercial = novo_objeto.comercial_id
                      } senão {
                      inteiro comercial = -1}
                      comercial
                   ''',
            "context": {
                'novo_objeto' : {
                    'preco': 20.0,
                    'comercial_id': 23,
                    'id': '5c3344a6bdc16a1a28639600',
                    'option_id': 1,
                    'familia': [
                        "adesivos",
                        "brancos"
                    ]
                }
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 23)

    def test_contains_expression_2(self):
        data = {
            "program": '''
                      sequência teste = [ "teste1"; "teste2"]
                      teste.contem(["teste1"])
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "bool")
        self.assertEqual(result["value"], "verdadeiro")

    def test_contains_expression_3(self):
        data = {
            "program": '''
                      sequência teste = [ "teste1"; "teste2"]
                      teste.contem(["teste2";"teste1"])
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "bool")
        self.assertEqual(result["value"], "verdadeiro")

    def test_contains_expression_4(self):
        data = {
            "program": '''
                      sequência teste = [ "teste1"; "teste2"]
                      teste.contem("teste3")
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "bool")
        self.assertEqual(result["value"], "falso")

    def test_contains_expression_5(self):
        data = {
            "program": '''
                      sequência teste = [ "TesTe1"; "teStE2"]
                      teste.contem("teste1")
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "bool")
        self.assertEqual(result["value"], "verdadeiro")

    def test_float_with_measurement_unit(self):
        data = {
            "program": '''
                         flutuante teste1
                         teste1 = 30m/hr
                         teste1
                      ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertEqual(result["value"], 30)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["measurement_unit"], "m / hr")


    def test_float_with_measurement_unit_1(self):
        data = {
            "program": '''
                      flutuante teste1
                      teste1 = 5min
                      teste1
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertEqual(result["value"], 5)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["measurement_unit"], "min")

    def test_float_with_measurement_unit_1(self):
        data = {
            "program": '''
                      flutuante teste1
                      teste1 = 5,85min
                      teste1
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertEqual(result["value"], 5.85)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(result["measurement_unit"], "min")

    def test_imcompatible_types(self):
        data = {
            "program": '''
                      flutuante teste1
                      teste1 = "new string"
                      teste1
                   ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == 992)
        self.assertEqual(result['message_error']["expected_type"], "flutuante")
        self.assertEqual(result['message_error']["error_value"], "new string")
        self.assertEqual(result['message_error']["expected_type"], "flutuante")


    def test_throw_error(self):
        data = {
            "program": '''
                        lança erro ("Não deveria conter este valor")
                       ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["error_code"] == 998)
        self.assertEqual(result["message_error"]["error_value"], "Não deveria conter este valor")

    def test_divide_espression(self):
        data = {
            "program": '''
                            flutuante resultado = 5000 / 50 
                            resultado
                      ''',
            "context": {
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == 'float')
        self.assertEqual(result["value"], 100.0)
        self.assertEqual(result["value"], 100.0)

    # def test_print_simulator(self):
    #     data = {
    #         "program": '''
    #         sequência medidas = [[300; 400; "1"; 20; 100; "right"; "bottom"];
	# 	                         [400; 500; "2"; 20; 100; "right"; "bottom"];
    #                              [100; 900; "2"; 20; 100; "right"; "bottom"];
    #                              [780; 610; "2"; 20; 100; "right"; "bottom"];
    #                              [450; 330; "2"; 20; 100; "right"; "bottom"]]
    #
    #         sequência maquinas = [{
    #                                     RIP_time: 180;
    #                                     bins: [[3200; 50000; 0,000006; 0]; [1500; 50000; 0,000006; 1]];
    #                                     calc_type: "openess_calc";
    #                                     init_time: 180;
    #                                     inset_reels: falso;
    #                                     margins: {
    #                                        top: 0;
    #                                        left: 0;
    #                                        right: 0;
    #                                        bottom: 0
    #                                     };
    #                                     max_parallel_reels: 100;
    #                                     openess: 3200;
    #                                     produtivity: 11111,12;
    #                                     space_between_reels: 100;
    #                                     time_cost:0
    #                              }]
    #
    #         objeto informacoes_geneticas = {
    #                                          generations : 300;
    #                                          max_stablement: 10;
    #                                          population: 10
    #                                        }
    #
    #         objeto restricoes = {
    #                                 consider_amendments_number: verdadeiro;
    #                                 consider_bins_number: falso;
    #                                 horizontal_cut: verdadeiro;
    #                                 infinite_height: falso;
    #                                 minimum_cut: 1000;
    #                                 overwrite_itens_amendments_configurations: falso;
    #                                 printed_amendment: verdadeiro;
    #                                 reuse_bins: verdadeiro;
    #                                 same_supplier: falso;
    #                                 vertical_cut: verdadeiro
    #                             }
    #
    #         simulador_impressao(medidas;maquinas;informacoes_geneticas; restricoes)
    #         ''',
    #         "context": {}
    #     }
    #     result = hpl_interpreter(data)
    #     self.assertTrue(result["type"] == "object")
    #     self.assertLess(result["value"]["percent"], 0.07)

    def test_script_0(self):
        data = {
            "program": '''
            sequência tabela_temporaria = tabela_de_produtividade.tabela_de_produtividade
            inteiro tamanho_produtividade = tabela_temporaria.tamanho - 1
            inteiro produtividade_atual = 0
            objeto propriedades_materia_prima = materia_prima_escolhida.propriedades
            enquanto(produtividade_atual menorOuIgual tamanho_produtividade) faz {
                               objeto linha_produtividade = tabela_temporaria{produtividade_atual}
                               sequência familias_produtividade = linha_produtividade.familia_para_refilar
                                se (familias_produtividade.contem(materia_prima_escolhida.familia) e
                                    propriedades_materia_prima.espessura menorOuIgual linha_produtividade.espessura_maxima){
                                    linha_produtividade{"tempo_de_setup"}=tabela_de_produtividade{"tempo_de_setup"}
                                    linha_produtividade{"numero_de_pessoas_alocadas"}=tabela_de_produtividade{"numero_de_pessoas_alocadas"}
                                    tabela_de_produtividade = linha_produtividade
                                }
                                produtividade_atual = produtividade_atual + 1
                } 
                tabela_de_produtividade
            ''',
            "context": {
                '__Context__': {},
                'medidas_do_trabalho': [
                    {'largura': '100.0 cm', 'comprimento': '200.0 cm', 'copias': 1.0},
                    {'largura': '150.0 cm', 'comprimento': '800.0 cm', 'copias': 1.0}
                ],
                'midia_de_impressao': [],
                'tabela_de_produtividade': {
                    'tabela_de_produtividade': [
                        {'espessura_maxima': '80.0 cm', 'produtividade': '45.0 m/hr',
                         'familia_para_refilar': ['Adesivos']},
                        {'espessura_maxima': '60.0 cm', 'produtividade': '60.0 m/hr',
                         'familia_para_refilar': ['Adesivos']},
                        {'espessura_maxima': '80.0 cm', 'produtividade': '30.0 m/hr',
                         'familia_para_refilar': ['Chapa']}],
                    'produtividade': None,
                    'espessura_maxima': None,
                    'familia_para_refilar': None,
                    'tempo_de_setup': '100 s',
                    'numero_de_pessoas_alocadas': 1
                },
                'sobras_de_midia_por_copia': {
                    'descricao': 'Refile manual',
                    'superior': 5.0,
                    'inferior': 5.0,
                    'esquerda': 5.0,
                    'direita': 5.0
                },
                'materia_prima_escolhida': {
                    'familia': ['Adesivos'],
                    'preco': 5.0,
                    'opcoes': {
                        'largura': 400,
                        'comprimento': 500
                    },
                    'propriedades': {
                        'espessura': '0.75 m'
                    },
                    'campos_customizados': {}
                },
                'agrupamento_de_processos': {
                    'agrupado_por_medida': True
                },
                'cost_center': 50.0
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "object")
        self.assertTrue("tempo_de_setup" in result["value"])
        self.assertTrue(result["value"]["tempo_de_setup"] == '100 s')
        self.assertTrue("numero_de_pessoas_alocadas" in result["value"])
        self.assertTrue("produtividade" in result["value"])

    def test_script_1(self):
        data = {
            "program": '''
            sequência tabela_temporaria = tabela_de_produtividade.tabela_de_produtividade
            inteiro tamanho_produtividade = tabela_temporaria.tamanho - 1
            inteiro produtividade_atual = 0
            objeto propriedades_materia_prima = materia_prima_escolhida.propriedades
            
            enquanto(produtividade_atual menorOuIgual tamanho_produtividade) faz {
                   objeto linha_produtividade = tabela_temporaria{produtividade_atual}
                   sequência familias_produtividade = linha_produtividade.familia_para_refilar
                   se (familias_produtividade.contem(materia_prima_escolhida.familia) e 
                       propriedades_materia_prima.espessura menorOuIgual linha_produtividade.espessura_maxima){
                        linha_produtividade{"tempo_de_setup"} = tabela_de_produtividade{"tempo_de_setup"}
                        linha_produtividade{"numero_de_pessoas_alocadas"} = tabela_de_produtividade{"numero_de_pessoas_alocadas"}
                        tabela_de_produtividade = linha_produtividade
               
                   }
                   produtividade_atual = produtividade_atual + 1
            }
            
            inteiro tamanho = medidas_do_trabalho.tamanho - 1   
            flutuante tempo = 0,0 
            se (agrupamento_de_processos.agrupado_por_medida) { 
                inteiro indice = 0
                objeto medida
                enquanto (indice menorOuIgual tamanho) faz { 
                    medida = medidas_do_trabalho{indice} 
                    tempo = tempo + ((medida.comprimento + medida.largura) * 2 / tabela_de_produtividade.produtividade ) * medida.copias + tabela_de_produtividade.tempo_de_setup 
                    indice = indice + 1 
                } 
            } senão {
                objeto medida = medidas_do_trabalho{indice} 
                tempo = tempo + ((medida.comprimento + medida.largura) * 2 / tabela_de_produtividade.tabela_de_produtividade ) * medida.copias + tabela_de_produtividade.tempo_de_setup 
            }
            tempo = (tempo) hr 
            tempo
            ''',
            "context": {
                '__Context__': {},
                'medidas_do_trabalho': [
                    {'largura': '100.0 cm', 'comprimento': '200.0 cm', 'copias': 1.0},
                    {'largura': '150.0 cm', 'comprimento': '800.0 cm', 'copias': 1.0}
                ],
                'midia_de_impressao': [],
                'tabela_de_produtividade': {
                    'tabela_de_produtividade': [
                        {'espessura_maxima': '80.0 cm', 'produtividade': '45.0 m/hr', 'familia_para_refilar': ['Adesivos']},
                        {'espessura_maxima': '60.0 cm', 'produtividade': '60.0 m/hr', 'familia_para_refilar': ['Adesivos']},
                        {'espessura_maxima': '80.0 cm', 'produtividade': '30.0 m/hr', 'familia_para_refilar': ['Chapa']}],
                    'produtividade': '45.0 m/hr',
                    'espessura_maxima': 80.0,
                    'familia_para_refilar': ['Adesivos'],
                    'tempo_de_setup': '100 s',
                    'numero_de_pessoas_alocadas': 1
                },
                'sobras_de_midia_por_copia': {
                    'descricao': 'Refile manual',
                    'superior': 5.0,
                    'inferior': 5.0,
                    'esquerda': 5.0,
                    'direita': 5.0
                },
                'materia_prima_escolhida': {
                    'familia': ['Adesivos'],
                    'preco': 5.0,
                    'opcoes': {
                        'largura': 400,
                        'comprimento': 500
                    },
                    'propriedades': {
                        'espessura': '0.75 m'
                    },
                    'campos_customizados': {}
                },
                'agrupamento_de_processos': {
                    'agrupado_por_medida': True
                },
                'cost_center': 50.0
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(round(result["value"], ndigits=2), 0.61)
        self.assertEqual(result["measurement_unit"], 'hr')

    def test_script_2(self):
        data = {
            "program": '''
            tempo_gasto * tabela_de_produtividade.numero_de_pessoas_alocadas * centro_de_custo
            ''',
            "context": {
                           '__Context__': {},
                           'medidas_do_trabalho': [
                               {'largura': '0.1 m', 'comprimento': '0.2 m', 'copias': 1.0},
                               {'largura': '0.15 m', 'comprimento': '0.8 m', 'copias': 1.0}],
                           'midia_de_impressao': [],
                           'tabela_de_produtividade': {
                               'tabela_de_produtividade': [
                                   {'espessura_maxima': '80.0 cm', 'produtividade': '45.0 m/hr', 'familia_para_refilar': ['Adesivos']}

                               ],
                               'produtividade': None,
                               'espessura_maxima': None,
                               'familia_para_refilar': None,
                               'tempo_de_setup': '100.0 s',
                               'numero_de_pessoas_alocadas': 1
                           },
                           'sobras_de_midia_por_copia': {
                               'descricao': 'Refile manual',
                               'superior': 5.0,
                               'inferior': 5.0,
                               'esquerda': 5.0,
                               'direita': 5.0
                           },
                           'agrupamento_de_processos': {
                               'agrupado_por_medida': True
                           },
                           'centro_de_custo': '50.0 1/hr',
                           'tamanho': 1,
                           'tempo': '0.1111111111111111 hr',
                           'indice': 2,
                            'medida': {
                                'largura': '0.15 m',
                                'comprimento': '0.8 m',
                                'copias': 1.0
                            },
                            'tempo_gasto': '0.1111111111111111 hr'
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertEqual(round(result["value"], ndigits=2), 5.56)

    def test_script_3(self):
        data = {
            "program": '''
            se (não existe(materia_prima_escolhida)){
                inteiro indice_escolhido = 0
                inteiro indice_atual = 0
                objeto materias_primas = midia_de_impressao{0}
                sequência opcoes_materia_prima = materias_primas.materias_primas
                inteiro indice_maximo = opcoes_materia_prima.tamanho - 1
                enquanto (indice_atual MenorOuIgual indice_maximo) faz{
                    objeto opcao_materia_prima = opcoes_materia_prima{indice_atual}
                    objeto mp_escolhida = opcoes_materia_prima{indice_escolhido}
                    se (opcao_materia_prima.preco menorOuIgual mp_escolhida.preco){
                        indice_escolhido = indice_atual
                    }
                    indice_atual = indice_atual + 1
                }
                
                opcoes_materia_prima{indice_escolhido}
            }
            ''',
            "context": {
                  "medidas_do_trabalho": [
                    {
                      "largura": 100.0,
                      "comprimento": 200.0,
                      "liner": 1.0
                    },
                    {
                      "largura": 150.0,
                      "comprimento": 800.0,
                      "liner": 2.0
                    }
                  ],
                  "midia_de_impressao": [
                    {
                      "materias_primas": [
                         {
                              "id": 3,
                              "preco": 15.0,
                              "opcoes": {
                                  "largura": 400,
                                  "comprimento": 500
                              },
                              "propriedades": {},
                              "campos_customizados": {}
                        },
                        {
                          "id": 1,
                          "preco": 5.0,
                          "opcoes": {
                            "largura": 400,
                            "comprimento": 500
                          },
                          "propriedades": {},
                          "campos_customizados": {}
                        },
                        {
                              "id": 2,
                              "preco": 10.0,
                              "opcoes": {
                                  "largura": 400,
                                  "comprimento": 500
                              },
                              "propriedades": {},
                              "campos_customizados": {}
                        }
                      ]
                    }
                  ]
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "object")
        self.assertEqual(result["value"]["id"], 1)

    def test_script_4(self):
        script = {
            "program" : '''
                sequência tabela_temporaria = tabela_de_produtividade.tabela_de_produtividade            
                inteiro tamanho_produtividade = tabela_temporaria.tamanho - 1            
                inteiro produtividade_atual = 0            
                objeto propriedades_materia_prima = materia_prima_escolhida.propriedades            
                enquanto(produtividade_atual menorOuIgual tamanho_produtividade) faz {                               
                    objeto linha_produtividade = tabela_temporaria{produtividade_atual}                               
                    sequência familias_produtividade = linha_produtividade.familia_para_refilar                                
                    se (familias_produtividade.contem(materia_prima_escolhida.familia) e                                    
                        propriedades_materia_prima.espessura menorOuIgual linha_produtividade.espessura_maxima){                                    
                            linha_produtividade{\"tempo_de_setup\"}=tabela_de_produtividade{\"tempo_de_setup\"}                                    
                            linha_produtividade{\"numero_de_pessoas_alocadas\"}=tabela_de_produtividade{\"numero_de_pessoas_alocadas\"}                                    
                            tabela_de_produtividade = linha_produtividade                                }                                
                            produtividade_atual = produtividade_atual + 1                
                    }                 
                tabela_de_produtividade''',
            "context": {
                'tabela_de_produtividade': {
                    'tabela_de_produtividade': [
                        {
                            'espessura_maxima': '100mm',
                            'produtividade': '30m/hr',
                            'familia_para_refilar': ['Adesivos', 'Brancos']
                        }
                    ],
                    'espessura_maxima': None,
                    'tempo_de_setup': '5min',
                    'numero_de_pessoas_alocadas': 4.0
                },
                'sobras_de_midia_por_copia': {
                    'descricao': 'aksna',
                    'superior': '1m',
                    'inferior': '1m',
                    'esquerda': '1m',
                    'direita': '1m'
                },
                'agrupamento_de_processos': {
                    'agrupado_por_medida': 'False'
                },
                'largura': None,
                'comprimento': None,
                'familia_para_refilar': None,
                'espessura_maxima': None,
                'produtividade': None,
                'tempo_de_setup': None,
                'numero_de_pessoas_alocadas': None,
                'descricao': None,
                'superior': None,
                'inferior': None,
                'esquerda': None,
                'direita': None,
                '': None,
                'materias_primas': {
                    'materias_primas': [
                        {
                            'preco': 10.0,
                            'id': '5b7c098ca871972568b93bdd',
                            'option_id': 15,
                            'familia': ['adesivos', 'brancos'],
                            'opcoes': {
                                'largura': '20m',
                                'comprimento': '30m'
                            },
                            'propriedades': {
                                'liner': 'm',
                                'espessura': '10mm',
                                'durabilidade': 'm'
                            },
                            'campos_customizados': {}
                        }
                    ]
                },
                'copias': None,
                'centro_de_custos': '333,33 1/hr',
                'medidas_do_trabalho': [
                    {
                        'largura': '12m',
                        'comprimento': '20m',
                        'copias': 15.0,
                        'descricao': 'x'
                    },
                    {
                        'largura': '15m',
                        'comprimento': '20m',
                        'copias': 10.0,
                        'descricao': 'y'
                    }
                ],
                'midia_de_impressao': [
                    {
                        'materias_primas': [
                            {
                                'preco': 10.0,
                                'id': '5b7c098ca871972568b93bdd',
                                'option_id': 15,
                                'familia': ['adesivos', 'brancos'],
                                'opcoes': {
                                    'largura': '20m',
                                    'comprimento': '30m'
                                },
                                'propriedades': {
                                    'liner': 'm',
                                    'espessura': '10mm',
                                    'durabilidade': 'm'
                                },
                                'campos_customizados': {}
                            }
                        ]
                    }
                ],
                'indice_escolhido': 0,
                'indice_atual': 1,
                'opcoes_materia_prima': [{'preco': 10.0, 'id': '5b7c098ca871972568b93bdd', 'option_id': 15, 'familia': ['adesivos', 'brancos'], 'opcoes': {'largura': '20m', 'comprimento': '30m'}, 'propriedades': {'liner': 'm', 'espessura': '10mm', 'durabilidade': 'm'}, 'campos_customizados': {}}],
                'indice_maximo': 0,
                'opcao_materia_prima': {'preco': 10.0, 'id': '5b7c098ca871972568b93bdd', 'option_id': 15, 'familia': ['adesivos', 'brancos'], 'opcoes': {'largura': '20m', 'comprimento': '30m'}, 'propriedades': {'liner': 'm', 'espessura': '10mm', 'durabilidade': 'm'}, 'campos_customizados': {}},
                'mp_escolhida': {'preco': 10.0, 'id': '5b7c098ca871972568b93bdd', 'option_id': 15, 'familia': ['adesivos', 'brancos'], 'opcoes': {'largura': '20m', 'comprimento': '30m'}, 'propriedades': {'liner': 'm', 'espessura': '10mm', 'durabilidade': 'm'}, 'campos_customizados': {}},
                'materia_prima_escolhida': {
                    'preco': 10.0,
                    'id': '5b7c098ca871972568b93bdd',
                    'option_id': 15,
                    'familia': ['adesivos', 'brancos'],
                    'opcoes': {'largura': '20m', 'comprimento': '30m'},
                    'propriedades': {
                        'liner': 'm',
                        'espessura': '10mm',
                        'durabilidade': 'm'
                    },
                    'campos_customizados': {}
                },
                'tabela_temporaria': [{'espessura_maxima': '100mm', 'produtividade': '30m/hr', 'familia_para_refilar': ['Adesivos', 'Brancos']}],
                'tamanho_produtividade': 0,
                'produtividade_atual': 1,
                'propriedades_materia_prima': {'liner': 'm', 'espessura': '10mm', 'durabilidade': 'm'},
                'linha_produtividade': {'espessura_maxima': '100mm', 'produtividade': '30m/hr', 'familia_para_refilar': ['Adesivos', 'Brancos']},
                'familias_produtividade': ['Adesivos', 'Brancos']
            }
        }
        result = hpl_interpreter(script)
        self.assertTrue(result["type"] == "object")
        self.assertEqual(result["value"]["produtividade"], "30m/hr")


    def test_exists_1(self):
        data = {
            "program": '''
                existe(teste_verdadeiro)
            ''',
            "context": {
                "teste_verdadeiro": '10cm'
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "bool")
        self.assertEqual(result["value"], "verdadeiro")

    def test_exists_2(self):
        data = {
            "program": '''
                existe(teste_verdadeiro2)
            ''',
            "context": {
                "teste_verdadeiro": '10cm'
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "bool")
        self.assertEqual(result["value"], "falso")

    def test_checklists_1(self):
        data = {
            "program": '''
                checklist{"Qual a durabilidade do trabalho?"}
            ''',
            "context": {
                "checklists": {
                    "Qual a durabilidade do trabalho?": 5
                }
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "int")
        self.assertEqual(result["value"], 5)

    def test_checklists_2(self):
        data = {
            "program": '''
                checklist{"Qual a espessura necessária?"} * checklist{"Qual o comprimento necessário?"} * checklist{"Qual a largura necessária?"}
            ''',
            "context": {
                "checklists": {
                    "Qual a espessura necessária?": '5 mm',
                    "Qual o comprimento necessário?": '10m',
                    "Qual a largura necessária?": '50m'
                }
            }
        }
        result = hpl_interpreter(data)
        self.assertTrue(result["type"] == "float")
        self.assertTrue(result["measurement_unit"] == 'm ** 3')
        self.assertEqual(result["value"], 2.5)


if __name__ == '__main__':
    unittest.main()
