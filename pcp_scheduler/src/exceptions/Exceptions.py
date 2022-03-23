class InsufficientResourcesException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InsufficientResourceCalendarException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LoadBalancerViolationException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
