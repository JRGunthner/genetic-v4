# coding: utf-8

from pcp_scheduler.mock import resources_mock
from pcp_scheduler.mock import configuration_mock

from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.src.model.ResourceCharacteristic import ResourceCharacteristic

def get_dependent_tasks():
    i = Planjob(1, "i", [1])
    c = Planjob(2, "c", [2])
    d = Planjob(4, "d", [3])
    a = Planjob(4, "a", [4])
    e = Planjob(3, "e", [5])
    f = Planjob(3, "f", [6])
    m = Planjob(2, "m", [7])

    i.successors.append('c')
    c.successors.append('d')
    d.successors.append('a')
    d.successors.append('e')
    f.successors.append('m')
    m.successors.append('e')

    c.predecessors.append('i')
    d.predecessors.append('c')
    a.predecessors.append('d')
    e.predecessors.append('d')
    m.predecessors.append('f')
    e.predecessors.append('m')
    return [i, c, d, a, e, f, m]

def get_3_dependent_tasks():
    # job A
    a1 = Planjob(30, 'a1', 1)
    a2 = Planjob(30, 'a2', 2)
    a3 = Planjob(30, 'a3', 3)
    a5 = Planjob(30, 'a5', 5)

    a1.successors.append('a2')
    a2.predecessors.append('a1')
    a2.successors.append('a3')
    a3.predecessors.append('a2')
    a3.successors.append('a5')
    a5.predecessors.append('a3')

    # job B
    b1 = Planjob(30, 'b1', 1)
    b2 = Planjob(30, 'b2', 2)
    b6 = Planjob(30, 'b6', 6)
    b7 = Planjob(30, 'b7', 7)

    b1.successors.append('b2')
    b2.predecessors.append('b1')
    b2.successors.append('b6')
    b6.predecessors.append('b2')
    b6.successors.append('b7')
    b7.predecessors.append('b6')

    a5.same_start.append('b6')
    b6.same_start.append('a5')
    return [a1, b1, b2, a2, a3, b6, b7, a5]

