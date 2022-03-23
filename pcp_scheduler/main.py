# coding: utf-8

from pcp_scheduler.src.scheduler.scheduler_ag import generate_allocation
from encoder import encoder
from pcp_scheduler.src.exceptions import Exceptions


def invoke(event, context):
    payload = encoder.deserializer(event['payload'])
    grid = payload['grid']
    tasks = payload['planjobs']
    configs = payload['configs']

    try:
        response = generate_allocation(grid, tasks, configs)
    except Exceptions.InsufficientResourcesException as e1:
        response = {"reason": "InsufficientResourcesException", 'resources': e1.value}
    except Exceptions.InsufficientResourceCalendarException as e2:
        response = {"reason": "InsufficientResourceCalendarException", 'resources': e2.value}
    except Exception as e3:
        response = {"reason": "Unknown"}

    return encoder.serializer(response)
