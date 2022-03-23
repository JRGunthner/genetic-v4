# coding: utf-8
from datetime import datetime, timedelta
from .LoadBalancer import LoadLimiter
from pcp_scheduler.utils import utils


class Resource:
    DATE_FORMAT = "%Y/%m/%d"

    def __init__(self, _id: object = "", name: object = "", sectors: object = [], groups: object = [], hour_type: object = "") -> object:
        self.id = _id
        self.name = name
        self.sectors = sectors
        self.groups = groups
        self.hour_type = hour_type
        self.available_slots = None
        self.load_limit = None
        self.journey = None
        self.date_load_informations = None
        self.brothers = []

    def __eq__(self, other):
        if not isinstance(other,  Resource):
            return False

        return self.name == other.name and self.sectors == other.sectors and self.groups == other.groups \
               and self.hour_type == other.hour_type

    def __ne__(self, other):
        if not isinstance(other, Resource):
            return True
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, ",".join(self.sectors), ",".join(self.groups), self.hour_type))

    def clean_temp_attrs(self):
        self.brothers = []

    def is_balanced(self, date_str, process_id, planjob_time):
        if self.load_limit is None: return True
        if process_id not in self.load_limit.rules.keys(): return True

        time_allocated = 0
        if date_str in self.date_load_informations.keys():
            process_info = self.get_process_by_id(process_id, date_str)
            if process_info is not None:
                time_allocated = sum(process_info.planjobs_per_time.values())

        minutes_limit = self.load_limit.rules[process_id].minutes_limit
        if minutes_limit is not None:
            return planjob_time + time_allocated <= minutes_limit
        else:
            date = datetime.strptime(date_str, self.DATE_FORMAT)
            weekday = date.weekday()
            daily_journey = filter(lambda d: d.day_of_week == weekday, self.journey.daily_journeys)
            if daily_journey != []:
                journey_duration = daily_journey[0].get_workable_duration()
                percentual_used = ((planjob_time + time_allocated) / journey_duration)*100
                return percentual_used <= self.load_limit.rules[process_id].percentual_limit

        return True

    def get_process_by_id(self, process_id, date_str):
        for process_info in self.date_load_informations[date_str]:
            if process_info.process_id == process_id:
                return process_info

        return None

    def has_slot(self, date_str, desired_slot):
        if date_str in self.available_slots.keys():
            for slot in self.available_slots[date_str]:
                if slot.start_time <= desired_slot.start_time and desired_slot.finish_time <= slot.finish_time:
                    return True

        return False

    def get_intervals_by_journey_date(self, date):
        weekday = date.weekday()
        daily_journey = [d for d in self.journey.daily_journeys if d.day_of_weekday == weekday]
        return daily_journey[0].intervals

    def is_slot_on_the_tail(self, slot):
        date = slot.start_time.date()
        weekday = date.weekday()
        for daily in self.journey.daily_journeys:
            if daily.day_of_weekday == weekday:
                return utils.time(slot.finish_time) == utils.time(daily.finish_time)  # ToDo or if has extra hours and slot in extra hour
                # ToDo se cheguei aqui meu slot não é compativel com nenhuma daily journey, o q fazer?

    def is_slot_on_the_head(self, slot):
        date = slot.start_time.date()
        weekday = date.weekday()
        for daily in self.journey.daily_journeys:
            if daily.day_of_weekday == weekday:
                return utils.time(slot.start_time) == utils.time(daily.start_time)  # ToDo or if has extra hours and slot in extra hour
                # ToDo se cheguei aqui meu slot não é compativel com nenhuma daily journey, o q fazer?

    def has_util_interval_allowed_btw_slots(self, slot, next_slot):
        date = slot.start_time.date()
        for interval_ in self.get_intervals_by_journey_date(date):
            if utils.time(slot.finish_time) == utils.time(interval_.start_time):
                return not self.is_interval_in_unavailable_slots(interval_)

        interval = (slot.finish_time, next_slot.start_time)
        return not self.is_interval_in_unavailable_slots(interval)

    def is_interval_in_unavailable_slots(self, interval):
        #Todo: receber unaivalable e verificar
        return False

    def get_daily_journey_by_date(self, datetime_):
        weekday = datetime_.weekday()
        return self.get_daily_journey_weekday(weekday)

    def get_daily_journey_weekday(self, weekday):
        for daily_journey in self.journey.daily_journeys:
            if daily_journey.day_of_weekday == weekday:
                return daily_journey
