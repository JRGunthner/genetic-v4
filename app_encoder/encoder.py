# coding: utf-8

import pandas as pd
import json
from encoder import CustomEncoder


def serializer(obj):
    return json.dumps(obj, cls=CustomEncoder.CustomEncoder)


def deserializer(obj):
    return json.loads(obj, object_hook=CustomEncoder.custom_decode)


def deserializer_file(path):
    # with open(path, encoding='ISO-8859-1') as file:
    with open(path, encoding='utf-8') as file:
        result = json.load(file, object_hook=CustomEncoder.custom_decode)
    return result
