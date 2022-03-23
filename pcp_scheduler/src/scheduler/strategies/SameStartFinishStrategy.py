# coding: utf-8

import math

from datetime import timedelta
from collections import deque

from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler.SchedulerFilter import SchedulerFilter
from pcp_scheduler.utils import utils


class SameStartFinishStrategy:

    def __init__(self, planjobs, configs, all_planjobs, fractioned=False):
        self.planjobs = planjobs
        self.fractioned = fractioned
        self.configs = configs
        self.all_planjobs = all_planjobs

    def allocate(self):
        if self.fractioned:
            pass #Todo self.do_fractioned_allocation()
        else:
            filter = SchedulerFilter(self.planjobs, self.configs, self.all_planjobs, same_start=True)
            filter.filter()
            self.do_normal_allocation()

    def do_normal_allocation(self):
        requirements = build_schema(self.planjobs)
        reqs_on_head = self.get_reqs_on_head(requirements)
        start_times = self.get_start_dates_reqs_on_head(reqs_on_head)

        for start_time in start_times:
            found = self.try_to_find_allocation(start_time, requirements)
            if found: return

    def try_to_find_allocation(self, start_date, requirements):
        for req in requirements:
            planjob = get_planjob_by_id(self.planjobs, req.planjob_id)
            for slot in req.slots:
                real_slot = Slot(start_date, start_date+timedelta(minutes=slot[0]), start_date+timedelta(minutes=slot[1]))
                planjob.execution_slots.append(real_slot)
                for resource in planjob.allocated_resources:
                    date_str = start_date.strftime(utils.DATE_FORMAT)
                    if not resource.has_slot(date_str, real_slot):
                        self.clean_execution_slots(requirements)
                        return False
        return True

    def clean_execution_slots(self, requirements):
        for req in requirements:
            planjob = get_planjob_by_id(self.planjobs, req.planjob_id)
            planjob.execution_slots = []

    def get_reqs_on_head(self, requirements):
        reqs_on_head = []
        for req in requirements:
            if req.start() == 0:
                reqs_on_head.append(req)

        return reqs_on_head

    def get_start_dates_reqs_on_head(self, reqs_on_head):
        planjobs = [get_planjob_by_id(self.all_planjobs, req.id) for req in reqs_on_head]
        filter = SchedulerFilter(planjobs, self.configs, self.all_planjobs, same_start=True)
        return filter.get_start_dates_same_start_finish_planjobs()


class Requirement:
    def __init__(self, planjob, start=None, finish=None):
        self.id = planjob.id
        self.planjob_id = planjob.id
        self.planjob = planjob
        self.slots = []
        self.define_first_slot(start, finish)

    def __eq__(self, other):
        return isinstance(other, Requirement) and self.id == other.id

    def define_first_slot(self, start, finish):
        if start is not None and finish is None:
            self.slots = [(start, start+self.planjob.time+self.planjob.setup)]
        elif start is None and finish is not None:
            self.slots = [(finish-self.planjob.time-self.planjob.setup, finish)]
        else:
            self.slots = [(start, finish)]

    def start(self):
        return self.slots[0][0]

    def finish(self):
        return self.slots[-1][1]

    def add_break_to_start_in(self, new_start):
        time1, time2 = self.get_2_half_time(self.planjob)
        break_ = self.slots[-1][1] - new_start - time1 - time2
        slot1 = (new_start, new_start+time1)
        slot2 = (slot1[1]+break_, slot1[1]+break_+time2)
        self.slots = [slot1, slot2]

    def add_break_to_finish_in(self, new_finish):
        time1, time2 = self.get_2_half_time(self.planjob)
        slot2 = (new_finish - time2, new_finish)
        break_ = new_finish - self.slots[0][0] - time1 - time2
        slot1 = (slot2[0]-break_-time1, slot2[0]-break_)
        self.slots = [slot1, slot2]

    def get_2_half_time(self, planjob):
        '''
        Retorna dois times que somados são igual ao time do planjob, se o tempo do planjob é um valor par os times
        retornado são iguais, se for ímpar o primeiro time retornado é o teto da divisão do tempo do planjob por dois e
        o segundo é o piso da divisão do tempo do planjob por dois
        :param planjob: planjob alvo
        :return:
        '''
        return planjob.setup+math.ceil(planjob.time/2), planjob.setup+math.floor(planjob.time/2)


def build_schema(planjobs):
    '''
    Constroi o esquema como os planjobs se relacionam em relação as suas restrições de inicio-inicio e/ou fim-fim,
    montando os tempos que cada planjob deve começar, terminar e a quantidade de slots de execução que eles precisam
    ter pra cumprir todas as suas necessidades.
    O modelo retornado contém tempos ficticios e não os tempos exatos em datetime.
    :param planjobs: planjobs a montar o esquema
    :return: list<Requirement> uma lista de requirements de start e finish time dos planjobs
    '''
    queue = deque(sorted([planjob for planjob in planjobs], key=lambda p: p.time+p.setup, reverse=True))
    planjobs_grid = set([])
    requirements = []
    ss_links = set([])
    sf_links = set([])

    while len(queue) != 0:
        planjob = queue.popleft()
        if planjob not in planjobs_grid:
            planjobs_grid.add(planjob)
            req = Requirement(planjob, start=0)
            requirements.append(req)
        else:
            req = get_requirement(planjob.id, requirements)

        define_same_start_requirements(planjob, planjobs, planjobs_grid, queue, req, requirements, ss_links)
        define_same_finish_requirements(planjob, planjobs, planjobs_grid, queue, req, requirements, sf_links)

    return requirements


