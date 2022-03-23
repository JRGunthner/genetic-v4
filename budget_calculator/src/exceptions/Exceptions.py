class HPLExecutionException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidMeasurementUnitCastException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidTypeCastException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)