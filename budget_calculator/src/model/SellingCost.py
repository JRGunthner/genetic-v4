class SellingCost:
    def __init__(self):
        self.tax_cost = 0.0
        self.commission_cost = 0.0
        self.financial_cost = 0.0
        self.other_cost = 0.0

    def __getitem__(self, key):
        return getattr(self, key)