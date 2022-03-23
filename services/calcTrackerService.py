from datetime import datetime

from budget_calculator.src.converters import convert_to_proposal_response, convert_to_error_response
from encoder import mongo_encoder
from utils import environment


CALC_FIRED = 2
CALC_FINISHED = 3
CALC_BROKEN = 5
CALC_USER_ERROR = 6


def get_calc_fired_status(calculation_id, account_id):
    msg = {
            "calculation_id": calculation_id,
            "account_id": account_id,
            "time": datetime.utcnow(),
            "status": CALC_FIRED
          }

    print("calc fired -> info: ", msg)
    return mongo_encoder.serializer(msg)


def get_calc_error_status(calculation_id, account_id, error_reason):
    error_response = convert_to_error_response(error_reason)
    msg = {
            "calculation_id": calculation_id,
            "account_id": account_id,
            "time": datetime.utcnow(),
            "status": CALC_BROKEN,
            "error_reason": error_response
        }

    print("calc broken -> ", msg)
    print(error_reason)
    return mongo_encoder.serializer(msg)


def get_calc_finished_status(calculation_id, account_id, proposal):
    proposal_response = convert_to_proposal_response(proposal)
    msg = {
            "calculation_id": calculation_id,
            "account_id": account_id,
            "time": datetime.utcnow(),
            "status": CALC_FINISHED,
            "output": proposal_response
         }
    print("calc finished -> result: ", msg)
    return mongo_encoder.serializer(msg)