def define_same_finish_requirements(planjob, planjobs, planjobs_grid, queue, req, requirements, sf_links):
    '''
    Estabelece os links entre os planjobs que têm restrição de fim-fim com o planjob passado como parâmetro
    de forma a cumprir a exigência deles terminarem juntos
    :param planjob: planjob alvo
    :param planjobs: todos os planjobs quem têm alguma relação de inicio-incio e/ou fim-fim com os outros
    :param planjobs_grid: planjobs que já estão adicionados na grade de alocação
    :param queue: fila de planjobs ainda a processar
    :param req: requirement do planjob alvo
    :param requirements: lista de todos os requirements já criados
    :param sf_links: links encontrados até agora entre os planjobs que têm restrição de fim-fim
    :return:
    '''
    sf_queue = deque(sorted([get_planjob_by_id(planjobs, id) for id in planjob.same_finish],
                            key=lambda p: p.time + p.setup, reverse=True))
    while len(sf_queue) != 0:
        sibling = sf_queue.popleft()
        if sibling in planjobs_grid:
            req_sibling = get_requirement(sibling.id, requirements)

            if req_sibling.finish() == req.finish():
                add_link(sf_links, (planjob.id, sibling.id))
                continue
            elif req_sibling.finish() < req.finish():
                add_in_queue(sibling, queue)
                continue
            elif req_sibling.finish() > req.finish():
                req.add_break_to_finish_in(req_sibling.finish())
                sf_queue = deque(
                    sorted([get_planjob_by_id(planjobs, id) for id in planjob.same_finish if id != sibling.id],
                           key=lambda p: p.time + p.setup))
                add_link(sf_links, (planjob.id, sibling.id))
                continue
        else:
            req_sibling = Requirement(sibling, finish=req.finish())
            add_link(sf_links, (planjob.id, sibling.id))
            requirements.append(req_sibling)
            planjobs_grid.add(sibling)


def define_same_start_requirements(planjob, planjobs, planjobs_grid, queue, req, requirements, ss_links):
    '''
    Estabelece os links entre os planjobs que têm restrição de inicio-inicio com o planjob passado como parâmetro
    de forma a cumprir a exigência deles começarem juntos
    :param planjob: planjob alvo
    :param planjobs: todos os planjobs quem têm alguma relação de inicio-incio e/ou fim-fim com os outros
    :param planjobs_grid: planjobs que já estão adicionados na grade de alocação
    :param queue: fila de planjobs ainda a processar
    :param req: requirement do planjob alvo
    :param requirements: lista de todos os requirements já criados
    :param ss_links: links encontrados até agora entre os planjobs que têm restrição de inicio-incio
    :return:
    '''
    ss_queue = deque(sorted([get_planjob_by_id(planjobs, id) for id in planjob.same_start],
                            key=lambda p: p.time + p.setup, reverse=True))
    while len(ss_queue) != 0:
        sibling = ss_queue.popleft()
        if sibling in planjobs_grid:
            req_sibling = get_requirement(sibling.id, requirements)
            if req_sibling.start() == req.start():
                add_link(ss_links, (planjob.id, sibling.id))
                continue

            elif req_sibling.start() < req.start():
                req.add_break_to_start_in(req_sibling.start())
                ss_queue = deque(
                    sorted([get_planjob_by_id(planjobs, id) for id in planjob.same_start if id != sibling.id],
                           key=lambda p: p.time + p.setup))
                add_link(ss_links, (planjob.id, sibling.id))
                continue

            elif req_sibling.start() > req.start():
                add_in_queue(sibling, queue)
                continue
        else:
            req_sibling = Requirement(sibling, start=req.start())
            add_link(ss_links, (planjob.id, sibling.id))
            requirements.append(req_sibling)
            planjobs_grid.add(sibling)


def get_requirement(id, requirements):
    for requirement in requirements:
        if requirement.id == id:
            return requirement


def get_planjob_by_id(planjobs, id):
    '''
    Procura pelo planjob com o id passado com parâmetro na lista de planjobs, se ele esta na lista o retorna
    :param planjobs: lista de planjobs
    :param id: id do planjob desejado
    :return: planjob se ele está na lista, None caso contrário
    '''
    for planjob in planjobs:
        if planjob.id == id:
            return planjob


def add_in_queue(planjob, queue):
    '''
    Adiciona um planjob na fila se ele não está nela
    :param sibling: planjob a adicionar na fila
    :param queue: fila
    :return:
    '''
    if planjob not in queue:
        queue.append(planjob)


def add_link(links, link):
    '''
    Ordena o link e armazena ele em links se ele já não está lá
    :param links: set de tuplas de ids de planjobs
    :param link: tupla com dois ids de planjobs
    :return:
    '''
    ordered_link = tuple(sorted(link))
    links.add(ordered_link)
