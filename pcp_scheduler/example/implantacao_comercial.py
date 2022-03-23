# coding: utf-8
from __future__ import print_function

from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Configuration import Configuration
from pcp_scheduler.src.model.Resource import Resource
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.mock import resources_mock
from pcp_scheduler.src.scheduler import scheduler_ag

# Criando recursos
maria = Resource("maria", "maria", ["comercial"], ["implantacao_basico", "implantacao_avancado", "gerente"], 1)
aline = Resource("aline", "aline", ["comercial"], ["implantacao_basico", "implantacao_avancado", "vendedor"], 1)
guilherme = Resource("guilherme", "guilherme", ["comercial"], ["implantacao_basico", "implantacao_avancado", "custeio", "vendedor"], 1)
camila = Resource("camila", "camila", ["comercial"], ["implantacao_basico", "vendedor"], 1)
gabriel = Resource("gabriel", "gabriel", ["comercial"], ["implantacao_basico", "vendedor"], 1)
jean = Resource("jean", "jean", ["comercial"], ["atendimento"], 1)
wagner = Resource("wagner", "wagner", ["comercial"], ["implantacao_basico", "treinador"], 1)

# Criando recursos other
maisa = Resource("maisa", "maisa", hour_type=1)
danieli = Resource("danieli", "danieli", hour_type=1)
vinicius = Resource("vinicius", "vinicius", hour_type=1)
yuri = Resource("yuri", "yuri", hour_type=1)
raquel = Resource("raquel", "raquel", hour_type=1)
inaldo = Resource("inaldo", "inaldo", hour_type=1)
thaila = Resource("thaila", "thaila", hour_type=1)
marcos = Resource("marcos", "marcos", hour_type=1)
marcelo = Resource("marcelo", "marcelo", hour_type=1)
sulina = Resource("sulina", "sulina", hour_type=1)
isabela = Resource("isabela", "isabela", hour_type=1)
nilton = Resource("nilton", "nilton", hour_type=1)
liliane = Resource("liliane", "liliane", hour_type=1)
wesley = Resource("wesley", "wesley", hour_type=1)
fabio = Resource("fabio", "fabio", hour_type=1)

grid = {
    maisa: resources_mock.um_mes_livre(mes=8),
    danieli: resources_mock.um_mes_livre(mes=8),
    vinicius: resources_mock.um_mes_livre(mes=8),
    yuri: resources_mock.um_mes_livre(mes=8),
    raquel: resources_mock.um_mes_livre(mes=8),
    inaldo: resources_mock.um_mes_livre(mes=8),
    thaila: resources_mock.um_mes_livre(mes=8),
    marcos: resources_mock.um_mes_livre(mes=8),
    marcelo: resources_mock.um_mes_livre(mes=8),
    sulina: resources_mock.um_mes_livre(mes=8),
    isabela: resources_mock.um_mes_livre(mes=8),
    nilton: resources_mock.um_mes_livre(mes=8),
    liliane: resources_mock.um_mes_livre(mes=8),
    wesley: resources_mock.um_mes_livre(mes=8),
    fabio: resources_mock.um_mes_livre(mes=8),
    maria: resources_mock.um_mes_livre(mes=8),
    aline: resources_mock.um_mes_livre(mes=8),
    guilherme: resources_mock.um_mes_livre(mes=8),
    camila: resources_mock.um_mes_livre(mes=8),
    gabriel: resources_mock.um_mes_livre(mes=8),
    jean: resources_mock.um_mes_livre(mes=8),
    wagner: resources_mock.um_mes_livre(mes=8),
}

#Criando desired resources
implantacao_basico = DesiredResource(1, groups=["implantacao_basico"])
implantacao_avancado = DesiredResource(1, groups=["implantacao_avancado"])
misto = DesiredResource(1, groups=["implantacao_avancado", "implantacao_basico"])
custeio = DesiredResource(1, groups=["custeio"])
vendedor = DesiredResource(1, groups=["vendedor"])
treinador = DesiredResource(1, groups=["treinador"])

# Criando tasks
tren_c11 = Planjob(60, "c11", [DesiredResource(1, resources=["danieli"]), implantacao_basico])
tren_c12 = Planjob(60, "c12", [DesiredResource(1, resources=["vinicius"]), implantacao_basico])
tren_c13 = Planjob(60, "c13", [DesiredResource(1, resources=["yuri"]), implantacao_basico])
tren_c14 = Planjob(60, "c14", [DesiredResource(1, resources=["raquel"]), implantacao_basico])
tren_c15 = Planjob(60, "c15", [DesiredResource(1, resources=["inaldo"]), implantacao_basico])
tren_c16 = Planjob(60, "c16", [DesiredResource(1, resources=["thaila"]), implantacao_basico])

