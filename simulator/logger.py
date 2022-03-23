import json

import boto3

from simulator.serializer import Serializer


class HoldLogger():
    array_to_log = []
    population = []
    client = {}
    def __init__(self, population, reuse_bin, generation):
        self.population = population
        self.reuse_bin = reuse_bin
        self.generation = generation
        self.client = lib.boto3.client('lambda')

    def run(self):
        self.array_to_log = []
        for individual in self.population:
            obj = Serializer(individual[0], self.reuse_bin, individual[0].machine_info["margins"]).get_returned_obj()
            self.array_to_log.append(obj)
        obj_generation = {
            "generation": self.generation,
            "array_to_log": json.dumps(self.array_to_log)
        }
        print(obj_generation)
        try:
            self.client.invoke(FunctionName='simulator_log',
                           InvocationType='Event',
                           Payload=json.dumps(obj_generation)
                           )
        except:
            print("Excedeu o tamanho limite")
