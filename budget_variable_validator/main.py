from encoder import encoder

tmp = '''
{
  "__ProductVariableModel__": {
    "declared_variables": [
      "medidas_do_trabalho.descricao",
      "medidas_do_trabalho.largura",
      "medidas_do_trabalho.altura",
      "medidas_do_trabalho.copias"
    ],
    "undeclared_variables": null,
    "post_scripts": [],
    "pre_scripts": [],
    "processes": [
      {
        "__ProcessVariableModel__": {
          "declared_variables": [
            "tabela_de_produtividade.tempo_de_setup",
            "tabela_de_produtividade.numero_de_pessoas_alocadas",
            "sobras_de_midia_por_copia.superior",
            "sobras_de_midia_por_copia.inferior",
            "sobras_de_midia_por_copia.esquerda",
            "sobras_de_midia_por_copia.direita",
            "agrupamento_de_processos.agrupado_por_medida"
          ],
          "undeclared_variables": null,
          "post_scripts": [],
          "pre_scripts": [
            {
              "__HPLScript__": {
                "context_variable": "tabela_de_produtividade",
                "script": "sequência tabela_temporaria = tabela_de_produtividade.tabela_de_produtividade            inteiro tamanho_produtividade = tabela_temporaria.tamanho - 1            inteiro produtividade_atual = 0            objeto propriedades_materia_prima = materia_prima_escolhida.propriedades            enquanto(produtividade_atual menorOuIgual tamanho_produtividade) faz {                               objeto linha_produtividade = tabela_temporaria{produtividade_atual}                               sequência familias_produtividade = linha_produtividade.familia_para_refilar                                se (familias_produtividade.contem(materia_prima_escolhida.familia) e                                    propriedades_materia_prima.espessura menorOuIgual linha_produtividade.espessura_maxima){                                    linha_produtividade{\"tempo_de_setup\"}=tabela_de_produtividade{\"tempo_de_setup\"}                                    linha_produtividade{\"numero_de_pessoas_alocadas\"}=tabela_de_produtividade{\"numero_de_pessoas_alocadas\"}                                    tabela_de_produtividade = linha_produtividade                                }                                produtividade_atual = produtividade_atual + 1                }                 tabela_de_produtividade",
                "language": 0
              }
            }
          ],
          "choose_feedstock_script": {
            "__HPLScript__": {
              "context_variable": "materia_prima_escolhida",
              "script": "se (não existe(materia_prima_escolhida)){                inteiro indice_escolhido = 0                inteiro indice_atual = 0                objeto materias_primas = midia_de_impressao{0}                sequência opcoes_materia_prima = materias_primas.materias_primas                inteiro indice_maximo = opcoes_materia_prima.tamanho - 1                enquanto (indice_atual MenorOuIgual indice_maximo) faz{                    objeto opcao_materia_prima = opcoes_materia_prima{indice_atual}                    objeto mp_escolhida = opcoes_materia_prima{indice_escolhido}                    se (opcao_materia_prima.preco menorOuIgual mp_escolhida.preco){                        indice_escolhido = indice_atual                    }                    indice_atual = indice_atual + 1                } opcoes_materia_prima{indice_escolhido}           }",
              "language": 0
            }
          },
          "ink_cost_script": {},
          "ink_quantity_script": {},
          "ink_quantities_script": {},
          "total_loss_script": {},
          "percent_loss_script": {},
          "print_area_script": {},
          "time_spent_script": {
            "__HPLScript__": {
              "context_variable": "tempo_gasto",
              "script": "inteiro tamanho = medidas_do_trabalho.tamanho - 1               flutuante tempo = 0,0             se (agrupamento_de_processos.agrupado_por_medida) {                 inteiro indice = 0                objeto medida                enquanto (indice menorOuIgual tamanho) faz {                    medida = medidas_do_trabalho{indice}                     tempo = tempo + ((medida.comprimento + medida.largura) * 2 / tabela_de_produtividade.produtividade ) * medida.copias + tabela_de_produtividade.tempo_de_setup                     indice = indice + 1                 }             } senão {                objeto medida = medidas_do_trabalho{indice}                 tempo = tempo + ((medida.comprimento + medida.largura) * 2 / tabela_de_produtividade.tabela_de_produtividade ) * medida.copias + tabela_de_produtividade.tempo_de_setup             }            tempo = (tempo) hr             tempo",
              "language": 0
            }
          },
          "total_time_spent_script": {},
          "feedstock_spent_script": {},
          "total_feedstock_spent_script": {
            "__HPLScript__": {
              "context_variable": "custo_materia_prima",
              "script": "materia_prima_gasta * materia_prima_selecionada.preco",
              "language": 0
            }
          },
          "subtotal_script": {
            "__HPLScript__": {
              "context_variable": "custo_total",
              "script": "custo_tempo + custo_materia_prima",
              "language": 0
            }
          }
        }
      }
    ]
  }
}
'''
data = encoder.deserializer(tmp)
data.validate_variables()