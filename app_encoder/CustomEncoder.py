# coding: utf-8

from datetime import datetime

from pint.util import UnitsContainer

from budget_calculator.src.model.Feedstock import Feedstock
from budget_calculator.src.model.HPLScript import HPLScript
from budget_calculator.src.model.IncomeTaxSellingCost import IncomeTaxSellingCost
from budget_calculator.src.model.ProposalItem import ProposalItem
from budget_calculator.src.model.PaymentOptionTax import PaymentOptionTax
from budget_calculator.src.model.BudgetPriceMethod import BudgetPriceMethod
from budget_calculator.src.model.Process import Process
from budget_calculator.src.model.Product import Product
from budget_calculator.src.model.ProductionCost import ProductionCost
from budget_calculator.src.model.ChooseFeedstock import ChooseFeedstock
from budget_calculator.src.model.Proposal import Proposal
from budget_calculator.src.model.ProposalWithUserToken import ProposalWithUserToken
from budget_calculator.src.model.SellingCost import SellingCost
from budget_calculator.src.model.ProcessFeedstockFormula import ProcessFeedstockFormula
from budget_variable_validator.src.model.ProcessVariableModel import ProcessVariableModel
from budget_variable_validator.src.model.ProductVariableModel import ProductVariableModel
from budget_variable_validator.src.model.VariableAutomapModel import VariableAutomapModel
from pcp_scheduler.src.model.Configuration import Configuration
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.src.model.ResourceCharacteristic import ResourceCharacteristic
from pcp_scheduler.src.model.Resource import Resource
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.ProcessLoadInformation import ProcessLoadInformation
from pcp_scheduler.src.model.Journey import Journey, DailyJourney
from pcp_scheduler.src.model.LoadBalancer import LoadLimiter, DailyJourneyLimit

import json


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,  datetime):
            return {'__datetime__': o.replace(microsecond=0).isoformat()}
        if isinstance(o, set):
            return list(o)
        if isinstance(o, UnitsContainer):
            return str(o)

        return {'__{}__'.format(o.__class__.__name__): o.__dict__}


def custom_decode(o):
    if '__Resource__' in o:
        resource = Resource()
        resource.__dict__.update(o['__Resource__'])
        return resource
    elif '__DesiredResource__' in o:
        desired = DesiredResource()
        desired.__dict__.update(o['__DesiredResource__'])
        return desired
    elif '__ResourceCharacteristic__' in o:
        characteristic = ResourceCharacteristic()
        characteristic.__dict__.update(o['__ResourceCharacteristic__'])
        return characteristic
    elif '__Planjob__' in o:
        task = Planjob()
        task.__dict__.update(o['__Planjob__'])
        return task
    elif '__Configuration__' in o:
        configs = Configuration()
        configs.__dict__.update(o['__Configuration__'])
        return configs
    elif '__Slot__' in o:
        slot = Slot()
        slot.__dict__.update(o['__Slot__'])
        return slot
    elif '__ProcessLoadInformation__' in o:
        process_info = ProcessLoadInformation()
        process_info.__dict__.update(o['__ProcessLoadInformation__'])
        return process_info
    elif '__Journey__' in o:
        journey = Journey()
        journey.__dict__.update(o['__Journey__'])
        return journey
    elif '__DailyJourney__' in o:
        daily_journey = DailyJourney()
        daily_journey.__dict__.update(o['__DailyJourney__'])
        return daily_journey
    elif '__LoadLimiter__' in o:
        load_limiter = LoadLimiter()
        load_limiter.__dict__.update(o['__LoadLimiter__'])
        return load_limiter
    elif '__DailyJourneyLimit__' in o:
        daily_limit = DailyJourneyLimit()
        daily_limit.__dict__.update(o['__DailyJourneyLimit__'])
        return daily_limit
    elif '__Proposal__' in o:
        propose = Proposal()
        propose.__dict__.update(o['__Proposal__'])
        return propose
    elif '__ProposalWithUserToken__' in o:
        propose_with_user_token = ProposalWithUserToken()
        propose_with_user_token.data.__dict__.update(o['__ProposalWithUserToken__']['data'])
        propose_with_user_token.token = o['__ProposalWithUserToken__']['token']
        return propose_with_user_token
    elif '__Product__' in o:
        product = Product()
        product.__dict__.update(o['__Product__'])
        return product
    elif '__ProductVariableModel__' in o:
        product_variable_model = ProductVariableModel()
        product_variable_model.__dict__.update(o['__ProductVariableModel__'])
        return product_variable_model
    elif '__Process__' in o:
        process = Process()
        process.__dict__.update(o['__Process__'])
        return process
    elif '__ChooseFeedstock__' in o:
        choose_feedstock = ChooseFeedstock()
        choose_feedstock.__dict__.update(o['__ChooseFeedstock__'])
        return choose_feedstock
    elif '__ProcessVariableModel__' in o:
        process_variable_model = ProcessVariableModel()
        process_variable_model.__dict__.update(o['__ProcessVariableModel__'])
        return process_variable_model
    elif '__VariableAutomapModel__' in o:
        variable_automap_model = VariableAutomapModel()
        variable_automap_model.__dict__.update(o['__VariableAutomapModel__'])
        return variable_automap_model
    elif '__ProposalItem__' in o:
        item = ProposalItem()
        item.__dict__.update(o['__ProposalItem__'])
        return item
    elif '__Feedstock__' in o:
        feedstock = Feedstock()
        feedstock.__dict__.update(o['__Feedstock__'])
        return feedstock
    elif '__PaymentOptionTax__' in o:
        payment_option_tax = PaymentOptionTax()
        payment_option_tax.__dict__.update(o['__PaymentOptionTax__'])
        return payment_option_tax
    elif '__ProductionCost__' in o:
        production_cost = ProductionCost()
        production_cost.__dict__.update(o['__ProductionCost__'])
        return production_cost
    elif '__SellingCost__' in o:
        selling_cost = SellingCost()
        selling_cost.__dict__.update(o['__SellingCost__'])
        return selling_cost
    elif '__BudgetPriceMethod__' in o:
        price_method = BudgetPriceMethod()
        price_method.__dict__.update(o['__BudgetPriceMethod__'])
        return price_method
    elif '__IncomeTaxSellingCost__' in o:
        income_tax_selling_cost = IncomeTaxSellingCost()
        income_tax_selling_cost.__dict__.update(o['__IncomeTaxSellingCost__'])
        return income_tax_selling_cost
    elif '__HPLScript__' in o:
        hpl_script = HPLScript()
        hpl_script.__dict__.update(o['__HPLScript__'])
        return hpl_script
    elif '__ProcessFeedstockFormula__' in o:
        process_feedstock_formula = ProcessFeedstockFormula()
        process_feedstock_formula.__dict__.update(o['__ProcessFeedstockFormula__'])
        return process_feedstock_formula
    elif '__ProcessFeedstockVariableModel__' in o:
        process_feedstock_variable_model = ProcessVariableModel()
        process_feedstock_variable_model.__dict__.update(o['__ProcessFeedstockVariableModel__'])
        return process_feedstock_variable_model
    elif '__datetime__' in o:
        return datetime.strptime(o['__datetime__'], '%Y-%m-%dT%H:%M:%S')
    else:
        return o
