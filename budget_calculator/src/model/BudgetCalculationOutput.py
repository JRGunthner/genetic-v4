
class ProposalCalcResponse:
    def __init__(self, items, total_price, total_profit_percentual):
        self.items = items
        self.total_price = total_price
        self.total_profit_percentual = total_profit_percentual
        self.type = 1


class ProposalItemCalcResponse:
    def __init__(self, production_cost, total_value=None,
                 apportionment_value=None, products=None,
                 quantity=None, unit_price=None):
        self.production_cost = production_cost
        self.products = products
        self.total_value = total_value
        self.apportionment_value = apportionment_value
        self.quantity = quantity
        self.unit_price = unit_price

    def set_products(self, products):
        self.products = products

    def set_feedstocks(self, feedstocks):
        self.feedstocks = feedstocks

    def set_processes(self, processes):
        self.processes = processes


class ProductCalcResponse:
    def __init__(self, production_cost, total_value=None,
                 apportionment_value=None, commission_value=None,
                 processes=None, feedstocks=None):
        self.production_cost = production_cost
        self.processes = processes
        self.total_value = total_value
        self.apportionment_value = apportionment_value
        self.commission_value = commission_value
        self.feedstocks = feedstocks

    def set_feedstocks(self, feedstocks):
        self.feedstocks = feedstocks

    def set_processes(self, processes):
        self.processes = processes


class ProcessCalcResponse:
    def __init__(self, production_cost, printing_costs, feedstocks, time_spent, product_block_feedstocks):
        self.production_cost = production_cost
        self.printing_cost = printing_costs
        self.feedstocks = feedstocks
        self.time_spent = time_spent
        self.product_block_feedstocks = product_block_feedstocks


class ErrorCalcResponse:
    def __init__(self, error_code, message_error_response, stack, method):
        self.error_code = error_code
        self.message_error = message_error_response
        self.method = method
        self.stack = stack


class MessageErrorResponse:
    def __init__(self, error_code, message_error):
        self.error_code = error_code
        self.error_value = message_error["error_value"] if "error_value" in message_error else None
        self.error_value2 = message_error["error_value2"] if "error_value2" in message_error else None
        self.operation = message_error["operation"] if "operation" in message_error else None
        self.error_line = message_error["error_line"] if "error_line" in message_error else None
        self.error_position = message_error["error_position"] if "error_position" in message_error else None
        self.expected_type = message_error["expected_type"] if "expected_type" in message_error else None
        self.received_type = message_error["received_type"] if "received_type" in message_error else None
        self.process_index = message_error["process_index"] if "process_index" in message_error else None
        self.product_index = message_error["product_index"] if "product_index" in message_error else None
        self.item_index = message_error["item_index"] if "item_index" in message_error else None
        self.name_array = message_error["name_array"] if "name_array" in message_error else None
        self.size_array = message_error["size_array"] if "size_array" in message_error else None


class FeedstockCalcResponse:
    def __init__(self, production_cost, choose_feedstock):
        self.production_cost = production_cost
        self.choose_feedstock = choose_feedstock
