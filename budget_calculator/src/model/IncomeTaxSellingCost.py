class IncomeTaxSellingCost:
    def __init__(self):
        pass

    def generate_subcontext(self):
        return self.__dict__

    def __getitem__(self, key):
        return getattr(self, key)