from datetime import datetime
from pcp_scheduler.src.model.Journey import Journey, DailyJourney
from pcp_scheduler.src.model.Slot import Slot

def get_journey_default():
    daily_journeys =[]
    interval = [Slot(datetime(1, 1, 1), datetime(1, 1, 1, 12), datetime(1, 1, 1, 13))]
    for i in range(7):
        daily_journey = DailyJourney(datetime(1, 1, 1, 8), datetime(1, 1, 1, 18), i, interval)
        daily_journeys.append(daily_journey)

    return Journey(daily_journeys)

def get_journey_6h_morning():
    daily_journeys = []
    for i in range(7):
        daily_journey = DailyJourney(datetime(1, 1, 1, 6), datetime(1, 1, 1, 12), i)
        daily_journeys.append(daily_journey)

    return Journey(daily_journeys)

def get_journey_6h_afternoon():
    daily_journeys = []
    for i in range(7):
        daily_journey = DailyJourney(datetime(1, 1, 1, 12), datetime(1, 1, 1, 18), i)
        daily_journeys.append(daily_journey)

    return Journey(daily_journeys)

def get_journey_6h_evening():
    daily_journeys = []
    for i in range(7):
        daily_journey = DailyJourney(datetime(1, 1, 1, 18), datetime(1, 1, 1, 0), i)
        daily_journeys.append(daily_journey)

    return Journey(daily_journeys)

def get_journey_6h_night():
    daily_journeys = []
    for i in range(7):
        daily_journey = DailyJourney(datetime(1, 1, 1, 0), datetime(1, 1, 1, 6), i)
        daily_journeys.append(daily_journey)

    return Journey(daily_journeys)

def get_journey_10pm_to_10am():
    daily_journeys = []
    for i in range(7):
        daily_journey = DailyJourney(datetime(1, 1, 1, 22), datetime(1, 1, 1, 10), i)
        daily_journeys.append(daily_journey)

    return Journey(daily_journeys)
