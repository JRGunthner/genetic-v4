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

file_to_test = 'test_agg_2.js'
# file_to_test = 'test_lucas_2.js'


class SerializedTestCase(unittest.TestCase):

    # @staticmethod
    # def test_serialize_file():
    #     content = deserializer_file(file_to_test)
    #     to_gantt = serializer(content)
    #     print(to_gantt)
    #
    # @staticmethod
    # def test_allocator_from_file():
    #     content = deserializer_file(file_to_test)
    #     grid = content['grid']
    #     planjobs = content['planjobs']
    #     configs = content['configs']
    #
    #     allocator = Allocator(grid, planjobs, configs)
    #     allocator.generate_allocation()

    # @staticmethod
    # def test_scheduler_from_file():
    #     content = deserializer_file(file_to_test)
    #
    #     grid = content['grid']
    #     planjobs = content['planjobs']
    #     configs = content['configs']
    #     non_working_days = content.get("non_working_days", [])
    #
    #     result = generate_allocation(grid, planjobs, configs, non_working_days)
    #     to_gantt = serializer(result)
    #     print(to_gantt)

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
        print("Quantidade de tasks:", len(response))

        var_gantt_js = []

        for index in range(len(response)):
            task_name = planjobs[index].pj_name
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

            print('\nProcesso:      {}'.format(task_name))
            print('ID:            {}'.format(a))

            for name in range(len(  planjobs[index].predecessors)):
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
                        '{ id: \'' + str(a) + '\', content: \'<u>PJ' + str(a) + \
                        '</u><span class="display-block">' + task_name + '</span>\', from: new Date(' + c + \
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
        'SellerOverviewService', 'Settings', 'holdLoading', '$filter',
        function(SellerOverviewService, Settings, holdLoading, $filter) {
            let self = this;
            
            self.tablePluginClasses = {
                'model.name': 'font-w-800 min-w-152',
                'model.responsible': 'font-w-600 min-w-152'
            };

            self.tablePluginColumns = [
                'model.name',
                'model.responsible'
            ];

            self.tablePluginHeaders = {
                'model.name': $filter('translate')('ETAPA'),
                'model.responsible': $filter('translate')('RECURSO')
            };

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
        }
    ]);
})(); '''

        arq_js = open('C:\Fontes\HoldNetWebApp\webapp\src\js\controllers\overview\seller-overview-controller.js',
                      'w', -1, "utf-8")
        # arq_js = open('C:\Fontes\HoldNetWebApp\webapp\src\js\controllers\overview\overview-controller.js',
        #               'w', -1, "utf-8")

        arq_js.write(text_javascript_part1)
        # arq_js.write(text_javascript_part2)
        arq_js.write(var_gantt_js)
        arq_js.write(text_javascript_part3)
        arq_js.close()

        webbrowser.open_new_tab('http://localhost:8000/#/')

        with open('allocator_output.js', 'w', encoding='ISO-8859-1') as file:
            file.write(allocator_output)


if __name__ == '__main__':
    unittest.main()
