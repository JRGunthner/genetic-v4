# coding: utf-8

from budget_calculator.src.model.Process import Process
from budget_calculator.src.model.Product import Product
from pcp_scheduler.src.model.Resource import Resource
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.Journey import Journey


def custom_decode(o):
    if 'Resource' in o:
        resource = Resource()
        resource.__dict__.update(o['__Resource__'])
        return resource
    if 'Slot' in o:
        slot = Slot()
        slot.__dict__.update(o['__Slot__'])
        return slot
    if 'Journey' in o:
        journey = Journey()
        journey.__dict__.update(o['__Journey__'])
        return journey
    if 'Product' in o:
        product = Product()
        product.__dict__.update(o['__Product__'])
        return product
    if 'Process' in o:
        process = Process()
        process.__dict__.update(o['__Process__'])
        return process
