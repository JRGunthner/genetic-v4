# coding: utf-8

from datetime import datetime, timedelta
from copy import deepcopy

from . import journey_mock
from pcp_scheduler.src.model.Resource import Resource
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.ProcessLoadInformation import ProcessLoadInformation

from pcp_scheduler.utils import utils

def get_impressora1():
    return Resource("1", "impressora mimaki", ["impressão"], ["mimaki"], 2)

def get_impressora2():
    return Resource("2", "impressora mimaki power", ["impressão"], ["mimaki", "high-quality"], 2)

def get_joao():
    return Resource("3", "joao", ["acabamento"], ["top"], 1)

def get_pedro():
    return Resource("4", "pedro", ["acabamento", "pre-impressão"], ["detalhista"], 1)

def get_maria():
    return Resource("5", "maria", ["acabamento"], [], 1)

def get_ana():
    ana_ = Resource("6", "ana", ["acabamento"], [], 1)
    ana_.journey = journey_mock.get_journey_default()
    return ana_

def get_ricardo():
    return Resource("7", "ricardo", ["acabamento"], [], 1)

def get_luisa():
    return Resource("8", "luisa", ["acabamento"], ["detalhista"], 1)

luisa = get_luisa()
ricardo = get_ricardo()
ana = get_ana()
maria = get_maria()
pedro = get_pedro()
joao = get_joao()
impressora1 = get_impressora1()
impressora2 = get_impressora2()


def um_mes_livre(mes=6, ano=2019):
    limite = 32 if mes in [1, 3, 5, 7, 8, 10, 12] else 31
    limite = 29 if mes == 2 else limite
    month = {}
    for i in range(1, limite):
        date_str = datetime(ano, mes, i).strftime("%Y/%m/%d")
        month[date_str] = [Slot(datetime(ano, mes, i), datetime(ano, mes, i, 9), datetime(ano, mes, i, 12)),
                           Slot(datetime(ano, mes, i), datetime(ano, mes, i, 13), datetime(ano, mes, i, 18))]
    return month


def uma_semana_livre(mes=6, ano=2019):
    week = {}
    for i in range(1, 8):
        date_str = datetime(ano, mes, i).strftime("%Y/%m/%d")
        week[date_str] = [Slot(datetime(ano, mes, i), datetime(ano, mes, i, 9), datetime(ano, mes, i, 12)),
                           Slot(datetime(ano, mes, i), datetime(ano, mes, i, 13), datetime(ano, mes, i, 18))]
    return week


def um_dia_livre(date):
    date_str = datetime(date.year, date.month, date.day).strftime("%Y/%m/%d")
    month = {}
    month[date_str] = [Slot(datetime(date.year, date.month, date.day), datetime(date.year, date.month, date.day, 9),
                            datetime(date.year, date.month, date.day, 12)),
                       Slot(datetime(date.year, date.month, date.day), datetime(date.year, date.month, date.day, 13),
                            datetime(date.year, date.month, date.day, 18))]
    return month


def dois_dias_livres_seguidos(date):
    date_str = datetime(date.year, date.month, date.day).strftime("%Y/%m/%d")
    month = {}
    month[date_str] = [Slot(datetime(date.year, date.month, date.day), datetime(date.year, date.month, date.day, 9),
                            datetime(date.year, date.month, date.day, 12)),
                       Slot(datetime(date.year, date.month, date.day), datetime(date.year, date.month, date.day, 13),
                            datetime(date.year, date.month, date.day, 18))]

    date_next = date + timedelta(days=1)
    date_str_next = datetime(date_next.year, date_next.month, date_next.day).strftime("%Y/%m/%d")
    month[date_str_next] = [Slot(datetime(date_next.year, date_next.month, date_next.day),
                                 datetime(date_next.year, date_next.month, date_next.day, 9),
                                 datetime(date_next.year, date_next.month, date_next.day, 12)),
                            Slot(datetime(date_next.year, date_next.month, date_next.day),
                                 datetime(date_next.year, date_next.month, date_next.day, 13),
                                 datetime(date_next.year, date_next.month, date_next.day, 18))]
    return month


def grid_todo_livre():
    grid = [impressora1, impressora2, joao, pedro, maria, ana, ricardo, luisa]
    for resource in grid:
        resource.available_slots = um_mes_livre()
        resource.journey = journey_mock.get_journey_default()

    return grid


def get_current_slot_resource(planjob):
    date_str = datetime(2019, 7, 18).strftime("%Y/%m/%d")
    current = {
                date_str: {
                    (datetime(2019, 7, 18, 8, 4), datetime(2019, 7, 18, 8, 8)): {planjob: [Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 4), datetime(2019, 7, 18, 8, 8))]},
                    (datetime(2019, 7, 18, 8, 15), datetime(2019, 7, 18, 8, 45)): {planjob: [Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 15), datetime(2019, 7, 18, 8, 45))]},
                }
              }
    return current


def get_single_resource_slots():
    date_str = datetime(2019, 7, 18).strftime("%Y/%m/%d")
    resource_allocation = {
                date_str: [
                    Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 3),  datetime(2019, 7, 18, 8, 4)), Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 5),  datetime(2019, 7, 18, 8, 13)),
                    Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 17),  datetime(2019, 7, 18, 8, 25)), Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 32),  datetime(2019, 7, 18, 8, 43)),
                    Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 54),  datetime(2019, 7, 18, 8, 56)), Slot(datetime(2019, 7, 18), datetime(2019, 7, 18, 8, 58),  datetime(2019, 7, 18, 8, 59))
                ]
            }
    return resource_allocation


def get_date_load_informations(data, process_id, planjob_id=0, time=240):
    process_info = ProcessLoadInformation(process_id)
    process_info.register_load_info(planjob_id, time)

    return {data: [process_info]}


def get_scheduler_by_journey(journey, mes=5, ano=2019):
    month = {}
    for day in range(1, 32):
        data = datetime(ano, mes, day)
        for daily_journey in journey.daily_journeys:
            if daily_journey.day_of_weekday == data.weekday():
                date_str = data.strftime(utils.DATE_FORMAT)
                start_time = datetime(ano, mes, day, daily_journey.start_time.hour, daily_journey.start_time.minute)
                finish_time = datetime(ano, mes, day, daily_journey.finish_time.hour, daily_journey.finish_time.minute)
                if daily_journey.finish_time.time() <= daily_journey.start_time.time():
                    finish_time += timedelta(days=1)
                month[date_str] = month.get(date_str, [])
                month[date_str].append(Slot(start_time, start_time, finish_time))

    return month
