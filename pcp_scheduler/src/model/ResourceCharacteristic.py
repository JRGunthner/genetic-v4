class ResourceCharacteristic:
    def __init__(self, hour_type="", resources=[], sectors=[], groups=[], priority=0):
        self.resources = resources
        self.sectors = sectors
        self.groups = groups
        self.hour_type = hour_type
        self.priority = priority
