class PaymentOptionTax:
    def __init__(self):
        self.value = 0.0
        self.value_type = -1
        self.tax_type = -1

    def __getitem__(self, key):
        return getattr(self, key)