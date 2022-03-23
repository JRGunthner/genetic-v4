from pcp_scheduler.src.model.LoadBalancer import *

def get_limit_4_hours(process_id=1):
    daily_limit = DailyJourneyLimit(minutes_limit=240)
    load_limit = LoadLimiter()
    load_limit.add_rule(process_id, daily_limit)

    return load_limit

