#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import traceback
import numpy
from functools import wraps
from pint import UnitRegistry, UndefinedUnitError, DimensionalityError
from budget_calculator.src.exceptions.Exceptions import HPLExecutionException
from hpl.engine.error_codes import UserDefinedError
from hpl.engine.subproperty_engine.subproperty_engine import select_subproperty
from hpl.exceptions.Exceptions import TokenizerException, ParserException
from hpl.parser.hplparser import parser
from hpl.serializer import HPLSerializer
from simulator.hold_simulator import HoldSimulator
from simulator.serializer import Serializer
from hpl.engine import error_codes
from utils.dictionary import get_dict_key_by_index, get_dict_value_by_index
import hpl.engine.symboltable as symboltable

ur = UnitRegistry()
Q_ = ur.Quantity
logging.basicConfig(
    level=logging.DEBUG,
    filename="parselog.txt",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()


def fn_LOAD(program, symbol_table, automap):
    '''
    Formato de nó esperado de while
    ('LOAD', <campos>, <sequência de comandos>, <proximonodo>)
    '''

    return execute_program("10 dm")


def fn_WHILE(program, symbol_table, automap):
    '''
    Formato de nó esperado de while: ('WHILE', <condição>, <sequência de comandos>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    returned = None
    while execute_program(program[1], symbol_table, automap):
        returned = execute_program(program[2], symbol_table, automap)
    if returned == None and len(program) == 4:
        return execute_program(program[3], symbol_table, automap)


def fn_DECLARING(program, symbol_table, automap):
    '''
    Formato de nó esperado de declaração
    ('DECLARING', <tipo>, <nomedavariavel>, <valordavariavel>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    if program[3] is not None:
        symboltable.addSymbolWithValue(program[2],
                                       program[1],
                                       execute_program(program[3], symbol_table, automap),
                                       symbol_table)
    else:
        symboltable.addSymbolDefaultValue(program[2],
                                          program[1],
                                          symbol_table)
    if len(program) == 5:
        return execute_program(program[4], symbol_table, automap)
    else:
        return None


def fn_BOOL(program, symbol_table, automap):
    '''
    Formato de nó esperado de um booleano
    ('BOOL', <valorbooleano>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return program[1]


def fn_INTEGER(program, symbol_table, automap):
    '''
    Formato de nó esperado de um inteiro: ('INTEGER', <valorinteiro>)
    :param program:
    :param symbol_table:
    :return:
    '''
    if len(program) > 2 and program[1] == '-':
        return -program[2]
    return program[1]


def fn_STRING(program, symbol_table, automap):
    '''
    Formato de nó esperado de um inteiro: ('STRING', <valorstring>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return program[1]


def fn_FLOAT(program, symbol_table, automap):
    '''
    Formato de nó esperado de um flutuante: # ('FLOAT', <valorinteiro>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return program[1]


def fn_ARRAY(program, symbol_table, automap):
    '''
    Formato de nó esperado de um array: # ('ARRAY', <listadevalores>)
    :param program:
    :param symbol_table:
    :return:
    '''
    array = []
    for element in program[1]:
        array = array + [execute_program(element, symbol_table, automap)]
    return array


def fn_IDENTIFIER(program, symbol_table, automap):
    '''
    Formato de nó esperado de um identificador: # ('IDENTIFIER', <valoridentificador>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return symboltable.getSymbol(program[1], symbol_table, automap)


def fn_CHECKLIST(program, symbol_table, automap):
    checklists = symboltable.getSymbol('checklists', symbol_table, automap)
    if program[1] in checklists:
        return checklists[program[1]]
    return None


def fn_IF(program, symbol_table, automap):
    '''
    Formato de nó esperado de um if
    ('IF', <expressaobooleana>, <sequencia de comandos - caso true>, <sequencia de comandos - caso false>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    returned = None
    if execute_program(program[1], symbol_table, automap):
        returned = execute_program(program[2], symbol_table, automap)
    elif program[3] is not None:
        returned = execute_program(program[3], symbol_table, automap)
    if returned is None and len(program) == 5:
        return execute_program(program[4], symbol_table, automap)
    else:
        return returned


def fn_ATTRIBUITION(program, symbol_table, automap):
    '''
    Formato de nó esperado de um attribuition: ('ATTRIBUITION', <nomedavariavel>, <expressao>, <proximonodo>)
    :param program:
    :param symbol_table:
    :return:
    '''
    symboltable.updateSymbolWithValue(program[1], execute_program(program[2], symbol_table, automap), symbol_table, automap)
    if len(program) == 4:
        return execute_program(program[3], symbol_table, automap)
    else:
        return None


def fn_ATTRIBUITION_ARRAY(program, symbol_table, automap):
    '''
    Formato de nó esperado de um attribuition: ('ATTRIBUITION_ARRAY', <nomedavariavel>, <expressao>, <indice>)
    :param program:
    :param symbol_table:
    :return:
    '''
    array = symboltable.getSymbol(program[1], symbol_table, automap)
    try:
        indice = execute_program(program[3], symbol_table, automap)
        array[indice] = execute_program(program[2], symbol_table, automap)
    except:
        raise ParserException(
            {
                "error_code": error_codes.CODES["INDEX_OUT_OF_RANGE"],
                "error_value": indice,
                "name_array": program[1],
                "size_array": len(array)
            })
    symboltable.updateSymbolWithValue(program[1], array, symbol_table, automap)

    if len(program) == 5:
        return execute_program(program[4], symbol_table, automap)
    else:
        return None


def fn_GREAT_EQUAL(program, symbol_table, automap):
    '''
    Formato de nó esperado de um great equal : ('GREAT_EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()

    second = get_value(execute_program(program[2], symbol_table, automap))

    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()
    return execute_operation(first, second, "GREAT_EQUAL")


def get_value(value):
    try:
        return Q_(value)
    except Exception as e:
        raise ParserException(
            {
                "error_code": error_codes.CODES["QUANTITY_IS_NOT_VALID"],
                "error_value": value,
            })


def handle_stripe(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args)
        except DimensionalityError as e:
            raise ParserException(
                {
                    "error_code": error_codes.CODES["OPERATION_DIMENSIONALITY_ERROR"],
                    "error_value": str(args[0]),
                    "error_value2": str(args[1]),
                    "operation": str(args[2])
                })
        except UndefinedUnitError as e:
            raise ParserException(
                {
                    "error_code": error_codes.CODES["OPERATION_UNDEFINED_UNIT_ERROR"],
                    "error_value": str(args[0]),
                    "error_value2": str(args[1]),
                    "operation": str(args[2])
                })
        except Exception as e:
            raise ParserException(
                {
                    "error_code": error_codes.CODES["OPERATION_ERROR"],
                    "error_value": str(args[0]),
                    "error_value2": str(args[1]),
                    "operation": str(args[2])
                })

    return decorated


@handle_stripe
def execute_operation(first, second, operation):
    if operation == "LESS":
        return first < second
    if operation == "GREAT":
        return first > second
    if operation == "LESS_EQUAL":
        return first <= second
    if operation == "GREAT_EQUAL":
        return first >= second
    if operation == "PLUS":
        return first + second
    if operation == "MINUS":
        return first - second
    if operation == "EQUAL":
        return first == second
    if operation == "NOT_EQUAL":
        return first != second
    if operation == "TIMES":
        return first * second
    if operation == "DIVIDE":
        return first / second


def fn_LESS(program, symbol_table, automap):
    '''
    Formato de nó esperado de um less: ('LESS', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()

    second = get_value(execute_program(program[2], symbol_table, automap))

    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "LESS")


def fn_GREAT(program, symbol_table, automap):
    '''
    Formato de nó esperado de um great: ('GREAT', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()

    second = get_value(execute_program(program[2], symbol_table, automap))

    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "GREAT")


def fn_LESS_EQUAL(program, symbol_table, automap):
    '''
    Formato de nó esperado de um less equal: ('LESS_EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()

    second = get_value(execute_program(program[2], symbol_table, automap))

    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "LESS_EQUAL")


def fn_NOT_EQUAL(program, symbol_table, automap):
    '''
    Formato de nó esperado de um not equal: ('NOT_EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()

    second = get_value(execute_program(program[2], symbol_table, automap))

    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "NOT_EQUAL")


def fn_EQUAL(program, symbol_table, automap):
    '''
    Formato de nó esperado de um equal: ('EQUAL', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()

    second = get_value(execute_program(program[2], symbol_table, automap))

    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "EQUAL")


def fn_PLUS(program, symbol_table, automap):
    '''
    Formato de nó esperado de um plus: ('PLUS', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()
    second = get_value(execute_program(program[2], symbol_table, automap))
    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "PLUS")


def fn_MINUS(program, symbol_table, automap):
    '''
    Formato de nó esperado de um minus: ('MINUS', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()
    second = get_value(execute_program(program[2], symbol_table, automap))
    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "MINUS")


def fn_TIMES(program, symbol_table, automap):
    '''
    Formato de nó esperado de um times: ('TIMES', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()
    second = get_value(execute_program(program[2], symbol_table, automap))
    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "TIMES")


def fn_DIVIDE(program, symbol_table, automap):
    '''
    Formato de nó esperado de um divide: ('DIVIDE', <primeirovalor>, <segundovalor>)
    :param program:
    :param symbol_table:
    :return:
    '''
    execute_program(program[1], symbol_table, automap)
    first = get_value(execute_program(program[1], symbol_table, automap))
    if first.unitless:
        first = first.magnitude
    else:
        first = first.to_base_units()
    second = get_value(execute_program(program[2], symbol_table, automap))
    if second.unitless:
        second = second.magnitude
    else:
        second = second.to_base_units()

    return execute_operation(first, second, "DIVIDE")


def fn_MEASUREMENT_UNIT_CAST(program, symbol_table, automap):
    '''
    Formato de nó esperado de um divide: ('MEASUREMENT_UNIT_CAST', <primeirovalor>, <unidade>)
    :param program:
    :param symbol_table:
    :return:
    '''
    value = Q_(execute_program(program[1], symbol_table, automap))
    if value.unitless:
        return Q_(value.magnitude, ur[program[2]])
    else:
        return Q_(value).to(ur[program[2]])


def fn_ACCESS_ARRAY(program, symbol_table, automap):
    '''
    Formato de nó esperado de um divide: ('ACCESS_ARRAY', <identificador>, <indice>)
    :param program:
    :param symbol_table:
    :return:
    '''
    value = symboltable.getSymbol(program[1], symbol_table, automap)
    if type(value) == dict:
        return value[execute_program(program[2], symbol_table, automap)]
    else:
        value = Q_(value)
    if value.unitless:
        if (value.magnitude.size > 0):
            item = value.magnitude[execute_program(program[2], symbol_table, automap)]
            if type(item) == dict:
                return item
            if type(item) == numpy.ndarray:
                return item.tolist()
            else:
                return item.item()
        else:
            raise ParserException(
                {
                    "error_code": error_codes.CODES["INDEX_OUT_OF_RANGE"],
                    "error_value": execute_program(program[2], symbol_table, automap),
                    "name_array": program[1],
                    "size_array": len(value.magnitude)
                })
    else:
        return Q_(value[execute_program(program[2], symbol_table, automap)].item()) * value.u


def fn_AND(program, symbol_table, automap):
    '''
    Formato de nó esperado de um AND: ('AND', <operador1>, <operador2>)
    :param program:
    :param symbol_table:
    :return:
    '''
    operator1 = execute_program(program[1], symbol_table, automap)
    operator2 = execute_program(program[2], symbol_table, automap)
    return operator1 and operator2


def fn_OR(program, symbol_table, automap):
    '''
    Formato de nó esperado de um OR: ('OR', <operador1>, <operador2>)
    :param program:
    :param symbol_table:
    :return:
    '''
    operator1 = execute_program(program[1], symbol_table, automap)
    operator2 = execute_program(program[2], symbol_table, automap)
    return operator1 or operator2


def fn_NOT(program, symbol_table, automap):
    '''
    Formato de nó esperado de um NOT: ('NOT', <operador>)
    :param program:
    :param symbol_table:
    :return:
    '''
    operator = execute_program(program[1], symbol_table, automap)
    return not operator


def fn_ACCESS_SUBPROPERTY(program, symbol_table, automap):
    '''
    Formato de nó esperado de um ACCESS_SUBPROPERTY: ('ACCESS_SUBPROPROPERTY', <expression>, <subpropriedade>, <parametros>)
    :param program:
    :param symbol_table:
    :return:
    '''
    obj = execute_program(program[1], symbol_table, automap)
    if len(program) == 4:
        complement = execute_program(program[3], symbol_table, automap)
        return select_subproperty(program[2], obj, complement)
    if len(program) == 5:
        complement = execute_program(program[3], symbol_table, automap)
        select_subproperty(program[2], obj, complement)
        return execute_program(program[4], symbol_table, automap)
    else:
        return select_subproperty(program[2], obj)


def fn_OBJECT(program, symbol_table, automap):
    '''
    Formato de nó esperado de um OBJECT: ('OBJECT', <objectdefinition>)
    :param program:
    :param symbol_table:
    :return:
    '''
    return execute_program(program[1], symbol_table, automap)


def fn_OBJECT_DEFINITION(program, symbol_table, automap):
    '''
    Formato de nó esperado de um OBJECT: ('OBJECT_DEFINITION', <nome da propriedade>, <valor da propriedade>, <outras definições>)
    :param program:
    :param symbol_table:
    :return:
    '''
    my_definition = {}
    my_definition[program[1]] = execute_program(program[2], symbol_table, automap)
    if len(program) == 4:
        other_definitions = execute_program(program[3], symbol_table, automap)
    else:
        other_definitions = {}
    return {**my_definition, **other_definitions}


def fn_PRINT_SIMULATOR_FUNCTION(program, symbol_table, automap):
    '''
    Formato de nó esperado para um PRINT_SIMULATOR_FUNCTION: ('PRINT_SIMULATOR_FUNCTION', <itens>, <máquinas>, <configurações do algoritmo genético>, <restrições>)
    :param program:
    :param symbol_table:
    :return:
    '''
    items = execute_program(program[1], symbol_table, automap)
    convert_quantities_items(items)
    machines = execute_program(program[2], symbol_table, automap)
    convert_quantities_machines(machines)
    genetic_configurations = execute_program(program[3], symbol_table, automap)
    constraints = execute_program(program[4], symbol_table, automap)
    media_remains = execute_program(program[5], symbol_table, automap)
    convert_media_remains(media_remains)
    simulation = HoldSimulator(items, machines, constraints, genetic_configurations, media_remains).simulate()[0]
    return Serializer(simulation, constraints["reuse_bins"], machines[0]["margins"]).get_returned_obj()


def convert_quantities_items(items):
    list_of_indexes_to_convert = [0, 1]

    for item in items:
        for index in list_of_indexes_to_convert:
            item[index] = (Q_(item[index]).to(ur.mm)).magnitude

        item[3] = int(item[3])


def convert_media_remains(media_remains):
    list_of_media_indexes_to_convert = [2, 3, 4, 5]
    list_of_media_measure_indexes_to_convert = [0, 1]
    measure_key_index = 0

    for media_remain in media_remains:
        for media_index in list_of_media_indexes_to_convert:
            media_remain_key = get_dict_key_by_index(media_remain, media_index)
            media_remain[media_remain_key] = (Q_(media_remain[media_remain_key]).to(ur.mm)).magnitude

        measure = get_dict_value_by_index(media_remain, measure_key_index)
        for media_measure_index in list_of_media_measure_indexes_to_convert:
            measure_key = get_dict_key_by_index(measure, media_measure_index)
            measure[measure_key] = (Q_(measure[measure_key]).to(ur.mm)).magnitude


def convert_quantities_machines(machines):
    list_of_indexes_to_convert = [0, 1]

    for machine in machines:
        bins = machine['bins']
        for bin in bins:
            for index in list_of_indexes_to_convert:
                bin[index] = (Q_(bin[index]).to(ur.mm)).magnitude

        keys_length = ['RIP_time', 'init_time']
        for key in keys_length:
            machine[key] = (Q_(machine[key]).to(ur.s)).magnitude

        margins = machine['margins']
        for key in margins:
            margins[key] = (Q_(margins[key]).to(ur.mm)).magnitude

        machine['openess'] = (Q_(machine['openess']).to(ur.mm)).magnitude
        machine['produtivity'] = (Q_(machine['produtivity']).to('mm**2/s')).magnitude
        machine['time_cost'] = (Q_(machine['time_cost']).to('1/s')).magnitude


def fn_EXISTS_FUNCTION(program, symbol_table, automap):
    '''
        Formato de nó esperado para um EXISTS_FUNCTION: ('EXISTS_FUNCTION', <identificador>)
        :param program:
        :param symbol_table:
        :return:
    '''
    return program[1] in symbol_table.keys()


def fn_ADIMENSIONAL_FUNCTION(program, symbol_table, automap):
    '''
        Formato de nó esperado para um ADIMENSIONAL_FUNCTION: ('ADIMENSIONAL', <identificador>)
        :param program:
        :param symbol_table:
        :return:
    '''
    return Q_(execute_program(program[1], symbol_table, automap)).magnitude


def fn_ERROR(program, symbol_table, automap):
    '''
        Formato de nó esperado para um ERROR: ('ERROR', <string>)
        :param program:
        :param symbol_table:
        :return:
    '''
    return UserDefinedError(program[1])


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
    'ADIMENSIONAL': fn_ADIMENSIONAL_FUNCTION,
    'ARRAY': fn_ARRAY,
    'ERROR': fn_ERROR,
    'CHECKLIST': fn_CHECKLIST
}


def execute_program(program, symbol_table, automap):
    return interpreter_functions[program[0]](program, symbol_table, automap)


def interpreter(program, context, automap={}):
    result = parser.parse(program, debug=log)
    return execute_program(result, context, automap)


def hpl_interpreter(input):
    program = input['program']
    context = input.get('context', {})
    automap_variables = input.get('automap', {})

    try:
        parsed = parser.parse(program, debug=log)
        result = execute_program(parsed, context, automap_variables)
        return HPLSerializer.serializer(result)
    except ParserException as e:
        result = {"error_code": e.value['error_code'], "message_error": e.value, "stack": traceback.format_exc()}
        return result
    except TokenizerException as e:
        result = {"error_code": e.value['error_code'], "message_error": e.value, "stack": traceback.format_exc()}
        return result
    except HPLExecutionException as e:
        result = {"error_code": e.value['error_code'], "message_error": e.value, "stack": traceback.format_exc()}
        return result
    except Exception as e:
        trace_ = {"traceback": traceback.format_exc()}
        result = {"error_code": error_codes.CODES["UNEXPECTED"], "message_error": {}, "stack": trace_}
        return result