tren_c17 = Planjob(60, "c17", [DesiredResource(1, resources=["maisa"]), implantacao_avancado])
tren_d17 = Planjob(60, "d17", [DesiredResource(1, resources=["maisa"]), implantacao_avancado])
tren_e17 = Planjob(60, "e17", [DesiredResource(1, resources=["maisa"]), implantacao_avancado])
tren_f17 = Planjob(60, "f17", [DesiredResource(1, resources=["maisa"]), implantacao_avancado])
tren_g17 = Planjob(60, "g17", [DesiredResource(1, resources=["maisa"]), implantacao_avancado])
tren_h17 = Planjob(60, "h17", [DesiredResource(1, resources=["maisa"]), implantacao_avancado])
tren_i17 = Planjob(60, "i17", [DesiredResource(1, resources=["maisa"]), implantacao_avancado])
tren_c17.successors.append('d17')
tren_d17.predecessors.append('c17')

tren_d17.successors.append('e17')
tren_e17.predecessors.append('d17')

tren_e17.successors.append('f17')
tren_f17.predecessors.append('e17')

tren_f17.successors.append('g17')
tren_g17.predecessors.append('f17')

tren_g17.successors.append('h17')
tren_h17.predecessors.append('g17')

tren_h17.successors.append('i17')
tren_i17.predecessors.append('h17')

tren_c18 = Planjob(60, "c18", [DesiredResource(1, resources=["marcos"]), implantacao_avancado])
tren_d18 = Planjob(60, "d18", [DesiredResource(1, resources=["marcos"]), implantacao_avancado, DesiredResource(1, resources=["nilton"])])
tren_e18 = Planjob(60, "e18", [DesiredResource(1, resources=["marcos"]), implantacao_avancado])
tren_f18 = Planjob(60, "f18", [DesiredResource(1, resources=["marcos"]), implantacao_avancado])

tren_c18.successors.append('d18')
tren_d18.predecessors.append('c18')
tren_d18.successors.append('e18')
tren_e18.predecessors.append('d18')
tren_e18.successors.append('f18')
tren_f18.predecessors.append('e18')

tren_c19 = Planjob(60, "c19", [DesiredResource(1, resources=["marcelo"]), implantacao_avancado])
tren_d19 = Planjob(60, "d19", [DesiredResource(1, resources=["marcelo"]), implantacao_avancado])
tren_c19.successors.append('d19')
tren_d19.predecessors.append('c19')

tren_c20 = Planjob(60, "c20", [DesiredResource(1, resources=["sulina"]), implantacao_avancado])
tren_d20 = Planjob(60, "d20", [DesiredResource(1, resources=["sulina"]), implantacao_avancado])
tren_e20 = Planjob(60, "e20", [DesiredResource(1, resources=["sulina"]), implantacao_avancado])
tren_c20.successors.append('d20')
tren_d20.predecessors.append('c20')

tren_d20.successors.append('e20')
tren_e20.predecessors.append('d20')

tren_c21 = Planjob(60, "c21", [DesiredResource(1, resources=["isabela"]), implantacao_basico])
tren_d21 = Planjob(60, "d21", [DesiredResource(1, resources=["isabela"]), implantacao_avancado])
tren_e21 = Planjob(60, "e21", [DesiredResource(1, resources=["isabela"]), implantacao_avancado])
tren_f21 = Planjob(60, "f21", [DesiredResource(1, resources=["isabela"]), misto])
tren_c21.successors.append('d21')
tren_d21.predecessors.append('c21')

tren_d21.successors.append('e21')
tren_e21.predecessors.append('d21')

tren_e21.successors.append('f21')
tren_f21.predecessors.append('e21')

tren_c22 = Planjob(60, "c22", [DesiredResource(1, resources=["nilton"]), implantacao_avancado])
tren_d22 = Planjob(60, "d22", [DesiredResource(1, resources=["nilton"]), implantacao_avancado])
tren_c22.successors.append('d22')
tren_d22.predecessors.append('c22')

tren_c23 = Planjob(60, "c23", [DesiredResource(1, resources=["liliane"]), implantacao_avancado])
tren_c24 = Planjob(60, "c24", [DesiredResource(1, resources=["wesley"]), implantacao_avancado])
tren_c25 = Planjob(60, "c25", [DesiredResource(1, resources=["fabio"]), implantacao_avancado])

tasks = [tren_c11, tren_c12, tren_c13, tren_c14, tren_c15, tren_c16, tren_c17, tren_c18, tren_c19, tren_c20, tren_c21,
         tren_c22, tren_c23, tren_c24, tren_c25, tren_d17, tren_d18, tren_d19, tren_d20, tren_d21, tren_d22, tren_e17,
         tren_e18, tren_e20, tren_e21, tren_f17, tren_f18, tren_f21, tren_g17, tren_h17, tren_i17]

def main():
    configs = Configuration()
    configs.groups_as_subset = True
    tasks2 = scheduler_ag.generate_allocation(grid, tasks, configs)

    for task in tasks2:
        resources = [allocated_resource.id for allocated_resource in task.allocated_resources]
        utc_date_start = task.start_date.strftime('%Y,%m,%d,%H,%M')
        utc_date_finish = task.finish_date.strftime('%Y,%m,%d,%H,%M')
        dependencies = ','.join([s for s in task.predecessors])
        dependencies = "'" + dependencies + "'" if dependencies != '' else 'null'
        print("['%s', '%s', \"%s\", new Date(%s), new Date(%s), minutesToMilliseconds(30), 100, %s]," % (
            task.id, task.id, resources, utc_date_start, utc_date_finish, dependencies))


if __name__ == "__main__":
    main()
