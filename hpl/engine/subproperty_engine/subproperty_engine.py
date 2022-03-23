import math

from budget_calculator.src.exceptions.Exceptions import HPLExecutionException
from hpl.engine import error_codes


def subproperty_engine_size(object, param=None):
    if type(object) is list:
        return len(object)


def subproperty_engine_keys(object, param=None):
    if type(object) is dict:
        return list(object.keys())


def subproperty_engine_round(object, ndigits=0):
    if type(object) is int or type(object) is float:
        return round(object, ndigits)


def subproperty_engine_truncate(object, ndigits=0):
    if type(object) is int or type(object) is float:
        return math.floor(object * 10 ** ndigits) / 10 ** ndigits


def subproperty_engine_floor(object, param = None):
    if type(object) is int or type(object) is float:
        return math.floor(object)


def subproperty_engine_ceil(object, param = None):
    if type(object) is int or type(object) is float:
        return math.ceil(object)


def subproperty_engine_contains(object, param=None):
    if type(object) is list:
        object = [item.lower() for item in object]
        if type(param) is list:
            param = [item.lower() for item in param]
            return set(param).issubset(set(object))
        else:
            param = param.lower()
            return param in object

def subproperty_engine_add(object, param=None):
    if type(object) is list:
        object.append(param)

subproperty_engine_en = {
    "size": subproperty_engine_size,
    "keys": subproperty_engine_keys,
    "round": subproperty_engine_round,
    "truncate": subproperty_engine_truncate,
    "floor": subproperty_engine_floor,
    "ceil": subproperty_engine_ceil,
    "contains": subproperty_engine_contains,
    "add": subproperty_engine_add
}

subproperty_engine_pt = {
    "tamanho": subproperty_engine_size,
    "chaves": subproperty_engine_keys,
    "arredonda": subproperty_engine_round,
    "truncar": subproperty_engine_truncate,
    "piso": subproperty_engine_floor,
    "teto": subproperty_engine_ceil,
    "contem": subproperty_engine_contains,
    "adiciona": subproperty_engine_add
}


def select_subproperty(key, object, param=None):
    if key in subproperty_engine_pt:
        if param is None:
            return subproperty_engine_pt[key](object)
        else:
            return subproperty_engine_pt[key](object, param)
    elif (type(object) is dict) and (key in object):
        if (object[key] is None):
            raise HPLExecutionException(
                {
                    "error_code": error_codes.CODES["NONE_VALUE_RETURNED"],
                    "error_value": key,
                })
        return object[key]
    else:
        raise HPLExecutionException(
            {
                "error_code": error_codes.CODES["SUBPROPERTY_NOT_FOUND"],
                "error_value": key,
            })
