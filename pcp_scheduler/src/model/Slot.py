# coding: utf-8

from datetime import datetime
from functools import total_ordering


@total_ordering
class Slot:
    def __init__(self, date=datetime.today(), start_time=datetime.today(), finish_time=datetime.today()):
        self.date = self.get_date_format(date)
        self.start_time = start_time
        self.finish_time = finish_time
        self.complement = None
        self.resources = None

    def __eq__(self, other):
        if not isinstance(other, Slot):
            return False
        return self.date == other.date and self.start_time == other.start_time and self.finish_time == other.finish_time

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, Slot):
            raise TypeError("Other is not Slot")
        return (self.start_time, self.finish_time).__lt__((other.start_time, other.finish_time))

    def __hash__(self):
        return hash((self.date, self.start_time, self.finish_time))

    def get_date_format(self, datetime_):
        DATE_FORMAT = '%Y/%m/%d'
        return datetime_.strptime(datetime_.strftime(DATE_FORMAT), DATE_FORMAT)

    def minutes(self):
        '''
        Retorna a duração do slot em minutos
        :return: inteiro
        '''
        return (self.finish_time - self.start_time).total_seconds() // 60

    def light_copy(self):
        """
        Retorna uma cópia independente do slot, somente com os atributos principais: date, start_time e finish_time
        :return: um slot
        """
        my_copy = Slot(self.date, self.start_time, self.finish_time)
        return my_copy
