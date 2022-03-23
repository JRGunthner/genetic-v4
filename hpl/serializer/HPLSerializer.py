#coding: utf-8

import numpy

from hpl.engine.error_codes import UserDefinedError
from hpl.engine import error_codes
from hpl.exceptions.Exceptions import ParserException

"""
Serialize HPL answer to JSON:
{
    value: <answer value>
    type: <answer type>
    measurement_unit: <answer measurement unit>
}
"""


def serializer(answer):
    if type(answer) == UserDefinedError:
        raise ParserException(
            {
                "error_code": error_codes.CODES["USER_ERROR"],
                "error_value": answer.msg,
            })
    elif type(answer) == bool:
        serialized_obj = {
            "type": "bool",
            "value": boolSerializer(answer)
        }
    elif type(answer) == int:
        serialized_obj = {
            "type": "int",
            "value": answer
        }
    elif type(answer) == float: #TODO: alterar formato de saída do float, para respeitar o mesmo formato de entrada
        serialized_obj = {
            "type": "float",
            "value": answer
        }
    elif type(answer) == list:
        serialized_obj = {
            "type": "list",
            "value": answer
        }
    elif type(answer) == numpy.ndarray: #Fixme: a comparação não pode ser feita assim, ver PINT_QUANTITY
        serialized_obj = {
             "type": "list",
             "value": answer.tolist()
        }
    elif type(answer) == str:
        serialized_obj = {
            "type": "string",
            "value": answer
        }
    elif type(answer) == dict:
        serialized_obj = {
            "type": "object",
            "value": answer
        }
    elif hasattr(answer, 'units'):
            serialized_obj = {
                "measurement_unit": '{:~}'.format(answer.units)
            }
            serialized_obj = {**serialized_obj, **serializer(answer.magnitude)}
    else:
        serialized_obj = {
            "type": "none",
            "value": None
        }

    return serialized_obj


def boolSerializer(value):
    if value:
        return "verdadeiro"
    else:
        return "falso"