def get_10_dependent_tasks():
    impressora1 = DesiredResource([ResourceCharacteristic(resources=[resources_mock.impressora1.id], hour_type=2)])
    ana = DesiredResource([ResourceCharacteristic(resources=[resources_mock.ana.id], hour_type=1)])
    joao = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.joao.id])])
    pedro = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.pedro.id])])
    luisa = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.luisa.id])])
    maria = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.maria.id])])

    # job A
    a1 = Planjob(45, 'a1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    a2 = Planjob(65, 'a2', [ana], configs=configuration_mock.get_default_configs_planjob())
    a3 = Planjob(50, 'a3', [joao], configs=configuration_mock.get_default_configs_planjob())
    a5 = Planjob(55, 'a5', [pedro], configs=configuration_mock.get_default_configs_planjob())
    a6 = Planjob(30, 'a6', [luisa], configs=configuration_mock.get_default_configs_planjob())

    a1.successors.append('a2')
    a2.predecessors.append('a1')
    a2.successors.append('a3')
    a3.predecessors.append('a2')
    a3.successors.append('a5')
    a5.predecessors.append('a3')
    a5.successors.append('a6')
    a6.predecessors.append('a5')

    # job B
    b1 = Planjob(70, 'b1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    b2 = Planjob(65, 'b2', [ana], configs=configuration_mock.get_default_configs_planjob())
    b3 = Planjob(35, 'b3', [joao], configs=configuration_mock.get_default_configs_planjob())
    b4 = Planjob(40, 'b4', [ana], configs=configuration_mock.get_default_configs_planjob())
    b6 = Planjob(55, 'b6', [luisa], configs=configuration_mock.get_default_configs_planjob())
    b7 = Planjob(20, 'b7', [maria], configs=configuration_mock.get_default_configs_planjob())

    b1.successors.append('b2')
    b2.predecessors.append('b1')
    b2.successors.append('b3')
    b2.successors.append('b6')
    b3.predecessors.append('b2')
    b6.predecessors.append('b2')
    b3.successors.append('b4')
    b4.predecessors.append('b3')
    b6.successors.append('b7')
    b7.predecessors.append('b6')

    # job  C
    c1 = Planjob(60, 'c1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    c7 = Planjob(25, 'c7', [luisa], configs=configuration_mock.get_default_configs_planjob())

    # job D
    d1 = Planjob(20, 'd1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    d2 = Planjob(30, 'd2', [ana], configs=configuration_mock.get_default_configs_planjob())
    d3 = Planjob(15, 'd3', [joao], configs=configuration_mock.get_default_configs_planjob())

    d1.successors.append('d2')
    d1.successors.append('d3')
    d2.predecessors.append('d1')
    d3.predecessors.append('d1')

    # job D
    e1 = Planjob(50, 'e1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    e5 = Planjob(35, 'e5', [pedro], configs=configuration_mock.get_default_configs_planjob())
    e6 = Planjob(45, 'e6', [luisa], configs=configuration_mock.get_default_configs_planjob())
    e7 = Planjob(30, 'e7', [maria], configs=configuration_mock.get_default_configs_planjob())

    e1.successors.append('e5')
    e5.predecessors.append('e1')
    e1.successors.append('e6')
    e6.predecessors.append('e1')

    e5.successors.append('e7')
    e6.successors.append('e7')
    e7.predecessors.append('e5')
    e7.predecessors.append('e6')

    # job D
    f1 = Planjob(20, 'f1', [impressora1], configs=configuration_mock.get_default_configs_planjob())

    # job D
    g1 = Planjob(20, 'g1', [impressora1], configs=configuration_mock.get_default_configs_planjob())

    # job D
    h1 = Planjob(20, 'h1', [impressora1], configs=configuration_mock.get_default_configs_planjob())

    # job D
    i1 = Planjob(20, 'i1', [impressora1], configs=configuration_mock.get_default_configs_planjob())

    c1.successors.append('c7')
    c7.predecessors.append('c1')

    a5.same_start.append('b6')
    b6.same_start.append('a5')
    c1.same_start.append('a2')
    a2.same_start.append('c1')
    e7.same_start.append('b2')
    b2.same_start.append('e7')

    e6.same_finish.append('b1')
    b1.same_finish.append('e6')
    return [a1, b1, d1, e1, e5, e6, e7, f1, g1, h1, i1, b2, a2, a3, b6, b7, a5, c1, c7, a6, b3, b4, d2, d3]

def get_100_dependent_tasks():
    impressora01 = DesiredResource([ResourceCharacteristic(resources=[resources_example4.impressora01.id], hour_type=2)])
    impressora02 = DesiredResource([ResourceCharacteristic(resources=[resources_example4.impressora02.id], hour_type=2)])
    aline = DesiredResource([ResourceCharacteristic(resources=[resources_example4.aline.id], hour_type=1)])
    guilherme = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.guilherme.id])])
    camila = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.camila.id])])
    gabriel = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.gabriel.id])])
    jean = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.jean.id])])

    marta = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.marta.id])])
    wagner = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.wagner.id])])
    maisa = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.maisa.id])])
    danieli = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.danieli.id])])
    vinicius = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.vinicius.id])])
    yuri = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.yuri.id])])
    raquel = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.raquel.id])])
    inaldo = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.inaldo.id])])
    thaila = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.thaila.id])])
    marcos = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.marcos.id])])
    marcelo = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.marcelo.id])])
    sulina = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.sulina.id])])
    isabela = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.isabela.id])])
    nilton = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.nilton.id])])
    liliane = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.liliane.id])])
    wesley = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.wesley.id])])
    fabio = DesiredResource([ResourceCharacteristic(1, resources=[resources_example4.fabio.id])])

    # job A
    a1 = Planjob(45, 'a1', [impressora01], configs=configuration_mock.get_default_configs_planjob())
    a2 = Planjob(65, 'a2', [aline], configs=configuration_mock.get_default_configs_planjob())
    a3 = Planjob(50, 'a3', [guilherme], configs=configuration_mock.get_default_configs_planjob())
    a5 = Planjob(55, 'a5', [camila], configs=configuration_mock.get_default_configs_planjob())
    a6 = Planjob(30, 'a6', [gabriel], configs=configuration_mock.get_default_configs_planjob())

    a1.successors.append('a2')
    a2.predecessors.append('a1')
    a2.successors.append('a3')
    a3.predecessors.append('a2')
    a3.successors.append('a5')
    a5.predecessors.append('a3')
    a5.successors.append('a6')
    a6.predecessors.append('a5')

    # job B
    b1 = Planjob(70, 'b1', [impressora01], configs=configuration_mock.get_default_configs_planjob())
    b2 = Planjob(65, 'b2', [aline], configs=configuration_mock.get_default_configs_planjob())
    b3 = Planjob(35, 'b3', [guilherme], configs=configuration_mock.get_default_configs_planjob())
    b4 = Planjob(40, 'b4', [aline], configs=configuration_mock.get_default_configs_planjob())
    b6 = Planjob(55, 'b6', [gabriel], configs=configuration_mock.get_default_configs_planjob())
    b7 = Planjob(20, 'b7', [jean], configs=configuration_mock.get_default_configs_planjob())

    b1.successors.append('b2')
    b2.predecessors.append('b1')
    b2.successors.append('b3')
    b2.successors.append('b6')
    b3.predecessors.append('b2')
    b6.predecessors.append('b2')
    b3.successors.append('b4')
    b4.predecessors.append('b3')
    b6.successors.append('b7')
    b7.predecessors.append('b6')

    # job  C
    c1 = Planjob(60, 'c1', [impressora01], configs=configuration_mock.get_default_configs_planjob())
    c7 = Planjob(25, 'c7', [gabriel], configs=configuration_mock.get_default_configs_planjob())

    # job D
    d1 = Planjob(20, 'd1', [impressora01], configs=configuration_mock.get_default_configs_planjob())
    d2 = Planjob(30, 'd2', [aline], configs=configuration_mock.get_default_configs_planjob())
    d3 = Planjob(15, 'd3', [guilherme], configs=configuration_mock.get_default_configs_planjob())

    d1.successors.append('d2')
    d1.successors.append('d3')
    d2.predecessors.append('d1')
    d3.predecessors.append('d1')

    # job D
    e1 = Planjob(50, 'e1', [impressora01], configs=configuration_mock.get_default_configs_planjob())
    e5 = Planjob(35, 'e5', [camila], configs=configuration_mock.get_default_configs_planjob())
    e6 = Planjob(45, 'e6', [gabriel], configs=configuration_mock.get_default_configs_planjob())
    e7 = Planjob(30, 'e7', [jean], configs=configuration_mock.get_default_configs_planjob())

    e1.successors.append('e5')
    e5.predecessors.append('e1')
    e1.successors.append('e6')
    e6.predecessors.append('e1')

    e5.successors.append('e7')
    e6.successors.append('e7')
    e7.predecessors.append('e5')
    e7.predecessors.append('e6')

    # job D
    f1 = Planjob(20, 'f1', [impressora01], configs=configuration_mock.get_default_configs_planjob())

    # job D
    g1 = Planjob(20, 'g1', [impressora01], configs=configuration_mock.get_default_configs_planjob())

    # job D
    h1 = Planjob(20, 'h1', [impressora01], configs=configuration_mock.get_default_configs_planjob())

    # job D
    i1 = Planjob(20, 'i1', [impressora01], configs=configuration_mock.get_default_configs_planjob())

    c1.successors.append('c7')
    c7.predecessors.append('c1')

    a5.same_start.append('b6')
    b6.same_start.append('a5')
    c1.same_start.append('a2')
    a2.same_start.append('c1')
    e7.same_start.append('b2')
    b2.same_start.append('e7')

    e6.same_finish.append('b1')
    b1.same_finish.append('e6')
    return [a1, b1, d1, e1, e5, e6, e7, f1, g1, h1, i1, b2, a2, a3, b6, b7, a5, c1, c7, a6, b3, b4, d2, d3]

