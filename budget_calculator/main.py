import traceback

from services import message_broker, calcTrackerService
from hpl.engine import error_codes


def budget_calc(propose):
    calc_fired_msg = calcTrackerService.get_calc_fired_status(propose.calculation_id, propose.account_id)
    message_broker.log_calc_status(calc_fired_msg)
    try:
        propose.calc_propose_price()
        calc_finished_msg = calcTrackerService.get_calc_finished_status(propose.calculation_id, propose.account_id, propose)
        message_broker.log_calc_status(calc_finished_msg)
        return propose
    except Exception as e:
        if hasattr(e, 'value') and "message_error" in e.value['variable']:
            result = {"error_code": e.value['variable']["error_code"],
                  "message_error": e.value['variable']["message_error"],
                  "method": e.value['method'],
                  "stack": traceback.format_exc()}
        else:
            result = {"error_code": error_codes.CODES["UNEXPECTED"],
                      "message_error": "Unexpected error",
                      "stack": traceback.format_exc()}

        calc_finished_msg = calcTrackerService.get_calc_error_status(propose.calculation_id, propose.account_id, result)
        message_broker.log_calc_status(calc_finished_msg)

        return result
