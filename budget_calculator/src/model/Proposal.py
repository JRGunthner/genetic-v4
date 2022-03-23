import uuid


class Proposal:
    def __init__(self):
        self.unique_local_id = str(uuid.uuid4())
        self.account_id = 0
        self.proposal_id = 0
        self.public_id = 0
        self.payment_option_tax = {}
        self.items = []
        self.context = {}
        self.total_production_cost_value = 0.0
        self.total_hidden_production_cost_value = 0.0
        self.total_non_hidden_production_cost_value = 0.0
        self.total_price = 0.0
        self.total_profit_percentual = 0.0

    def __getitem__(self, key):
        return getattr(self, key)

    def calc_propose_price(self):
        self.calc_production_cost()
        self.apportionment_hidden_items()
        self.calc_total_cost()
        self.calc_quantity()
        self.calc_unit_price()
        self.calc_total_profit_percentual()
    
    def calc_production_cost(self):
        item_index = 0
        for item in self.items:
            try:
                item.calc_production_cost(self.context)
            except Exception as e:
                e.value['variable']["message_error"]["item_index"] = item_index
                raise

            if item.hidden:
                self.total_hidden_production_cost_value = \
                    self.total_hidden_production_cost_value + item.production_cost.sum_production_costs()
            else:
                self.total_non_hidden_production_cost_value = \
                    self.total_non_hidden_production_cost_value + item.production_cost.sum_production_costs()

            item_index += 1

        self.total_production_cost_value = \
            self.total_hidden_production_cost_value + self.total_non_hidden_production_cost_value

    def apportionment_hidden_items(self):
        if self.total_non_hidden_production_cost_value > 0:
            for item in self.items:
                if not item.hidden:
                    percent = item.production_cost.sum_production_costs() / self.total_non_hidden_production_cost_value
                    item.set_apportionment(self.total_hidden_production_cost_value * percent)

    def calc_total_cost(self):
        item_index = 0
        for item in self.items:
            if not item.hidden:
                try:
                    item.calc_total_value(self.context)
                except Exception as e:
                    e.value['variable']["message_error"]["item_index"] = item_index
                    raise
                item_index += 1
                self.total_price += item.total_price

    def calc_quantity(self):
        measurement_unit_hpl_symbol = "m*m"
        item_index = 0
        for item in self.items:
            if not item.hidden:
                try:
                    item.calc_quantity(measurement_unit_hpl_symbol)
                except Exception as e:
                    e.value['variable']["message_error"]["item_index"] = item_index
                    raise
                item_index += 1

    def calc_unit_price(self):
        item_index = 0
        for item in self.items:
            if not item.hidden:
                try:
                    item.calc_unit_price()
                except Exception as e:
                    e.value['variable']["message_error"]["item_index"] = item_index
                    raise
                item_index += 1

    def calc_total_profit_percentual(self):
        self.total_profit_percentual = \
            ((self.total_price - self.total_production_cost_value) * 100) / \
            (self.total_production_cost_value if self.total_production_cost_value != 0 else 1)
