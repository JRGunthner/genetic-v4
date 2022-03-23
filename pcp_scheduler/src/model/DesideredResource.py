class DesiredResource:
    def __init__(self, resources_characteristic=[]):
        self.resources_characteristic = resources_characteristic

    def add_resource_characteristic(self, resource_characteristic):
        self.resources_characteristic.append(resource_characteristic)
