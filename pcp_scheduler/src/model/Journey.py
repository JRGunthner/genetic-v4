class DailyJourney:
    def __init__(self, start_time=None, finish_time=None, day_of_week=None, intervals=[]):
        self.start_time = start_time
        self.finish_time = finish_time
        self.day_of_weekday = day_of_week
        self.intervals = intervals

    def get_workable_duration(self):
        duration = (self.finish_time - self.start_time).total_seconds() / 60
        for slot in self.intervals:
            slot_duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            duration -= slot_duration

        # ToDo: verificar se tem hora extra naquele dia e somar a duration
        return duration

class Journey:
    def __init__(self, daily_journeys=[]):
        self.daily_journeys = daily_journeys
