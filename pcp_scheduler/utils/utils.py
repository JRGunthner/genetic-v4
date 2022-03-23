#coding: utf-8

from pcp_scheduler.src.model.Slot import Slot
from datetime import datetime

global DATE_FORMAT, TIME_FORMAT, DATETIME_FORMAT
DATE_FORMAT = '%Y/%m/%d'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = '%Y/%m/%d %H:%M'

def get_all_permutations(vector):
    permutations = []
    recursive_permute(vector, 0, permutations)
    return permutations


def recursive_permute(vector, k, permutations):
    size = len(vector)
    if k == size:
        permutations.append(vector[::])
    else:
        for i in range(k, size):
            exchange_positions(vector, k, i)
            recursive_permute(vector, k + 1, permutations)
            exchange_positions(vector, i, k)


def exchange_positions(vector, p1, p2):
    tmp = vector[p1]
    vector[p1] = vector[p2]
    vector[p2] = tmp


def get_index_by_id(array, id):
    for i in range(len(array)):
        if array[i].id == id:
            return i
    return None


def median_low(data):
    data = sorted(data)
    length = len(data)
    if length % 2 == 1:
        return data[length//2]
    else:
        return data[length//2 - 1]


def has_any_planjob_fractioned(planjobs):
    for planjob in planjobs:
        if planjob.configs.fractioned_between_planjobs:
            return True

    return False


def has_planjob_same_day(planjobs):
    for planjob in planjobs:
        if planjob.configs.same_day: return True
    return False


def has_any_planjob_scheduled(planjobs):
    for planjob in planjobs:
        if planjob.scheduled_date is not None:
            return True

    return False


def change_limits(slots, inferior_limit=None, superior_limit=None):
    '''
    Recebe os slots de tempo disponiveis de um recurso e os retorna ajustados com
    os datetimes limitantes inferior e/ou superior
    :param slots: slots de tempo de um recurso {datea: [slots], ..., datez: [slots}}
    :param inferior_limit:
    :param superior_limit:
    :return:
    '''
    if inferior_limit is not None:
        dates = slots.keys()
        inferior_date = inferior_limit.date()

        for date_str in sorted(dates):
            date = datetime.strptime(date_str, DATE_FORMAT).date()
            if date < inferior_date:
                slots.pop(date_str)
            elif date == inferior_date:
                # remove or adjust intervals
                slots[date_str] = get_superior_intervals(slots[date_str], inferior_limit)

    if superior_limit is not None:
        dates = slots.keys()
        superior_date = superior_limit.date()

        for date_str in sorted(dates)[::-1]:
            date = datetime.strptime(date_str, DATE_FORMAT).date()
            if date > superior_date:
                slots.pop(date_str)
            elif date == superior_date:
                # remove or adjust intervals
                slots[date_str] = get_inferior_slots(slots[date_str], superior_limit)


def get_planjob_slots_from_potential_slots(planjob, potential_slots):
    """
    Recebe um potential_slots e retorna todos os slots de interseção separados por data
    do planjob passado como parâmetro
    :param planjob: planjob que se quer extrair as informações
    :param potential_slots: potential_slots de ondem será extraidas as informações
    :return:
    """
    result = {}

    for date in sorted(potential_slots.keys()):
        result[date] = []
        for slot_intersection in sorted(potential_slots[date]):
            planjobs = potential_slots[date][slot_intersection]
            slots = planjobs[planjob]
            most_early_finish = min([slot.finish_time for slot in slots])
            result[date].append(Slot(slot_intersection[0], slot_intersection[0], most_early_finish))

    return result


def get_superior_intervals(times, max_finish_date):
    indexes_to_remove = []
    time_limit = max_finish_date

    for i in range(len(times)):
        start = times[i].start_time
        finish = times[i].finish_time
        if finish <= time_limit:
            indexes_to_remove.append(i)
        elif start < time_limit < finish:
            times[i] = Slot(time_limit, time_limit, finish)

    indexes_to_remove.sort(reverse=True)
    for i in indexes_to_remove:
        times.pop(i)

    return times


def get_inferior_slots(slots, superior_limit):
    indexes_to_remove = []
    time_limit = superior_limit

    for i in range(len(slots)):
        start = slots[i].start_time
        finish = slots[i].finish_time
        if start >= time_limit:
            indexes_to_remove.append(i)
        elif start < time_limit < finish:
            slots[i] = Slot(start, start, time_limit)

    indexes_to_remove.sort(reverse=True)
    for i in indexes_to_remove:
        slots.pop(i)

    return slots


def get_date_format(datetime_):
    return datetime_.strptime(datetime_.strftime(DATE_FORMAT), DATE_FORMAT)


def time(datetime_):
    return datetime_.strftime(TIME_FORMAT)
