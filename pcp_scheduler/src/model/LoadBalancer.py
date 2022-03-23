# coding: utf-8

from pcp_scheduler.src.exceptions.Exceptions import LoadBalancerViolationException


class DailyJourneyLimit:
    def __init__(self, minutes_limit=None, percentual_limit=None):
        self.minutes_limit = minutes_limit
        self.percentual_limit = percentual_limit


class LoadLimiter:
    def __init__(self, rules={}):
        self.rules = rules

    def add_rule(self, process_id, daily_limit=DailyJourneyLimit()):
        self.rules[process_id] = daily_limit


class LoadBalancer:

    @staticmethod
    def load_balance(planjob, date_str, desired_slot, prohibited_resources, configs):
        for i in range(len(planjob.allocated_resources)):
            resource = planjob.allocated_resources[i]
            must_change = None
            if not resource.is_balanced(date_str, planjob.process_id, planjob.time):
                must_change = True
                its_ok = False
                for brother in resource.brothers:
                    if brother in prohibited_resources:
                        continue
                    if not brother.is_balanced(date_str, planjob.process_id, planjob.time):
                        continue
                    if not brother.has_slot(date_str, desired_slot):
                        continue
                    planjob.allocated_resources[i] = brother
                    its_ok = True
                    break
            if configs.must_respect_load_limit and must_change and not its_ok:
                e = {"resource_id": resource.id, "desired_date": date_str, "desired_slot": desired_slot,
                     "planjob_id": planjob.id}
                raise LoadBalancerViolationException(e)

    @staticmethod
    def slot_is_allowed(slot, planjob, configs):
        if configs.must_respect_load_limit:
            date_str = slot.start_time.strftime("%Y/%m/%d")
            for resource in planjob.allocated_resources:
                if not resource.is_balanced(date_str, planjob.process_id, planjob.time + planjob.setup):
                    return False

        return True
