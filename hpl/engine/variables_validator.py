import logging

from hpl.parser.hplparser import parser


def fn_WHILE(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de while: ('WHILE', <condição>, <sequência de comandos>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])

    if len(program) == 4:
        return find_undeclared_variables(declared_variables, undeclared_variables, program[3])
    else:
        return declared_variables, undeclared_variables


def fn_DECLARING(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de declaração
    ('DECLARING', <tipo>, <nomedavariavel>, <valordavariavel>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables.append(program[2])
    if not (program[3] is None):
        declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                             program[3])
    if program[1] == 'OBJECT':
        if not (program[3] is None):
            variables = get_subvariables(program[3][1])
            for v in variables:
                if isinstance(v, tuple) and v[0] == 'IDENTIFIER':
                    declared_variables.append(program[2] + "." + v[0][1])
                else:
                    declared_variables.append(program[2]+"."+v)
    if len(program) == 5:
        return find_undeclared_variables(declared_variables, undeclared_variables, program[4])

    return declared_variables, undeclared_variables

def get_subvariables(program):
    variables = []
    variables.append(program[1])
    if len(program) == 4:
        other_variables = get_subvariables(program[3])
    else:
        other_variables = []
    return variables + other_variables


def fn_BOOL(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um booleano
    ('BOOL', <valorbooleano>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return declared_variables, undeclared_variables


def fn_INTEGER(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um inteiro: ('INTEGER', <valorinteiro>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return declared_variables, undeclared_variables


def fn_STRING(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um inteiro: ('STRING', <valorstring>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return declared_variables, undeclared_variables


def fn_FLOAT(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um flutuante: # ('FLOAT', <valorinteiro>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return declared_variables, undeclared_variables


def fn_ARRAY(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um array: # ('ARRAY', <listadevalores>)
    :param program:
    :param symbol_table:
    :return:
    '''
    for element in program[1]:
        declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables, element)
    return declared_variables, undeclared_variables



def fn_IDENTIFIER(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um identificador: # ('IDENTIFIER', <valoridentificador>)
    :param program:
    :param symbol_table:
    :return:
    '''
    if program[1] not in declared_variables:
        undeclared_variables.append(program[1])
    return declared_variables, undeclared_variables


def fn_IF(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um if
    ('IF', <expressaobooleana>, <sequencia de comandos - caso true>, <sequencia de comandos - caso false>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    if not (program[1] is None):
        declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                             program[1])
    if not (program[2] is None):
        declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                             program[2])
    if not(program[3] is None):
        declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                                 program[3])

    if len(program) == 5:
        return find_undeclared_variables(declared_variables, undeclared_variables, program[4])

    return declared_variables, undeclared_variables


def fn_ATTRIBUITION(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um attribuition: ('ATTRIBUITION', <nomedavariavel>, <expressao>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    if program[1] not in declared_variables:
        undeclared_variables.append(program[1])

    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    if len(program) == 4:
        return find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[3])
    return declared_variables, undeclared_variables


def fn_ATTRIBUITION_ARRAY(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um attribuition: ('ATTRIBUITION_ARRAY', <nomedavariavel>, <expressao>, <indice>, <proximo_nodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    if program[1] not in declared_variables:
        undeclared_variables.append(program[1])

    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[3])

    if program[4] is not None:
        return find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[4])
    return declared_variables, undeclared_variables


def fn_GREAT(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um great : ('GREAT', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_LESS(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um less : ('LESS', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_GREAT_EQUAL(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um great equal : ('GREAT_EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_LESS_EQUAL(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um less equal: ('LESS_EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_NOT_EQUAL(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um not equal: ('NOT_EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_EQUAL(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um equal: ('EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_PLUS(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um plus: ('PLUS', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables



def fn_MINUS(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um minus: ('MINUS', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables



def fn_TIMES(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um times: ('TIMES', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_DIVIDE(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um divide: ('DIVIDE', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables

def fn_MEASUREMENT_UNIT_CAST(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um divide: ('MEASUREMENT_UNIT_CAST', <primeirovalor>, <unidade>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    return declared_variables, undeclared_variables


def fn_ACCESS_ARRAY(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um divide: ('ACCESS_ARRAY', <identificador>, <indice>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    if program[1] not in declared_variables:
        undeclared_variables.append(program[1])

    return declared_variables, undeclared_variables


def fn_AND(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um AND: ('AND', <operador1>, <operador2>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_OR(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um OR: ('OR', <operador1>, <operador2>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[2])
    return declared_variables, undeclared_variables


def fn_NOT(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um NOT: ('NOT', <operador>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables,
                                                                         program[1])
    return declared_variables, undeclared_variables


def fn_ACCESS_SUBPROPERTY(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um ACCESS_SUBPROPERTY: ('ACCESS_SUBPROPROPERTY', <expression>, <subpropriedade>, <parametros>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return find_undeclared_variables(declared_variables, undeclared_variables, program[1])

def fn_OBJECT(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um OBJECT: ('OBJECT', <objectdefinition>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return find_undeclared_variables(declared_variables, undeclared_variables, program[1])



def fn_OBJECT_DEFINITION(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado de um OBJECT: ('OBJECT_DEFINITION', <nome da propriedade>, <valor da propriedade>, <outras definições>)
    :param program:
    :param symbol_table:
    :return:
    '''
    declared_variables, undeclared_variables = find_undeclared_variables(declared_variables, undeclared_variables, program[2])
    if len(program) == 4:
        return find_undeclared_variables(declared_variables, undeclared_variables, program[3])
    return declared_variables, undeclared_variables


def fn_PRINT_SIMULATOR_FUNCTION(declared_variables, undeclared_variables, program):
    '''
    Formato de nó esperado para um PRINT_SIMULATOR_FUNCTION: ('PRINT_SIMULATOR_FUNCTION', <itens>, <máquinas>, <configurações do algoritmo genético>, <restrições>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return declared_variables, undeclared_variables

def fn_EXISTS_FUNCTION(declared_variables, undeclared_variables, program):
    '''
        Formato de nó esperado para um EXISTS_FUNCTION: ('EXISTS_FUNCTION', <identificador>)
        :param program:
        :param symbol_table:
        :return:
    '''
    return declared_variables, undeclared_variables


def fn_ERROR(declared_variables, undeclared_variables, program):
    '''
        Formato de nó esperado para um ERROR: ('ERROR', <string>)
        :param program:
        :param symbol_table:
        :return:
    '''
    return declared_variables, undeclared_variables



interpreter_functions = {
    'DECLARING': fn_DECLARING,
    'BOOL': fn_BOOL,
    'INTEGER': fn_INTEGER,
    'FLOAT': fn_FLOAT,
    'STRING': fn_STRING,
    'OBJECT': fn_OBJECT,
    'OBJECT_DEFINITION': fn_OBJECT_DEFINITION,
    'IDENTIFIER': fn_IDENTIFIER,
    'IF': fn_IF,
    'WHILE': fn_WHILE,
    'ATTRIBUITION': fn_ATTRIBUITION,
    'ATTRIBUITION_ARRAY': fn_ATTRIBUITION_ARRAY,
    'LESS': fn_LESS,
    'LESS_EQUAL': fn_LESS_EQUAL,
    'NOT_EQUAL': fn_NOT_EQUAL,
    'EQUAL': fn_EQUAL,
    'GREAT': fn_GREAT,
    'GREAT_EQUAL': fn_GREAT_EQUAL,
    'AND': fn_AND,
    'OR': fn_OR,
    'NOT': fn_NOT,
    'PLUS': fn_PLUS,
    'TIMES': fn_TIMES,
    'DIVIDE': fn_DIVIDE,
    'MEASUREMENT_UNIT_CAST': fn_MEASUREMENT_UNIT_CAST,
    'ACCESS_ARRAY': fn_ACCESS_ARRAY,
    'ACCESS_SUBPROPERTY': fn_ACCESS_SUBPROPERTY,
    'MINUS': fn_MINUS,
    'PRINT_SIMULATOR_FUNCTION': fn_PRINT_SIMULATOR_FUNCTION,
    'EXISTS_FUNCTION': fn_EXISTS_FUNCTION,
    'ARRAY': fn_ARRAY,
    'ERROR': fn_ERROR
}

def find_undeclared_variables(declared_variables, undeclared_variables, program):
    return interpreter_functions[program[0]](declared_variables, undeclared_variables, program)

def get_external_variables(script, declared_variables):
    undeclared_variables = []
    parsed = parser.parse(script)
    return find_undeclared_variables(declared_variables, undeclared_variables, parsed)