def get_tasks_resources_granularity():
    impressora1 = DesiredResource([ResourceCharacteristic(resources=[resources_mock.impressora1.id], hour_type=2)])
    ana = DesiredResource([ResourceCharacteristic(resources=[resources_mock.ana.id], hour_type=1)])
    joao = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.joao.id])])
    pedro = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.pedro.id])])
    luisa = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.luisa.id])])
    maria = DesiredResource([ResourceCharacteristic(1, resources=[resources_mock.maria.id])])

    # job A
    a1 = Planjob(30, 'a1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    a2 = Planjob(30, 'a2', [ana], configs=configuration_mock.get_default_configs_planjob())
    a3 = Planjob(30, 'a3', [joao], configs=configuration_mock.get_default_configs_planjob())
    a5 = Planjob(30, 'a5', [pedro], configs=configuration_mock.get_default_configs_planjob())

    a1.successors.append('a2')
    a2.predecessors.append('a1')
    a2.successors.append('a3')
    a3.predecessors.append('a2')
    a3.successors.append('a5')
    a5.predecessors.append('a3')

    # job B
    b1 = Planjob(30, 'b1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    b2 = Planjob(30, 'b2', [ana], configs=configuration_mock.get_default_configs_planjob())
    b6 = Planjob(30, 'b6', [luisa], configs=configuration_mock.get_default_configs_planjob())
    b7 = Planjob(30, 'b7', [maria], configs=configuration_mock.get_default_configs_planjob())

    b1.successors.append('b2')
    b2.predecessors.append('b1')
    b2.successors.append('b6')
    b6.predecessors.append('b2')
    b6.successors.append('b7')
    b7.predecessors.append('b6')

    # job  C
    c1 = Planjob(30, 'c1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    c6 = Planjob(15, 'c6', [luisa], configs=configuration_mock.get_default_configs_planjob())

    c1.successors.append('c6')
    c6.predecessors.append('c1')

    a5.same_start.append('b6')
    b6.same_start.append('a5')
    c1.same_start.append('a2')
    a2.same_start.append('c1')

    c6.same_finish.append('b7')
    b7.same_finish.append('c6')
    return [a1, b1, b2, a2, a3, b6, b7, a5, c1, c6]

def get_tasks_groups_granularity():
    impressora1 = DesiredResource([ResourceCharacteristic(resources=[resources_mock.impressora1.id], hour_type=2)])
    ana = DesiredResource([ResourceCharacteristic(resources=[resources_mock.ana.id], hour_type=1)])
    joao = DesiredResource([ResourceCharacteristic(resources=[resources_mock.joao.id], hour_type=1)])
    luisa = DesiredResource([ResourceCharacteristic(resources=[resources_mock.luisa.id], hour_type=1)])
    maria = DesiredResource([ResourceCharacteristic(resources=[resources_mock.maria.id], hour_type=1)])
    detalhista = DesiredResource([ResourceCharacteristic(groups=["detalhista"], hour_type=1)])

    # job A
    a1 = Planjob(30, 'a1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    a2 = Planjob(30, 'a2', [ana], configs=configuration_mock.get_default_configs_planjob())
    a3 = Planjob(30, 'a3', [joao], configs=configuration_mock.get_default_configs_planjob())
    a5 = Planjob(30, 'a5', [detalhista], configs=configuration_mock.get_default_configs_planjob())

    a1.successors.append('a2')
    a2.predecessors.append('a1')
    a2.successors.append('a3')
    a3.predecessors.append('a2')
    a3.successors.append('a5')
    a5.predecessors.append('a3')

    # job B
    b1 = Planjob(30, 'b1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    b2 = Planjob(30, 'b2', [ana], configs=configuration_mock.get_default_configs_planjob())
    b6 = Planjob(30, 'b6', [detalhista], configs=configuration_mock.get_default_configs_planjob())
    b7 = Planjob(30, 'b7', [maria], configs=configuration_mock.get_default_configs_planjob())

    b1.successors.append('b2')
    b2.predecessors.append('b1')
    b2.successors.append('b6')
    b6.predecessors.append('b2')
    b6.successors.append('b7')
    b7.predecessors.append('b6')

    # job  C
    c1 = Planjob(30, 'c1', [impressora1], configs=configuration_mock.get_default_configs_planjob())
    c6 = Planjob(15, 'c6', [luisa], configs=configuration_mock.get_default_configs_planjob())

    c1.successors.append('c6')
    c6.predecessors.append('c1')

    a5.same_start.append('b6')
    b6.same_start.append('a5')
    c1.same_start.append('a2')
    a2.same_start.append('c1')

    c6.same_finish.append('b7')
    b7.same_finish.append('c6')
    return [a1, b1, b2, a2, a3, b6, b7, a5, c1, c6]

def get_tasks_sectors_granularity():
    impressao = DesiredResource([ResourceCharacteristic(sectors=["impressão"], hour_type=2)])
    acabamento = DesiredResource([ResourceCharacteristic(sectors=["acabamento"], hour_type=1)])

    # job A
    a1 = Planjob(30, 'a1', [impressao], configs=configuration_mock.get_default_configs_planjob())
    a2 = Planjob(30, 'a2', [acabamento], configs=configuration_mock.get_default_configs_planjob())
    a3 = Planjob(30, 'a3', [acabamento], configs=configuration_mock.get_default_configs_planjob())
    a5 = Planjob(30, 'a5', [acabamento], configs=configuration_mock.get_default_configs_planjob())

    a1.successors.append('a2')
    a2.predecessors.append('a1')
    a2.successors.append('a3')
    a3.predecessors.append('a2')
    a3.successors.append('a5')
    a5.predecessors.append('a3')

    # job B
    b1 = Planjob(30, 'b1', [impressao], configs=configuration_mock.get_default_configs_planjob())
    b2 = Planjob(30, 'b2', [acabamento], configs=configuration_mock.get_default_configs_planjob())
    b6 = Planjob(30, 'b6', [acabamento], configs=configuration_mock.get_default_configs_planjob())
    b7 = Planjob(30, 'b7', [acabamento], configs=configuration_mock.get_default_configs_planjob())

    b1.successors.append('b2')
    b2.predecessors.append('b1')
    b2.successors.append('b6')
    b6.predecessors.append('b2')
    b6.successors.append('b7')
    b7.predecessors.append('b6')

    # job  C
    c1 = Planjob(30, 'c1', [impressao], configs=configuration_mock.get_default_configs_planjob())
    c6 = Planjob(15, 'c6', [acabamento], configs=configuration_mock.get_default_configs_planjob())

    c1.successors.append('c6')
    c6.predecessors.append('c1')

    a5.same_start.append('b6')
    b6.same_start.append('a5')
    c1.same_start.append('a2')
    a2.same_start.append('c1')

    c6.same_finish.append('b7')
    b7.same_finish.append('c6')

    return [a1, b1, b2, a2, a3, b6, b7, a5, c1, c6]
