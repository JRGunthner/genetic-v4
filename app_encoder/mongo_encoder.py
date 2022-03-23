# coding: utf-8

from datetime import datetime

import json

from pint.util import UnitsContainer


def serializer(obj):
    return json.dumps(obj, cls=MongoEncoder)


def deserializer(obj):
    return json.loads(obj)


class MongoEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,  datetime):
            return o.replace(microsecond=0).isoformat()
        if isinstance(o, set):
            return list(o)
        if isinstance(o, UnitsContainer):
            return str(o)

        return o.__dict__


def custom_decode(o):
    return o
