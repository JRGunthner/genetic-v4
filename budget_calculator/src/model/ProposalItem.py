import uuid

from budget_calculator.src.model.ProductionCost import ProductionCost


class ProposalItem:
    def __init__(self, products=[], processes=[], feedstocks=[]):
        self.unique_local_id = str(uuid.uuid4())
        self.products = products
        self.processes = processes
        self.feedstocks = feedstocks
        self.production_cost = {}
        self.total_price = float(0.0)
        self.quantity = float(0.0)
        self.unit_price = float(0.0)
        self.apportionment_value = float(0.0)
        self.context = {}
        self.hidden = False

    def __getitem__(self, key):
        return getattr(self, key)

    def execute_pre_scripts(self):
        for product in self.products:
            product.execute_pre_hpl_scripts()

    def calc_production_cost(self, context):
        new_context = {**context, **self.context}
        self.production_cost = ProductionCost()
        product_index = 0
        for product in self.products:
            try:
                product.execute_pre_hpl_scripts()
                product.calc_production_cost(new_context)
            except Exception as e:
                e.value['variable']["message_error"]["product_index"] = product_index
                raise
            product_index += 1
            self.production_cost.labor_production_cost += product.production_cost.labor_production_cost
            self.production_cost.feedstock_production_cost += product.production_cost.feedstock_production_cost
            self.production_cost.outsourcing_production_cost += product.production_cost.outsourcing_production_cost

    def set_apportionment(self, value):
        if value > 0:
            total_products_production_cost = self.production_cost.sum_production_costs()
            self.apportionment_value = value
            self.production_cost.distribute_apportionment_value(value)
            for product in self.products:
                product_apportionment_value = value*(product.production_cost.sum_production_costs()/total_products_production_cost)
                product.set_apportionment(product_apportionment_value)

    def calc_total_value(self, context):
        new_context = {**context, **self.context}
        product_index = 0
        for product in self.products:
            try:
                product.calc_total_value(new_context)
            except Exception as e:
                e.value['variable']["message_error"]["product_index"] = product_index
                raise
            product_index += 1
            self.total_price = float(self.total_price) + float(product.total_value)

    def calc_quantity(self, measurement_unit_hpl_symbol):
        self.quantity = float(0.0)
        product_index = 0
        for product in self.products:
            try:
                product.calc_total_quantity(measurement_unit_hpl_symbol)
            except Exception as e:
                e.value['variable']["message_error"]["product_index"] = product_index
                raise
            product_index += 1
            self.quantity += product.total_quantity

    def calc_unit_price(self):
        self.unit_price = 0.0

        if self.quantity != 0:
            self.unit_price = self.total_price / self.quantity
