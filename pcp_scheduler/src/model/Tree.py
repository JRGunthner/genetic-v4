# coding: utf-8

import random


class Node:
    def __init__(self, resource, children):
        self.data = resource
        self.children = children


def find_allocations(tasks):
    """
    Retorna uma lista com várias formas de alocação de recursos para as taferas passadas como
    parâmetro.
    Cada índice de uma solução corresponde a o indice da tarefa que usará aquele recurso
    Por exemplo: se tasks é igual a [t1,t2,t3,t4] e o retorno desta função é [[r3,r9,r1,r5]]
    Siginifica que o recurso r3 pode ser alocado para t1, r9 para t2 e assim successivamente
    :param tasks: lista de tarefas na ordem em que elas terão direito a escolher um recurso
    :return:
    """
    solutions = []
    roots = build_graph(tasks, 0)
    for root in roots:
        find_possible_allocations(root, [], solutions, len(tasks))

    return solutions


def build_graph(tasks, pos):
    """
    Constroi o grafo de ordem em que os recursos serão alocados para
    as tasks. Essa ordem é definida pela ordenação das tasks na lista e tarefas
    passada como parâmetro. Ou seja, a task na raiz escolhe primeiro, as sucessoras dela depois
    e assim por diante
    :param tasks: tarefas na ordem que escolherão os recursos que desejam
    :param pos: posição da tarefa que está tendo seus sucessores definidos
    :return: a lista de nós roots
    """

    if pos == len(tasks)-1:
        nodes = []
        for r in tasks[pos].resources:
            n = Node(r, [])
            nodes.append(n)
        return nodes
    else:
        all_children = build_graph(tasks, pos+1)
        nodes = []
        for resource in tasks[pos].resources:
            my_children = [child for child in all_children if child.data is not resource]
            if len(my_children) > 0:
                node = Node(resource, my_children)
                nodes.append(node)
        return nodes


def find_possible_allocations(node, choosen, solutions, size):
    """
    Encontra todas as possíveis ordens de alocação dos recursos
    :param node: nó raiz do grafo de orde de alocação das tarefas
    :param choosen: resources já escolhidos até o momento
    :param solutions: lista de todas as formas de alocação
    :param size: tamanho que deve ser uma forma de alocação
    :return:
    """
    current_choosen = choosen[::]
    if node.data not in current_choosen:
        current_choosen.append(node.data)

    if len(node.children) == 0:
        if len(current_choosen) == size: solutions.append(current_choosen)
        return
    else:
        random.shuffle(node.children)
        for child in node.children:
            if child.data not in current_choosen:
                find_possible_allocations(child, current_choosen, solutions, size)
