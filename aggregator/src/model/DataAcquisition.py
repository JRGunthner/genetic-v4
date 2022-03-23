# coding: utf-8

import unittest
import numpy as nd
import pandas as pd
import json
import traceback
import webbrowser

from encoder.encoder import deserializer_file, serializer
from pcp_scheduler.src.scheduler.scheduler import Allocator
from pcp_scheduler.src.scheduler.scheduler_ag import generate_allocation
from pcp_scheduler.src.exceptions import Exceptions

file_list_resources = 'general_tests\lista_recursos.json'
file_list_processes = 'general_tests\lista_processos.json'
file_list_materials = 'general_tests\lista_materiais.json'
file_list_outsourceds = 'general_tests\lista_terceirizados.json'
file_list_jobs = 'general_tests\lista_jobs.json'
file_list_products = 'general_tests\lista_produtos.json'


class SerializedTestCase(unittest.TestCase):

    @staticmethod
    def test_serialize_file():
        list_resources = deserializer_file(file_list_resources)
        list_processes = deserializer_file(file_list_processes)
        list_materials = deserializer_file(file_list_materials)
        list_outsourceds = deserializer_file(file_list_outsourceds)
        list_jobs = deserializer_file(file_list_jobs)
        list_products = deserializer_file(file_list_products)

        all_resources = serializer(list_resources)
        all_processes = serializer(list_processes)
        all_materials = serializer(list_materials)
        all_outsourceds = serializer(list_outsourceds)
        all_jobs = serializer(list_jobs)
        all_products = serializer(list_products)

        print(all_resources)
        print(all_processes)
        print(all_materials)
        print(all_outsourceds)
        print(all_jobs)
        print(all_products)

    @staticmethod
    def test_allocator_from_file():
        content = deserializer_file(file_to_test)
        grid = content['grid']
        planjobs = content['planjobs']
        configs = content['configs']

        allocator = Allocator(grid, planjobs, configs)
        allocator.generate_allocation()

    @staticmethod
    def test_scheduler_from_file():
        content = deserializer_file(file_to_test)

        grid = content['grid']
        planjobs = content['planjobs']
        configs = content['configs']
        non_working_days = content.get("non_working_days", [])

        result = generate_allocation(grid, planjobs, configs, non_working_days)
        to_gantt = serializer(result)
        print(to_gantt)

    @staticmethod
    def test_application_allocate_planjobs():
        try:
            data = deserializer_file(file_to_test)

        except Exception as e:
            response = {"reason": e.__class__.__name__, "informations": {"traceback": traceback.format_exc()}}
            print(response)
            return serializer(response), 400

        grid = data['grid']
        planjobs = data['planjobs']
        configs = data['configs']
        non_working_days = data.get("non_working_days", [])

        list_id = []
        list_name = []
        for name in range(len(grid)):
            list_id.append(grid[name].id)
            list_name.append(grid[name].name)
        dict_name_id = dict(zip(list_id, list_name))

        try:
            response = generate_allocation(grid, planjobs, configs, non_working_days)
            status_code = 200
        except Exceptions.InsufficientResourcesException as e1:
            response = {"reason": "InsufficientResourcesException", 'informations': e1.value}
            status_code = 400
        except Exceptions.InsufficientResourceCalendarException as e2:
            response = {"reason": "InsufficientResourceCalendarException", 'informations': e2.value}
            status_code = 400
        except Exceptions.LoadBalancerViolationException as e3:
            response = {"reason": "LoadBalancerViolationException", 'informations': e3.value}
            status_code = 400
        except Exception as e3:
            trace_ = {"traceback": traceback.format_exc()}
            reason = e3.__class__.__name__
            response = {"reason": reason, "informations": trace_}
            status_code = 500

        allocator_output = serializer(response)
        print(allocator_output)
        print("Status code =", status_code)
        print("Quantidade de planjobs:", len(response))

        var_gantt_js = []

        for index in range(len(response)):
            a = planjobs[index].id
            b = response[index].time

            f = response[index].execution_slots[0].start_time
            g = response[index].execution_slots[0].finish_time

            c = response[index].execution_slots[0].start_time.strftime('%Y,%#m,%#d,%#H,%#M')
            d = response[index].execution_slots[0].finish_time.strftime('%Y,%#m,%#d,%#H,%#M')
            e = len(response[index].allocated_resources_id)

            print_id_resource = []
            print_id_predecessors = []
            print_id_successors = []

            print('\nPlanjob ID:    {}'.format(a))

            for name in range(len(planjobs[index].predecessors)):
                print_id_predecessors.append(planjobs[index].predecessors[name])
                print('Predecessor {}: {}'.format(name + 1, print_id_predecessors[name]))

            actual_successor = 0
            responsible = []

            for name in range(len(planjobs[index].successors)):
                print_id_successors.append(planjobs[index].successors[name])
                print('Sucessor {}:    {}'.format(name + 1, print_id_successors[name]))
                actual_successor = print_id_successors[name]

            print('Tempo [min]:   {}'.format(b))
            print('Início:        {}'.format(f))
            print('Fim:           {}'.format(g))
            print('Recursos:      {}'.format(e))
            for name in range(len(response[index].allocated_resources_id)):
                print_id_resource.append(response[index].allocated_resources_id[name])
                print('  Recurso {}:   {}, {}'.format(name + 1, print_id_resource[name],
                                                      dict_name_id[print_id_resource[name]]))
                responsible = dict_name_id[print_id_resource[name]]

            var_gantt = '{ name: \'' + str(a) + '\', responsible: \'' + responsible + '\', tasks: [\n\t' \
                                                                                      '{ id: \'' + str(
                a) + '\', content: \'<u>PJ' + str(a) + \
                        '</u><span class="display-block">Teste</span>\', from: new Date(' + c + \
                        '), to: new Date(' + d + ') '

            var_gantt_id_successors = []
            var_gantt_successors = []
            if planjobs[index].successors:
                for name in range(len(planjobs[index].successors)):
                    var_gantt_id_successors.append(planjobs[index].successors[name])

                    var_gantt_successors.append(',\n\t\tclasses: [\'gantt-task-running\'], \n\t\tdependencies: [ \n' \
                                                '\t\t\t{ to: \'' + str(actual_successor) + '\', connectParameters: ' \
                                                                                           '{ sourceEndpointIndex: 1, targetEndpointIndex: 0 }},')

                var_gantt_dependencies = ',\n\t\tclasses: [\'gantt-task-running\'], \n\t\tdependencies: [ \n' \
                                         '\t\t\t{ to: \'' + str(actual_successor) + '\', connectParameters: ' \
                                                                                    '{ sourceEndpointIndex: 1, targetEndpointIndex: 0 }},'
                var_gantt_dependencies += '\n\t\t]\n\t}\n]},'
            else:
                var_gantt_dependencies = '}\n]},'

            print(var_gantt + var_gantt_dependencies)
            var_gantt_js.append(var_gantt + var_gantt_dependencies + '\n')

        var_gantt_js = ''.join(var_gantt_js)
        print(var_gantt_js)

        text_javascript_part1 = '''(function() {
        'use strict';

        angular.module('holdOverview').controller('OverviewController', [
            '$state', 'HoldCache', 'UserProfileService',
            function($state, HoldCache, UserProfileService) {
                let self = this;

                self.data = [

        '''
        text_javascript_part2 = '''
                    { name: 'Pré-Impressão', responsible: 'Carlos', tasks: [
                        { id: '1', content: '<u>PJ345.843</u><span class="display-block">Fechamento Arquivo</span>', from: new Date(2019, 6, 1, 8, 0, 0), to: new Date(2019, 6, 1, 9, 45, 0) },
                        { id: '2', content: '<u>PJ345.843</u><span class="display-block">Criação Arte</span>', from: new Date(2019, 6, 1, 10, 15, 0), to: new Date(2019, 6, 1, 11, 50, 0) },
                        { id: '3', content: '<u>PJ345.843</u><span class="display-block">Fechamento de arquivo</span>', from: new Date(2019, 6, 1, 12, 30, 0), to: new Date(2019, 6, 1, 15, 0, 0) }
                    ]},          
                    { name: 'Impressão', responsible: 'Mimaki JV33', tasks: [
                        { id: '4', content: '<u>PJ345.843</u><span class="display-block">Impressão Mimaki JV33</span>', from: new Date(2019, 6, 1, 8, 0, 0), to: new Date(2019, 6, 1, 9, 55, 0) },
                        { id: '5', content: '<u>PJ345.843</u><span class="display-block">Impressão Mimaki JV33</span>', from: new Date(2019, 6, 1, 10, 20, 0), to: new Date(2019, 6, 1, 14, 5, 0) }
                    ]},
                    { name: 'Impressão', responsible: 'Targa XT', tasks: [
                        { id: '6', content: '<u>PJ345.843</u><span class="display-block">Impressão Mimaki Targa XT</span>', from: new Date(2019, 6, 1, 8, 0, 0), to: new Date(2019, 6, 1, 10, 50, 0) },
                        { id: '7', content: '<u>PJ345.843</u><span class="display-block">Impressão Mimaki Targa XT</span>', from: new Date(2019, 6, 1, 12, 30, 0), to: new Date(2019, 6, 1, 15, 0, 0) }
                    ]},
                    { name: 'Acabamento', responsible: 'Taylor', tasks: [
                        { id: '8', content: '<u>PJ345.843</u><span class="display-block">Refile Manual</span>', from: new Date(2019, 6, 1, 8, 0, 0), to: new Date(2019, 6, 1, 9, 20, 0) },
                        { id: '9', content: '<u>PJ345.843</u><span class="display-block">Aplicação de Substrato</span>', from: new Date(2019, 6, 1, 9, 50, 0), to: new Date(2019, 6, 1, 14, 20, 0) }
                    ]},
                    { name: 'Acabamento', responsible: 'Allisson', tasks: [
                        { id: '10', content: '<u>PJ345.843</u><span class="display-block">Refile Manual</span>', from: new Date(2019, 6, 1, 8, 0, 0), to: new Date(2019, 6, 1, 10, 50, 0) },
                        { id: '11', content: '<u>PJ345.843</u><span class="display-block">Aplicação de Substrato</span>', from: new Date(2019, 6, 1, 11, 30, 0), to: new Date(2019, 6, 1, 15, 0, 0) }
                    ]},
                    { name: 'Expedição', responsible: 'Jéssica', tasks: [
                        { id: '12', content: '<u>PJ345.843</u><span class="display-block">Embalagem Bolha</span>', from: new Date(2019, 6, 1, 8, 0, 0), to: new Date(2019, 6, 1, 9, 50, 0) }
                    ]},
                    { name: 'Instalação', responsible: 'João', tasks: [
                        { id: '13', content: '<u>PJ345.843</u><span class="display-block">Aplicação Externa</span>', from: new Date(2019, 6, 1, 10, 10, 0), to: new Date(2019, 6, 1, 13, 0, 0) }
                    ]},
                    { name: 'Entrega', responsible: 'Marcelo', tasks: [
                        { id: '14', content: '<u>PJ345.843</u><span class="display-block">Cr...</span>', from: new Date(2019, 6, 1, 10, 50, 0), to: new Date(2019, 6, 1, 11, 20, 0) },
                        { id: '15', content: '<u>PJ345.843</u><span class="display-block">Entrega</span>', from: new Date(2019, 6, 1, 12, 10, 0), to: new Date(2019, 6, 1, 15, 0, 0) }
                    ]},
        '''
        text_javascript_part3 = '''
                ];
                var goToOverview = function() {
                    let SALESMAN = 1;
                    let ADMINSTRATOR = 2;
                    let FINANCIAL_MANAGER = 3;
                    let FINANCIAL = 4;
                    let COMERCIAL = 5;
                    let PRODUCTION = 6;
                    let PRODUCTION_MANAGER = 7;
                    let CONSULTANT = 8;
                    let POS_OPERATOR_CASHIER = 9;
                    let BUYER = 10;
                    let PURCHASING_MANAGER = 11;

                    let menuOptions = [];
                    menuOptions[SALESMAN] = function() { return 'app.seller_overview'; };
                    menuOptions[ADMINSTRATOR] = function() { return 'app.administrator_overview'; };
                    menuOptions[FINANCIAL_MANAGER] = function() { return 'app.financial_manager_overview'; };
                    menuOptions[FINANCIAL] = function() { return 'app.financial_overview'; };
                    menuOptions[COMERCIAL] = function() { return 'app.commercial_manager_overview'; };
                    menuOptions[PRODUCTION] = function() { return 'app.production_worker_overview'; };
                    menuOptions[PRODUCTION_MANAGER] = function() { return 'app.production_manager_overview'; };
                    menuOptions[CONSULTANT] = function() { return 'app.consultant_overview'; };
                    menuOptions[POS_OPERATOR_CASHIER] = function() { return 'app.point_of_sale_operator_overview'; };
                    menuOptions[BUYER] = function() { return 'app.buyer_overview'; };
                    menuOptions[PURCHASING_MANAGER] = function() { return 'app.purchasing_manager_overview'; };

                    if (self.loggedUserProfileType && menuOptions[self.loggedUserProfileType.id]) {
                        let targetPage = menuOptions[self.loggedUserProfileType.id]();
                        $state.go(targetPage);
                    }
                };

                (function main() {
                    let permissions = HoldCache.get('permissions');
                    let userProfileType = UserProfileService.loadUserProfileTypes().find(value  => value.id == permissions.userProfileType);

                    if (userProfileType) {
                        self.loggedUserProfileType = userProfileType ;
                    }

                    if (_.isUndefined($state.current) ||
                        $state.current.name == 'app' ||
                        $state.current.name == 'app.overview') {
                        goToOverview();
                    }
                })();
            }
        ]);
    })();
        '''

        arq_js = open('C:\Fontes\HoldNetWebApp\webapp\src\js\controllers\overview\overview-controller.js',
                      'w', -1, "utf-8")

        arq_js.write(text_javascript_part1)
        arq_js.write(var_gantt_js)
        arq_js.write(text_javascript_part3)
        arq_js.close()

        webbrowser.open_new_tab('http://localhost:8000/#/')

        with open('allocator_output.js', 'w', encoding='ISO-8859-1') as file:
            file.write(allocator_output)


if __name__ == '__main__':
    unittest.main()
