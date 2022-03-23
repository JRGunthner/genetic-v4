from budget_calculator.src.model.BudgetCalculationOutput import ProposalCalcResponse, ProposalItemCalcResponse, \
    ProductCalcResponse, FeedstockCalcResponse, ProcessCalcResponse, ErrorCalcResponse, MessageErrorResponse


def convert_to_processes_response(processes):
    processes_response = []
    for process in processes:
        processes_response.append(ProcessCalcResponse(process.production_cost, process.printing_costs, process.feedstocks, process.time_spent, process.product_block_feedstocks))

    return processes_response


def convert_to_feedstocks_response(feedstocks):
    feedstocks_response = []
    for feedstock in feedstocks:
        feedstocks_response.append(FeedstockCalcResponse(feedstock.production_cost, feedstock.choose_feedstock))

    return feedstocks_response


def convert_to_products_response(products):
    products_response = []
    for product in products:
        processes_response = convert_to_processes_response(product.processes)
        feedstocks_response = convert_to_feedstocks_response(product.feedstocks)
        product_response = ProductCalcResponse(product.production_cost, product.total_value,
                                               product.apportionment_value, product.commission,
                                               processes_response, feedstocks_response)
        products_response.append(product_response)

    return products_response


def convert_to_items_response(items):
    items_response = []
    for item in items:
        products_response = convert_to_products_response(item.products)
        item_response = ProposalItemCalcResponse(item.production_cost, item.total_price,
                                                 item.apportionment_value, products_response,
                                                 item.quantity, item.unit_price)
        items_response.append(item_response)

    return items_response


def convert_to_proposal_response(proposal_calculated):
    items_response = convert_to_items_response(proposal_calculated.items)
    proposal_response = ProposalCalcResponse(
        items_response, proposal_calculated.total_price, proposal_calculated.total_profit_percentual)
    proposal_response.calculation_id = proposal_calculated.calculation_id
    return proposal_response


def convert_to_message_error_response(error_code, message_error):
    message_error_response = MessageErrorResponse(
            error_code, message_error)
    return message_error_response


def convert_to_error_response(error_reason):
    message_error_response = convert_to_message_error_response(
        error_reason['error_code'], error_reason['message_error'])
    error_response = ErrorCalcResponse(
        error_reason['error_code'], message_error_response, error_reason['stack'], error_reason['method'])

    return error_response
