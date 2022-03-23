#! /usr/bin/env python
# -*- coding: utf-8 -*-
from hpl.exceptions.Exceptions import ParserException
from hpl.engine import error_codes
from pint import UnitRegistry

ur = UnitRegistry()
Q_ = ur.Quantity


def init_default_integer():
    return 0


def init_default_float():
    return 0.0


def init_default_string():
    return ""


def init_default_char():
    return ''


def init_default_boolean():
    return False


def init_default_object():
    return {}


def init_default_array():
    return []


initialize_default_functions = {
    'INTEGER': init_default_integer,
    'FLOAT': init_default_float,
    'STRING': init_default_string,
    'CHAR': init_default_char,
    'BOOLEAN': init_default_boolean,
    'OBJECT': init_default_object,
    'ARRAY': init_default_array
}

map_types_python = {
    'INTEGER': [int],
    'FLOAT': [float, int],
    'STRING': [str],
    'CHAR': [str],
    'BOOLEAN': [bool],
    'OBJECT': [dict],
    'ARRAY': [list]
}

map_types_hpl = {
    'INTEGER': "inteiro",
    'FLOAT': "flutuante",
    'STRING': "texto",
    'CHAR': "caracter",
    'BOOLEAN': "booleano",
    'OBJECT': "objeto",
    'ARRAY': "sequência",
    int: "inteiro",
    float: "flutuante",
    str: "texto",
    bool: "booleano",
    dict: "objeto",
    list: "sequência",
}


def iscompatibleTypes(type_1, type_2):
    if type_1 == float:
        return type_2 in [float, int]
    if type_1 == int:
        return type_2 in [float, int]
    return type_1 == type_2


def addSymbolDefaultValue(symbol_name, symbol_type, symbol_table):
    if symbol_type not in initialize_default_functions:
        raise ParserException(
            {
                "error_code": error_codes.CODES["SYMBOL_TYPE_NOT_FOUND"],
                "error_value": symbol_type
            })
    symbol_table[symbol_name] = initialize_default_functions[symbol_type]()


def addSymbolWithValue(symbol_name, symbol_type, symbol_value, symbol_table):
    if symbol_type not in initialize_default_functions:
        raise ParserException(
            {
                "error_code": error_codes.CODES["SYMBOL_TYPE_NOT_FOUND"],
                "error_value": symbol_type,
            })
    if symbol_value is not None:
        if type(symbol_value) not in map_types_python[symbol_type]:
            raise ParserException(
                {
                    "error_code": error_codes.CODES["TYPE_ERROR"],
                    "error_value": symbol_value,
                    "expected_type": map_types_hpl[symbol_type],
                    "received_type": map_types_hpl[type(symbol_value)],
                    "received_value": symbol_value
                })
    symbol_table[symbol_name] = symbol_value


def updateSymbolWithValue(symbol_name, symbol_value, symbol_table, automap):
    if symbol_name in symbol_table:
        symbol_name_type = type(symbol_table[symbol_name])
        symbol_value_quantity = symbol_value.magnitude if (
                    symbol_name_type == float and hasattr(symbol_value, 'magnitude')) else symbol_value
        if not iscompatibleTypes(symbol_name_type, type(symbol_value_quantity)):
            raise ParserException(
                {
                    "error_code": error_codes.CODES["TYPE_ERROR"],
                    "error_value": symbol_value,
                    "expected_type": map_types_hpl[symbol_name_type],
                    "received_type": map_types_hpl[type(symbol_value_quantity)],
                    "received_value": symbol_value
                })
        symbol_table[symbol_name] = symbol_value
    else:
        if symbol_name in automap:
            symbol_name_type = type(symbol_table[automap[symbol_name]])
            symbol_value_quantity = symbol_value.magnitude if (
                    symbol_name_type == float and hasattr(symbol_value, 'magnitude')) else symbol_value
            if not iscompatibleTypes(symbol_name_type, type(symbol_value_quantity)):
                raise ParserException(
                    {
                        "error_code": error_codes.CODES["TYPE_ERROR"],
                        "error_value": symbol_value,
                        "expected_type": map_types_hpl[symbol_name_type],
                        "received_type": map_types_hpl[type(symbol_value_quantity)],
                        "received_value": symbol_value
                    })
            symbol_table[automap[symbol_name]] = symbol_value
            symbol_table[symbol_name] = symbol_value
        raise ParserException(
            {
                "error_code": error_codes.CODES["SYMBOL_NAME_NOT_FOUND"],
                "error_value": symbol_name,
            })


def getSymbol(symbol_name, symbol_table, automap):
    if symbol_name in symbol_table:
        if symbol_table[symbol_name] is None:
            return get_symbol_in_automap(symbol_name, symbol_table, automap)
        return symbol_table[symbol_name]
    else:
        return get_symbol_in_automap(symbol_name, symbol_table, automap)


def get_symbol_in_automap(symbol_name, symbol_table, automap):
    if symbol_name in automap:
        paths = automap[symbol_name].split('.')
        from hpl.engine.interpreter import execute_program
        return execute_program(mount_automap_execution_tree(paths), symbol_table, automap)
    raise ParserException(
        {
            "error_code": error_codes.CODES["SYMBOL_NAME_NOT_FOUND"],
            "error_value": symbol_name,
        })


def mount_automap_execution_tree(paths):
    execution_tree = ('IDENTIFIER', paths[0])
    if len(paths) > 0:
        for i in range(1,len(paths)):
            execution_tree = ('ACCESS_SUBPROPERTY', execution_tree, paths[i])
    return execution_tree
