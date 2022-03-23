# coding: utf-8
import unittest
import copy

from datetime import datetime, date, timedelta

from pcp_scheduler.mock import tasks_mock, resources_mock, configuration_mock, journey_mock, load_balancer_mock
from pcp_scheduler.src.scheduler import scheduler
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Resource import Resource
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.src.model.ResourceCharacteristic import ResourceCharacteristic
from pcp_scheduler.src.exceptions import Exceptions
from pcp_scheduler.utils import test_utils, utils
from pcp_scheduler.src.scheduler.scheduler import Scheduler
from pcp_scheduler.src.scheduler.scheduler import Allocator
from pcp_scheduler.src.scheduler import scheduler_utils
from pcp_scheduler.src.scheduler.strategies.OrdinaryStrategy import OrdinaryStrategy
from .resource_filter import ResourceFilter
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException


class TestScheduler(unittest.TestCase):

    global DATE_FORMAT
    DATE_FORMAT = '%Y/%m/%d'

    def test_get_tasks_per_deepness(self):
        planjobs = tasks_mock.get_dependent_tasks()

        allocator = Allocator([], planjobs, {})
        tasks_per_deepness = allocator.get_planjobs_per_deepness(planjobs)

        self.assertEqual(len(tasks_per_deepness.keys()), 4)
        self.assertTrue(0 in tasks_per_deepness.keys())
        self.assertTrue(1 in tasks_per_deepness.keys())
        self.assertTrue(2 in tasks_per_deepness.keys())
        self.assertTrue(3 in tasks_per_deepness.keys())

        self.assertEqual(len(tasks_per_deepness.get(0)), 2)
        self.assertEqual(len(tasks_per_deepness.get(1)), 2)
        self.assertEqual(len(tasks_per_deepness.get(2)), 1)
        self.assertEqual(len(tasks_per_deepness.get(3)), 2)

        self.assertEqual(tasks_per_deepness.get(2)[0].id, "d")
        self.assertTrue(tasks_per_deepness.get(0)[0].id in ["i", "f"])

        for (deepness, tasks) in tasks_per_deepness.items():
            for task in tasks:
                self.assertEqual(task.deepness, deepness)

    def test_define_correspondent_slots(self):
        task_a = Planjob(2, 1, 'a')
        task_a.deepness = 0
        task_b = Planjob(8, 2, 'b')
        task_b.deepness = 0
        task_a.same_start.append(task_b)
        task_b.same_start.append(task_a)
        wished_date = datetime(2017, 7, 18).strftime("%Y/%m/%d")

        resource_filter = ResourceFilter([task_a, task_b], {}, [])

        sibling_slot = resources_mock.get_single_resource_slots()
        current_slot = resources_mock.get_current_slot_resource(task_a)

        potential_slots = scheduler_utils.define_correspondent_slots(current_slot, sibling_slot, task_b,
                                                                     resource_filter.slot_is_enough_same_start)

        self.assertEqual(len(potential_slots.get(wished_date).keys()), 3)

        for slot_intersection, tasks_slot in potential_slots.get(wished_date).items():
            for task, resources in tasks_slot.items():
                for resource_slot in resources:
                    diff = (resource_slot.finish_time - slot_intersection[0]).total_seconds() / 60
                    self.assertTrue(diff >= task.time)

    def test_get_tasks_per_desired_resources(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        acabamento = ResourceCharacteristic(1, sectors=["acabamento"])
        task1 = Planjob(30, "task1", [DesiredResource([acabamento]), DesiredResource([acabamento])])
        task2 = Planjob(30, "task2", [DesiredResource([acabamento]), DesiredResource([acabamento])])
        task1.same_start.append('task2')
        task2.same_start.append('task1')

        resource_filter = ResourceFilter([task1, task2], configs, grid)

        allocation = resource_filter.get_tasks_per_desired_resources(task1.same_start, task1)
        self.assertEqual(len(allocation.keys()), 2)

        all_resources = set([])
        for (task, resources) in allocation.items():
            all_resources = all_resources.union(resources)
            self.assertTrue(task in [task1, task2])
            self.assertEqual(len(resources), 2)
            self.assertEqual(len(set(resources)), 2)

        self.assertEqual(len(all_resources), 4)

    def test_allocate_simple_task(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()
        resource1 = grid[0]
        resource2 = grid[1]

        desired_resource_1 = DesiredResource([ResourceCharacteristic(1, resources=[resource1.id])])
        desired_resource_2 = DesiredResource([ResourceCharacteristic(1, resources=[resource2.id])])

        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        planjob = Planjob(30, "task", [desired_resource_1, desired_resource_2], configs=default_configs_planjob)

        scheduler = Scheduler(grid, [planjob], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.allocated_resources), 2)
        self.assertEqual(len(planjob.execution_slots), 1)

    def test_allocate_same_start_task(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        acabamento = ResourceCharacteristic(1, sectors=["acabamento"])
        task1 = Planjob(30, "task1", [DesiredResource([acabamento])], configs=default_configs_planjob)
        task2 = Planjob(40, "task2", [DesiredResource([acabamento]), DesiredResource([acabamento])], configs=default_configs_planjob)
        task3 = Planjob(25, "task3", [DesiredResource([acabamento])], configs=default_configs_planjob)

        task1.same_start.append('task2')
        task1.same_start.append('task3')
        task2.same_start.append('task3')
        task2.same_start.append('task1')
        task3.same_start.append('task1')
        task3.same_start.append('task2')

        self.assertEqual(len(task1.execution_slots), 0)
        self.assertEqual(len(task2.execution_slots), 0)
        self.assertEqual(len(task3.execution_slots), 0)

        scheduler = Scheduler(grid, [task1, task2, task3], configs)
        scheduler.allocate_planjob(task1)

        self.assertEqual(len(task1.execution_slots), 1)
        self.assertEqual(len(task2.execution_slots), 1)
        self.assertEqual(len(task3.execution_slots), 1)

        self.assertEqual(task1.execution_slots[0].start_time, task2.execution_slots[0].start_time)
        self.assertEqual(task1.execution_slots[0].start_time, task3.execution_slots[0].start_time)
        self.assertEqual(task2.execution_slots[0].start_time, task3.execution_slots[0].start_time)

        all_resources = set(task1.allocated_resources)
        all_resources = all_resources.union(set(task2.allocated_resources))
        all_resources = all_resources.union(set(task3.allocated_resources))

        self.assertEqual(len(all_resources), 4)

    def test_allocate_same_finish_task(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()
        pj_configs = configuration_mock.get_default_configs_planjob()

        acabamento = ResourceCharacteristic(1, sectors=["acabamento"])
        task1 = Planjob(30, "task1", [DesiredResource([acabamento])], configs=pj_configs)
        task2 = Planjob(40, "task2", [DesiredResource([acabamento]), DesiredResource([acabamento])], configs=pj_configs)
        task3 = Planjob(25, "task3", [DesiredResource([acabamento])], configs=pj_configs)

        task1.same_finish.append('task2')
        task1.same_finish.append('task3')
        task2.same_finish.append('task3')
        task2.same_finish.append('task1')
        task3.same_finish.append('task1')
        task3.same_finish.append('task2')

        self.assertEquals(len(task1.execution_slots), 0)
        self.assertEquals(len(task2.execution_slots), 0)
        self.assertEquals(len(task3.execution_slots), 0)

        scheduler = Scheduler(grid, [task1, task2, task3], configs)
        scheduler.allocate_planjob(task1)

        self.assertEqual(len(task1.execution_slots), 1)
        self.assertEqual(len(task2.execution_slots), 1)
        self.assertEqual(len(task3.execution_slots), 1)

        self.assertEqual(task1.execution_slots[0].finish_time, task2.execution_slots[0].finish_time)
        self.assertEqual(task1.execution_slots[0].finish_time, task3.execution_slots[0].finish_time)
        self.assertEqual(task2.execution_slots[0].finish_time, task3.execution_slots[0].finish_time)

        all_resources = set(task1.allocated_resources)
        all_resources = all_resources.union(set(task2.allocated_resources))
        all_resources = all_resources.union(set(task3.allocated_resources))

        self.assertEqual(len(all_resources), 4)

    def test_allocate_tasks_resources_granularity(self):
        grid = resources_mock.grid_todo_livre()
        tasks = tasks_mock.get_tasks_resources_granularity()
        configs = configuration_mock.get_configuration_default()

        allocator = Allocator(grid, tasks, configs)
        allocator.generate_allocation()

        for task in tasks:
            self.assertEqual(len(task.execution_slots), 1)

            if len(task.predecessors) > 0 and len(task.same_start) == 0:
                predecessors = [t for t in tasks if t.id in task.predecessors]
                major = test_utils.get_last_predecessor_to_execute(predecessors)
                self.assertTrue(major.execution_slots[-1].finish_time <= task.execution_slots[0].start_time)

            for sibling_id in task.same_start:
                sibling = [t for t in tasks if t.id == sibling_id][0]
                self.assertEqual(task.execution_slots[0].start_time, sibling.execution_slots[0].start_time)

            for sibling_id in task.same_finish:
                sibling = [t for t in tasks if t.id == sibling_id][0]
                self.assertEqual(task.execution_slots[-1].finish_time, sibling.execution_slots[-1].finish_time)

    def test_allocate_tasks_group_granularity(self):
        grid = resources_mock.grid_todo_livre()
        tasks = tasks_mock.get_tasks_groups_granularity()
        configs = configuration_mock.get_configuration_default()

        allocator = Allocator(grid, tasks, configs)
        allocator.generate_allocation()

        for planjob in tasks:
            self.assertEqual(len(planjob.execution_slots), 1)

            if len(planjob.predecessors) > 0 and len(planjob.same_start) == 0:
                predecessors = [t for t in tasks if t.id in planjob.predecessors]
                major = test_utils.get_last_predecessor_to_execute(predecessors)
                self.assertTrue(major.execution_slots[-1].finish_time <= planjob.execution_slots[0].start_time)

            for sibling_id in planjob.same_start:
                sibling = [t for t in tasks if t.id == sibling_id][0]
                self.assertEqual(planjob.execution_slots[0].start_time, sibling.execution_slots[0].start_time)
                self.assertEqual(set(planjob.allocated_resources).intersection(sibling.allocated_resources), set([]))

            for sibling_id in planjob.same_finish:
                sibling = [t for t in tasks if t.id == sibling_id][0]
                self.assertEqual(planjob.execution_slots[-1].finish_time, sibling.execution_slots[-1].finish_time)
                self.assertEqual(set(planjob.allocated_resources).intersection(sibling.allocated_resources), set([]))

    def test_allocate_tasks_sector_granularity(self):
        grid = resources_mock.grid_todo_livre()
        planjobs = tasks_mock.get_tasks_sectors_granularity()
        configs = configuration_mock.get_configuration_default()

        allocator = Allocator(grid, planjobs, configs)
        allocator.generate_allocation()

        for planjob in planjobs:
            self.assertEqual(len(planjob.execution_slots), 1)

            if len(planjob.predecessors) > 0 and len(planjob.same_start) == 0:
                predecessors = [t for t in planjobs if t.id in planjob.predecessors]
                major = test_utils.get_last_predecessor_to_execute(predecessors)
                self.assertTrue(major.execution_slots[-1].finish_time <= planjob.execution_slots[0].start_time)

            for sibling_id in planjob.same_start:
                sibling = [t for t in planjobs if t.id == sibling_id][0]
                self.assertTrue(planjob.execution_slots[0].start_time == sibling.execution_slots[0].start_time)
                self.assertEqual(set(planjob.allocated_resources).intersection(sibling.allocated_resources), set([]))

            for sibling_id in planjob.same_finish:
                sibling = [t for t in planjobs if t.id == sibling_id][0]
                self.assertTrue(planjob.execution_slots[-1].finish_time == sibling.execution_slots[-1].finish_time)
                self.assertEqual(set(planjob.allocated_resources).intersection(sibling.allocated_resources), set([]))

    def test_allocation_insufficient_resources(self):
        acabamento = ResourceCharacteristic(groups=["top"], hour_type=1)
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        # job A
        a1 = Planjob(30, 'a1', [DesiredResource([acabamento])])
        a2 = Planjob(30, 'a2', [DesiredResource([acabamento])])
        a1.same_start.append('a2')
        a2.same_start.append('a1')

        tasks = [a1, a2]
        allocator = Allocator(grid, tasks, configs)
        try:
            allocator.generate_allocation()
        except Exceptions.InsufficientResourcesException as e:
            self.assertEqual(type(e.value), dict)
            self.assertEqual(len(e.value['planjobs']), 2)
            self.assertTrue(a1.id in e.value['planjobs'])
            self.assertTrue(a2.id in e.value['planjobs'])

    def test_get_task_per_chosen_resource(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        impressora1 = ResourceCharacteristic(resources=[resources_mock.impressora1.id], hour_type=2)
        ana = ResourceCharacteristic(resources=[resources_mock.ana.id], hour_type=1)

        a2 = Planjob(30, 'a2', [DesiredResource([ana])])
        c1 = Planjob(30, 'c1', [DesiredResource([impressora1])])
        c1.same_start.append('a2')
        a2.same_start.append('c1')

        resource_filter = ResourceFilter([a2,c1], configs, grid)
        allocation = resource_filter.get_tasks_per_desired_resources(a2.same_start, a2)

        self.assertEqual(len(allocation.keys()), 2)
        for (task, resources) in allocation.items():
            for resource in resources:
                resource_is_desired = False
                for desired_resource in task.desired_resources:
                    for resource_characteristic in desired_resource.resources_characteristic:
                        resource_in_ids = resource.id in resource_characteristic.resources
                        resource_in_group = set(resource.groups).intersection(resource_characteristic.groups) != set([])
                        resource_in_sectors = set(resource.sectors).intersection(resource_characteristic.sectors) != set([])
                        resource_hour_type = resource.hour_type == resource_characteristic.hour_type

                        resource_is_desired = resource_is_desired or (resource_hour_type and (resource_in_ids
                                                                                              or resource_in_group or resource_in_sectors))

                self.assertTrue(resource_is_desired)

        allocation = resource_filter.get_tasks_per_desired_resources(c1.same_start, c1)

        self.assertEqual(len(allocation.keys()), 2)
        for (task, resources) in allocation.items():
            for resource in resources:
                resource_is_desired = False
                for desired_resource in task.desired_resources:
                    for resource_characteristic in desired_resource.resources_characteristic:
                        resource_in_ids = resource.id in resource_characteristic.resources
                        resource_in_group = set(resource.groups).intersection(resource_characteristic.groups) != set([])
                        resource_in_sectors = set(resource.sectors).intersection(resource_characteristic.sectors) != set([])
                        resource_hour_type = resource.hour_type == resource_characteristic.hour_type

                        resource_is_desired = resource_is_desired or (resource_hour_type and (resource_in_ids
                                                                                              or resource_in_group or resource_in_sectors))

                self.assertTrue(resource_is_desired)

    def test_allocate_desired_resources(self):
        acabamento = ResourceCharacteristic(sectors=["acabamento"], hour_type=1)
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        task = Planjob(30, "task", [DesiredResource([acabamento]), DesiredResource([acabamento])])
        resource_filter = ResourceFilter([task], configs, grid)

        solutions = resource_filter.get_desired_resources(task)
        for solution in solutions:
            self.assertEqual(len(solution), 2)
            self.assertNotEqual(solution[0].id, solution[1].id)
            self.assertNotEqual(set(solution[0].sectors).intersection(["acabamento"]), set([]))
            self.assertNotEqual(set(solution[1].sectors).intersection(["acabamento"]), set([]))

    def test_get_planjob_slots_from_potential_slots(self):
        planjob = tasks_mock.get_10_dependent_tasks()[0]
        potential_slots = resources_mock.get_current_slot_resource(planjob)
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, potential_slots)
        wished_date = datetime(2017, 7, 18).strftime("%Y/%m/%d")

        self.assertEqual(len(available_slots.keys()), 1)
        self.assertEqual(len(list(available_slots.values())[0]), 2)
        self.assertEqual(list(available_slots.keys())[0], wished_date)

        potential_slots = {
            datetime(2017, 7, 18): {
                (datetime(2017, 7, 18, 8, 30), datetime(2017, 7, 18, 9)):
                    {
                        planjob: [Slot(datetime(2017, 7, 18), datetime(2017, 7, 18, 8, 25), datetime(2017, 7, 18, 9, 20)),
                                  Slot(datetime(2017, 7, 18), datetime(2017, 7, 18, 8, 30), datetime(2017, 7, 18, 9, 15))]
                    },
                (datetime(2017, 7, 18, 10, 15), datetime(2017, 7, 18, 10, 45)): {
                    planjob: [Slot(datetime(2017, 7, 18), datetime(2017, 7, 18, 10, 15), datetime(2017, 7, 18, 10, 45))]},
            }
        }
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, potential_slots)

        self.assertEqual(len(available_slots.keys()), 1)
        self.assertEqual(list(available_slots.keys())[0], datetime(2017, 7, 18))
        self.assertEqual(len(list(available_slots.values())[0]), 2)

        slot = Slot(datetime(2017, 7, 18, 8, 30), datetime(2017, 7, 18, 8, 30), datetime(2017, 7, 18, 9, 15))
        self.assertTrue(slot in list(available_slots.values())[0])

    def test_change_limits(self):
        planjob = tasks_mock.get_10_dependent_tasks()[0]
        potential_slots = resources_mock.get_current_slot_resource(planjob)
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, potential_slots)
        global_start = datetime(2017, 7, 18, 8, 20)

        utils.change_limits(available_slots, inferior_limit=global_start)

        self.assertEqual(len(available_slots.keys()), 1)
        self.assertEqual(len(available_slots.values()), 1)
        for slot in list(available_slots.values())[0]:
            self.assertTrue(slot.start_time >= global_start)

        potential_slots = resources_mock.get_current_slot_resource(planjob)
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, potential_slots)
        global_finish = datetime(2017, 7, 18, 8, 25)

        utils.change_limits(available_slots, superior_limit=global_finish)

        self.assertEqual(len(available_slots.keys()), 1)
        self.assertEqual(len(list(available_slots.values())[0]), 2)
        for slot in list(available_slots.values())[0]:
            self.assertTrue(slot.finish_time <= global_finish)

        potential_slots = resources_mock.get_current_slot_resource(planjob)
        available_slots = utils.get_planjob_slots_from_potential_slots(planjob, potential_slots)
        global_start = datetime(2017, 7, 18, 8, 16)
        global_finish = datetime(2017, 7, 18, 8, 26)

        utils.change_limits(available_slots, inferior_limit=global_start, superior_limit=global_finish)

        self.assertEqual(len(available_slots.keys()), 1)
        self.assertEqual(len(list(available_slots.values())[0]), 1)
        for slot in list(available_slots.values())[0]:
            self.assertTrue(slot.finish_time <= global_finish)
            self.assertTrue(slot.start_time >= global_start)

    def test_set_start_finish_dates_fractioned_planjob(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()
        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        default_configs_planjob.fractioned_between_planjobs = True

        maria = grid[4]
        desired_resource_maria = DesiredResource([ResourceCharacteristic(1, resources=[maria.id])])

        planjob = Planjob(520, "planjob1", [desired_resource_maria], configs=default_configs_planjob)

        self.assertTrue(len(planjob.execution_slots) == 0)

        scheduler = Scheduler(grid, [planjob], configs)
        scheduler.allocate_planjob(planjob)

        self.assertTrue(len(planjob.execution_slots) > 0)

        dates = set([])
        acumulated = 0
        for slot in planjob.execution_slots:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            acumulated += duration
            dates.add(slot.date.date())

        self.assertEqual(acumulated, planjob.time)
        self.assertEqual(len(dates), 2)

    def test_set_start_finish_dates_fractioned_planjob_same_start(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        default_configs_planjob.fractioned_between_planjobs = True

        ana = ResourceCharacteristic(1, resources=["6"])
        maria = ResourceCharacteristic(1, resources=["5"])

        planjob1 = Planjob(420, "planjob1", [DesiredResource([maria])], configs=default_configs_planjob)
        planjob2 = Planjob(90, "planjob2", [DesiredResource([ana])], configs=default_configs_planjob)

        planjob1.same_start.append("planjob2")
        planjob2.same_start.append("planjob1")

        self.assertTrue(len(planjob1.execution_slots) == 0)
        self.assertTrue(len(planjob2.execution_slots) == 0)

        scheduler = Scheduler(grid, [planjob1, planjob2], configs)
        scheduler.allocate_planjob(planjob1)

        self.assertTrue(len(planjob1.execution_slots) > 0)
        acumulated = 0
        for slot in planjob1.execution_slots:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            acumulated += duration

        self.assertEqual(acumulated, planjob1.time)

        self.assertTrue(len(planjob2.execution_slots) > 0)
        acumulated = 0
        for slot in planjob2.execution_slots:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            acumulated += duration

        self.assertEqual(acumulated, planjob2.time)

        planjob1_start_dates = [slot.start_time for slot in planjob1.execution_slots]
        planjob2_start_dates = [slot.start_time for slot in planjob2.execution_slots]

        self.assertTrue(set(planjob1_start_dates).intersection(planjob2_start_dates) != set([]))

    @unittest.skip("feature not implemented")
    def test_set_start_finish_dates_fractioned_planjob_same_finish(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        default_configs_planjob.fractioned_between_planjobs = True

        ana = ResourceCharacteristic(1, resources=["6"])
        maria = ResourceCharacteristic(1, resources=["5"])

        planjob1 = Planjob(420, "planjob1", [DesiredResource([maria])], configs=default_configs_planjob)
        planjob2 = Planjob(90, "planjob2", [DesiredResource([ana])], configs=default_configs_planjob)

        planjob1.same_finish.append("planjob2")
        planjob2.same_finish.append("planjob1")

        self.assertTrue(len(planjob1.execution_slots) == 0)
        self.assertTrue(len(planjob2.execution_slots) == 0)

        scheduler.set_tasks([planjob1, planjob2])
        used_slots = scheduler.allocate_same_finish_task(planjob1, grid, configs)

        self.assertTrue(len(planjob1.execution_slots) > 0)
        acumulated = 0
        for slot in planjob1.execution_slots:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            acumulated += duration
        self.assertEqual(acumulated, planjob1.time)

        self.assertTrue(len(planjob2.execution_slots) > 0)
        acumulated = 0
        for slot in planjob2.execution_slots:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            acumulated += duration
        self.assertEqual(acumulated, planjob2.time)

        planjob1_finish_dates = [slot.finish_time for slot in planjob1.execution_slots]
        planjob2_finish_dates = [slot.finish_time for slot in planjob2.execution_slots]

        self.assertTrue(set(planjob1_finish_dates).intersection(planjob2_finish_dates) != set([]))

    def test_load_balancer_simple_planjob(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        configs = configuration_mock.get_configuration_default()

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.um_dia_livre(target_date)

        luisa = resources_mock.get_luisa()
        luisa.available_slots = resources_mock.um_dia_livre(target_date)

        maria.brothers = [luisa]
        luisa.brothers = [maria]

        grid = [maria, luisa]

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id, luisa.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        potential_slots = {
            target_date_str: {
                (datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))]},
                (datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))]},
            }
        }

        strategy = OrdinaryStrategy([planjob], potential_slots, configs)
        strategy.set_execution_slots_same_start()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertNotEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(planjob.allocated_resources[0].id, luisa.id)

    def test_load_balancer_simple_planjob_no_alternatives(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        configs = configuration_mock.get_configuration_default()

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.um_dia_livre(target_date)
        maria.brothers = []

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        potential_slots = {
            target_date_str: {
                (datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))]},
                (datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))]},
            }
        }

        strategy = OrdinaryStrategy([planjob], potential_slots, configs)
        strategy.set_execution_slots_same_start()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, maria.id)

    def test_load_balancer_same_start_planjob(self):
        configs = configuration_mock.get_configuration_default()
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.um_dia_livre(target_date)

        luisa = resources_mock.get_luisa()
        luisa.available_slots = resources_mock.um_dia_livre(target_date)

        maria.brothers = [luisa]
        luisa.brothers = [maria]

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id, luisa.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        joao = resources_mock.get_joao()
        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_start.append(planjob2)
        planjob2.same_start.append(planjob)

        potential_slots = {
            target_date_str: {
                (datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))],
                    planjob2: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))]},
                (datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))],
                    planjob2: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))]},
            }
        }

        strategy = OrdinaryStrategy([planjob, planjob2], potential_slots, configs, same_start=True)
        strategy.set_execution_slots_same_start()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertNotEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(planjob.allocated_resources[0].id, luisa.id)

        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)

    def test_load_balancer_same_start_planjob_no_alternatives(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        configs = configuration_mock.get_configuration_default()

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.um_dia_livre(target_date)

        joao = resources_mock.get_joao()
        joao.available_slots = resources_mock.um_dia_livre(target_date)

        maria.brothers = [joao]

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_start.append(2)
        planjob2.same_start.append(1)

        potential_slots = {
            target_date_str: {
                (datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))],
                    planjob2: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))]},
                (datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))],
                    planjob2: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))]},
            }
        }

        strategy = OrdinaryStrategy([planjob], potential_slots, configs, same_start=True)
        strategy.set_execution_slots_same_start()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, maria.id)

        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)

    def test_load_balancer_same_finish_planjob(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        configs = configuration_mock.get_configuration_default()

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.um_dia_livre(target_date)

        luisa = resources_mock.get_luisa()
        luisa.available_slots = resources_mock.um_dia_livre(target_date)

        maria.brothers = [luisa]
        luisa.brothers = [maria]

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id, luisa.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        joao = resources_mock.get_joao()
        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_finish.append(planjob2)
        planjob2.same_finish.append(planjob)

        potential_slots = {
            target_date_str: {
                (datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))],
                    planjob2: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 9), datetime(2017, 5, 1, 12))]},
                (datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18)): {
                    planjob: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))],
                    planjob2: [Slot(datetime(2017, 5, 1), datetime(2017, 5, 1, 13), datetime(2017, 5, 1, 18))]},
            }
        }

        strategy = OrdinaryStrategy([planjob, planjob2], potential_slots, configs, same_finish=True)
        strategy.set_execution_slots_same_finish()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertNotEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(planjob.allocated_resources[0].id, luisa.id)

        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)

        self.assertEqual(planjob.execution_slots[0].finish_time, planjob2.execution_slots[0].finish_time)

    def test_simple_planjob_must_respect_load_limits(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()
        configs.must_respect_load_limit = True

        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.um_mes_livre()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)

        grid[4] = maria

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        at_least_one_slot_allowed = False
        for slot in maria.available_slots[target_date_str]:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            at_least_one_slot_allowed = at_least_one_slot_allowed or duration >= (planjob.time+planjob.setup)

        self.assertTrue(at_least_one_slot_allowed)

        scheduler = Scheduler(grid, [planjob], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertNotEqual(planjob.execution_slots[0].start_time.date(), target_date.date())
        self.assertEqual(planjob.execution_slots[0].start_time.date(), date(2017, 5, 2))

    def test_simple_planjob_must_respect_load_limits_error(self):
        target_date_str = "2017/05/01"
        process_id = 1

        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()
        configs.must_respect_load_limit = True

        maria = grid[4]
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id, time=30)

        planjob = Planjob(250, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        scheduler = Scheduler(grid, [planjob], configs)

        try:
            scheduler.allocate_planjob(planjob)
        except Exceptions.InsufficientResourceCalendarException as e:
            self.assertEqual(type(e.value), dict)
            self.assertTrue(planjob.id in e.value['planjobs'])
            self.assertTrue(maria.id in e.value['resources'])

    def test_same_start_must_respect_load_limits(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        configs = configuration_mock.get_configuration_default()
        configs.must_respect_load_limit = True

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.dois_dias_livres_seguidos(target_date)
        maria.brothers = []

        joao = resources_mock.get_joao()
        joao.available_slots = resources_mock.dois_dias_livres_seguidos(target_date)

        grid = [maria, joao]

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_start.append(2)
        planjob2.same_start.append(1)

        at_least_one_sufficient_slot = False
        for slot in maria.available_slots[target_date_str]:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            at_least_one_sufficient_slot = at_least_one_sufficient_slot or duration >= (planjob.time + planjob.setup)

        self.assertTrue(at_least_one_sufficient_slot)

        scheduler = Scheduler(grid, [planjob, planjob2], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)
        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(planjob.execution_slots[0].start_time.date(), date(2017, 5, 2))
        self.assertEqual(planjob2.execution_slots[0].start_time.date(), date(2017, 5, 2))
        self.assertEqual(planjob.execution_slots[0].start_time, planjob2.execution_slots[0].start_time)

    def test_same_finish_must_respect_load_limits(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        configs = configuration_mock.get_configuration_default()
        configs.must_respect_load_limit = True

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.dois_dias_livres_seguidos(target_date)
        maria.brothers = []

        joao = resources_mock.get_joao()
        joao.available_slots = resources_mock.dois_dias_livres_seguidos(target_date)

        grid = [maria, joao]

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_finish.append(2)
        planjob2.same_finish.append(1)

        at_least_one_sufficient_slot = False
        for slot in maria.available_slots[target_date_str]:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            at_least_one_sufficient_slot = at_least_one_sufficient_slot or duration >= (planjob.time + planjob.setup)

        self.assertTrue(at_least_one_sufficient_slot)

        scheduler = Scheduler(grid, [planjob, planjob2], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)
        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(planjob.execution_slots[0].start_time.date(), date(2017, 5, 2))
        self.assertEqual(planjob2.execution_slots[0].start_time.date(), date(2017, 5, 2))
        self.assertEqual(planjob.execution_slots[0].finish_time, planjob2.execution_slots[0].finish_time)

    def test_same_finish_must_respect_load_limits_error(self):
        target_date = datetime(2017, 5, 1)
        target_date_str = "2017/05/01"
        process_id = 1

        configs = configuration_mock.get_configuration_default()
        configs.must_respect_load_limit = True

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.load_limit = load_balancer_mock.get_limit_4_hours()
        maria.date_load_informations = resources_mock.get_date_load_informations(target_date_str, process_id)
        maria.available_slots = resources_mock.um_dia_livre(target_date)
        maria.brothers = []

        joao = resources_mock.get_joao()
        joao.available_slots = resources_mock.um_dia_livre(target_date)

        grid = [maria, joao]

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]

        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_finish.append(2)
        planjob2.same_finish.append(1)

        scheduler = Scheduler(grid, [planjob, planjob2], configs)

        try:
            scheduler.allocate_planjob(planjob)
        except Exceptions.InsufficientResourceCalendarException as e:
            self.assertEqual(type(e.value), dict)
            self.assertEqual(len(e.value.keys()), 2)
            self.assertTrue(planjob.id in e.value['planjobs'])
            self.assertTrue(planjob2.id in e.value['planjobs'])

    def test_simple_planjob_fractioned_between_intervals(self):
        configs = configuration_mock.get_configuration_default()
        planjob_configs = configuration_mock.get_default_configs_planjob()
        planjob_configs.fractioned_between_intervals = True

        today = datetime.today()
        today_str = today.strftime(utils.DATE_FORMAT)

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.dois_dias_livres_seguidos(today)

        first_slot = Slot(datetime(today.year, today.month, today.day),
                          datetime(today.year, today.month, today.day, 9),
                          datetime(today.year, today.month, today.day, 10))
        second_slot = Slot(datetime(today.year, today.month, today.day),
                           datetime(today.year, today.month, today.day, 11),
                           datetime(today.year, today.month, today.day, 12))

        ana.available_slots[today_str][0] = first_slot
        ana.available_slots[today_str].insert(1, second_slot)
        grid = [ana]

        planjob = Planjob(420, 1, [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], planjob_configs)

        scheduler = Scheduler(grid, [planjob], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, ana.id)

        self.assertEqual(len(planjob.execution_slots), 3)
        self.assertEqual(planjob.execution_slots[0].start_time, second_slot.start_time)

        tomorrow = today + timedelta(days=1)
        self.assertEqual(planjob.execution_slots[-1].date.date(), tomorrow.date())

        sum = 0
        for slot in planjob.execution_slots:
            sum += ((slot.finish_time - slot.start_time).total_seconds() // 60)

        self.assertEqual(sum, planjob.time + planjob.setup*len(planjob.execution_slots))

    def test_same_start_fractioned_between_intervals(self):
        configs = configuration_mock.get_configuration_default()
        configs_pj1 = configuration_mock.get_default_configs_planjob()
        configs_pj2 = copy.deepcopy(configuration_mock.get_default_configs_planjob())
        configs_pj2.fractioned_between_intervals = True

        today = datetime.today()
        today_str = today.strftime(utils.DATE_FORMAT)

        pedro = resources_mock.get_pedro()
        pedro.available_slots = resources_mock.dois_dias_livres_seguidos(today)
        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.dois_dias_livres_seguidos(today)

        grid = [pedro, ana]

        first_slot = Slot(datetime(today.year, today.month, today.day),
                          datetime(today.year, today.month, today.day, 9),
                          datetime(today.year, today.month, today.day, 10))
        second_slot = Slot(datetime(today.year, today.month, today.day),
                           datetime(today.year, today.month, today.day, 11),
                           datetime(today.year, today.month, today.day, 12))

        ana.available_slots[today_str][0] = first_slot
        ana.available_slots[today_str].insert(1, second_slot)

        planjob = Planjob(420, 1, [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs_pj2)
        planjob2 = Planjob(60, 2, [DesiredResource([ResourceCharacteristic(resources=[pedro.id])])], configs_pj1)

        planjob.same_start.append(planjob2.id)
        planjob2.same_start.append(planjob.id)

        scheduler = Scheduler(grid, [planjob, planjob2], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, ana.id)
        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, pedro.id)

        self.assertEqual(len(planjob.execution_slots), 3)
        self.assertEqual(planjob.execution_slots[0].start_time, second_slot.start_time)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(planjob2.execution_slots[0].start_time, second_slot.start_time)

        tomorrow = today + timedelta(days=1)
        self.assertEqual(planjob.execution_slots[-1].date.date(), tomorrow.date())

        sum = 0
        for slot in planjob.execution_slots:
            sum += ((slot.finish_time - slot.start_time).total_seconds() // 60)

        self.assertEqual(sum, planjob.time + planjob.setup*len(planjob.execution_slots))

    def test_simple_planjob_nonstop_infinity(self):
        global_configs = configuration_mock.get_configuration_default()
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_infinity = True

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        grid = [ana]

        planjob = Planjob(1440, 1, [DesiredResource([ResourceCharacteristic(resources=ana.id)])], configs=configs_pj)
        planjob.allocated_resources = [ana]

        scheduler = Scheduler(grid, [planjob], global_configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.execution_slots), 1)

        time = (planjob.execution_slots[0].finish_time - planjob.execution_slots[0].start_time).total_seconds() // 60
        self.assertEqual(time, planjob.time+planjob.setup)

    def test_update_grid_planjob_nonstop_infinity(self):
        global_configs = configuration_mock.get_configuration_default()
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_infinity = True

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        ana_dates_before = set(ana.available_slots.keys())

        grid = [ana]

        planjob = Planjob(1440, 1, [DesiredResource([ResourceCharacteristic(resources=ana.id)])], configs=configs_pj)
        planjob.allocated_resources = [ana]

        scheduler = Scheduler(grid, [planjob], global_configs)
        scheduler.allocate_planjob(planjob)

        ana_dates_current = set(ana.available_slots.keys())
        self.assertTrue(ana_dates_current.issubset(ana_dates_before))
        self.assertEquals(len(ana_dates_before.difference(ana_dates_current)), 1)
        self.assertEquals(ana_dates_before.difference(ana_dates_current), {'2017/05/01'})

    def test_allocate_planjob_nonstop_infinity_same_start(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        nonstop_config = configuration_mock.get_default_configs_planjob()
        nonstop_config.nonstop_infinity = True
        default_configs_planjob = configuration_mock.get_default_configs_planjob()

        acabamento = ResourceCharacteristic(1, sectors=["acabamento"])
        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()

        grid[5] = ana

        planjob1 = Planjob(1400, "planjob1", [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs=nonstop_config)
        planjob2 = Planjob(40, "planjob2", [DesiredResource([acabamento]), DesiredResource([acabamento])], configs=default_configs_planjob)
        planjob3 = Planjob(25, "planjob3", [DesiredResource([acabamento])], configs=default_configs_planjob)

        planjob1.same_start.append('planjob2')
        planjob1.same_start.append('planjob3')
        planjob2.same_start.append('planjob3')
        planjob2.same_start.append('planjob1')
        planjob3.same_start.append('planjob1')
        planjob3.same_start.append('planjob2')

        self.assertEqual(len(planjob1.execution_slots), 0)
        self.assertEqual(len(planjob2.execution_slots), 0)
        self.assertEqual(len(planjob3.execution_slots), 0)

        scheduler = Scheduler(grid, [planjob1, planjob2, planjob3], configs)
        scheduler.allocate_planjob(planjob1)

        self.assertEqual(len(planjob1.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(len(planjob3.execution_slots), 1)

        self.assertEqual(planjob1.execution_slots[0].start_time, planjob2.execution_slots[0].start_time)
        self.assertEqual(planjob1.execution_slots[0].start_time, planjob3.execution_slots[0].start_time)
        self.assertEqual(planjob2.execution_slots[0].start_time, planjob3.execution_slots[0].start_time)

        all_resources = set(planjob1.allocated_resources)
        all_resources = all_resources.union(set(planjob2.allocated_resources))
        all_resources = all_resources.union(set(planjob3.allocated_resources))

        self.assertEqual(len(all_resources), 4)

    @unittest.skip("feature not implemented")
    def test_allocate_planjob_nonstop_infinity_same_finish(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        nonstop_config = configuration_mock.get_default_configs_planjob()
        nonstop_config.nonstop_infinity = True
        default_configs_planjob = configuration_mock.get_default_configs_planjob()

        acabamento = ResourceCharacteristic(1, sectors=["acabamento"])
        ana = resources_mock.ana
        ana.available_slots = resources_mock.um_mes_livre()

        planjob1 = Planjob(1400, "planjob1", [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs=nonstop_config)
        planjob2 = Planjob(40, "planjob2", [DesiredResource([acabamento]), DesiredResource([acabamento])], configs=default_configs_planjob)
        planjob3 = Planjob(25, "planjob3", [DesiredResource([acabamento])], configs=default_configs_planjob)

        planjob1.same_finish.append('planjob2')
        planjob1.same_finish.append('planjob3')
        planjob2.same_finish.append('planjob3')
        planjob2.same_finish.append('planjob1')
        planjob3.same_finish.append('planjob1')
        planjob3.same_finish.append('planjob2')

        self.assertEqual(len(planjob1.execution_slots), 0)
        self.assertEqual(len(planjob2.execution_slots), 0)
        self.assertEqual(len(planjob3.execution_slots), 0)

        scheduler.set_tasks([planjob1, planjob2, planjob3])
        used_slots = scheduler.allocate_same_finish_task(planjob1, grid, configs)

        self.assertEqual(len(planjob1.execution_slots), 1)
        self.assertEqual(len(planjob3.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 1)

        self.assertEqual(planjob1.execution_slots[0].finish_time, planjob2.execution_slots[0].finish_time)
        self.assertEqual(planjob1.execution_slots[0].finish_time, planjob3.execution_slots[0].finish_time)
        self.assertEqual(planjob2.execution_slots[0].finish_time, planjob3.execution_slots[0].finish_time)

        all_resources = set(planjob1.allocated_resources)
        all_resources = all_resources.union(set(planjob2.allocated_resources))
        all_resources = all_resources.union(set(planjob3.allocated_resources))

        self.assertEqual(len(all_resources), 4)

    def test_allocate_simple_planjob_journey_two_days(self):
        grid = resources_mock.grid_todo_livre()
        global_configs = configuration_mock.get_configuration_default()
        configs_pj = configuration_mock.get_default_configs_planjob()

        ana = resources_mock.get_ana()
        ana.journey = journey_mock.get_journey_10pm_to_10am()
        ana.available_slots = resources_mock.get_scheduler_by_journey(ana.journey)

        grid[5] = ana

        planjob = Planjob(200, 1, [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs=configs_pj)
        self.assertEquals(len(planjob.execution_slots), 0)

        allocator = Allocator(grid, [planjob], global_configs)
        allocator.generate_allocation()

        self.assertEquals(len(planjob.execution_slots), 1)

        tomorrow = (planjob.execution_slots[0].start_time + timedelta(days=1)).date()
        self.assertEquals(planjob.execution_slots[0].finish_time.date(), tomorrow)

    def test_allocate_simple_task_scheduled_date(self):
        grid = resources_mock.grid_todo_livre()
        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        configs = configuration_mock.get_configuration_default()
        resource1 = grid[0]
        resource2 = grid[1]

        desired_resource_1 = DesiredResource([ResourceCharacteristic(1, resources=[resource1.id])])
        desired_resource_2 = DesiredResource([ResourceCharacteristic(1, resources=[resource2.id])])

        planjob = Planjob(30, "task", [desired_resource_1, desired_resource_2], configs=default_configs_planjob)
        planjob.scheduled_date = datetime(2017, 5, 10, 9)

        scheduler = Scheduler(grid, [planjob], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)

    def test_simple_planjob_fractioned_between_intervals_scheduled_date(self):
        configs = configuration_mock.get_configuration_default()
        grid = resources_mock.grid_todo_livre()
        planjob_configs = configuration_mock.get_default_configs_planjob()
        planjob_configs.fractioned_between_intervals = True

        acabamento = [DesiredResource([ResourceCharacteristic(hour_type=1, sectors=['acabamento'])])]
        planjob = Planjob(420, 1, acabamento, planjob_configs)
        planjob.scheduled_date = datetime(2017, 5, 10, 9)

        scheduler = Scheduler(grid, [planjob], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(len(planjob.execution_slots), 2)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)

        sum = 0
        for slot in planjob.execution_slots:
            sum += ((slot.finish_time - slot.start_time).total_seconds() // 60)

        self.assertEqual(sum, planjob.time + planjob.setup*len(planjob.execution_slots))

    def test_allocate_deadline_planjob_scheduled_date(self):
        grid = resources_mock.grid_todo_livre()
        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        default_configs_planjob.is_deadline = True
        configs = configuration_mock.get_configuration_default()
        resource1 = grid[0]
        resource2 = grid[1]

        desired_resource_1 = DesiredResource([ResourceCharacteristic(1, resources=[resource1.id])])
        desired_resource_2 = DesiredResource([ResourceCharacteristic(1, resources=[resource2.id])])

        planjob1 = Planjob(7200, "pj1", [desired_resource_1, desired_resource_2], configs=default_configs_planjob)
        planjob2 = Planjob(7200, "pj2", [desired_resource_1, desired_resource_2], configs=default_configs_planjob)
        planjob1.scheduled_date = datetime(2017, 5, 10, 9)
        planjob2.scheduled_date = datetime(2017, 5, 20, 9)

        scheduler = Scheduler(grid, [planjob1, planjob2], configs)
        scheduler.allocate_planjob(planjob1)

        finish_date = planjob1.scheduled_date + timedelta(days=5)
        self.assertEqual(len(planjob1.execution_slots), 1)
        self.assertEqual(planjob1.execution_slots[0].start_time, planjob1.scheduled_date)
        self.assertEqual(planjob1.execution_slots[0].finish_time.date(), finish_date.date())

        self.assertTrue(configs.deadline_hour is not None)
        self.assertEqual(planjob1.execution_slots[0].finish_time.hour, configs.deadline_hour)

        configs.deadline_hour = None
        scheduler.allocate_planjob(planjob2)

        finish_date = planjob2.scheduled_date + timedelta(days=5)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(planjob2.execution_slots[0].start_time, planjob2.scheduled_date)
        self.assertEqual(planjob2.execution_slots[0].finish_time.date(), finish_date.date())

        self.assertTrue(configs.deadline_hour is None)
        self.assertEqual(planjob2.execution_slots[0].finish_time.hour, planjob2.execution_slots[0].start_time.hour)

    def test_allocate_deadline_planjob_predecessor(self):
        grid = resources_mock.grid_todo_livre()
        config_pj_1 = configuration_mock.get_default_configs_planjob()
        config_pj_2 = configuration_mock.get_default_configs_planjob()
        config_pj_2.is_deadline = True
        configs = configuration_mock.get_configuration_default()
        resource1 = grid[0]
        resource2 = grid[1]

        desired_resource_1 = DesiredResource([ResourceCharacteristic(1, resources=[resource1.id])])
        desired_resource_2 = DesiredResource([ResourceCharacteristic(1, resources=[resource2.id])])

        planjob1 = Planjob(60, "pj1", [desired_resource_1, desired_resource_2], configs=config_pj_1)
        planjob2 = Planjob(7200, "pj2", [desired_resource_1, desired_resource_2], configs=config_pj_2)

        planjob1.successors.append("pj2")
        planjob2.predecessors.append("pj1")

        scheduler = Scheduler(grid, [planjob1, planjob2], configs)
        scheduler.allocate_planjob(planjob1)

        self.assertEqual(len(planjob1.execution_slots), 1)

        scheduler.allocate_planjob(planjob2)

        finish_date = planjob1.execution_slots[-1].finish_time + timedelta(days=5)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(planjob2.execution_slots[0].start_time, planjob1.execution_slots[-1].finish_time)
        self.assertEqual(planjob2.execution_slots[0].finish_time.date(), finish_date.date())

    def test_allocate_deadline_planjob_little_time(self):
        grid = resources_mock.grid_todo_livre()

        configs = configuration_mock.get_configuration_default()
        configs.deadline_hour = 8
        config_pj = configuration_mock.get_default_configs_planjob()
        config_pj.is_deadline = True

        resource = grid[1]

        desired_resource = DesiredResource([ResourceCharacteristic(1, resources=[resource.id])])
        planjob = Planjob(60, "pj2", [desired_resource], configs=config_pj)
        planjob.scheduled_date = datetime(2017, 5, 10, 9)

        scheduler = Scheduler(grid, [planjob], configs)
        scheduler.allocate_planjob(planjob)

        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertNotEquals(planjob.execution_slots[0].finish_time.hour, configs.deadline_hour)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)

        finish_time = planjob.scheduled_date + timedelta(hours=1)
        self.assertEqual(planjob.execution_slots[0].finish_time, finish_time)

    def test_relay_strategy(self):
        global_configs = configuration_mock.get_configuration_default()
        global_configs.relay_slot_floor_limit = 60

        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.relay = True

        date_ = datetime(2017, 5, 2)
        date_str = date_.strftime(utils.DATE_FORMAT)
        next_day = date_ + timedelta(days=1)
        next_day_str = next_day.strftime(utils.DATE_FORMAT)

        maria = resources_mock.get_maria()
        ana = resources_mock.get_ana()

        maria.available_slots = {}
        maria.available_slots[date_str] = [Slot(date_, datetime(2017, 5, 2, 8), datetime(2017, 5, 2, 9))]
        maria.available_slots[next_day_str] = [Slot(next_day, datetime(2017, 5, 3, 8), datetime(2017, 5, 3, 12))]

        ana.available_slots = {}
        ana.available_slots[date_str] = [Slot(date_, datetime(2017, 5, 2, 9), datetime(2017, 5, 2, 13))]
        ana.available_slots[next_day_str] = [Slot(next_day, datetime(2017, 5, 3, 8), datetime(2017, 5, 3, 12))]

        planjob = Planjob(240, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id, ana.id])])], configs_pj)

        self.assertEquals(len(planjob.execution_slots), 0)

        scheduler = Scheduler([maria, ana], [planjob], global_configs)
        scheduler.allocate_planjob(planjob)

        self.assertNotEquals(len(planjob.execution_slots), 0)
        self.assertEquals(len(planjob.execution_slots), 2)
        self.assertEquals(planjob.execution_slots[0].start_time, datetime(2017, 5, 2, 8))
        self.assertEquals(planjob.execution_slots[-1].finish_time, datetime(2017, 5, 2, 12))
        self.assertTrue(ana in planjob.allocated_resources)
        self.assertTrue(maria in planjob.allocated_resources)

    def test_relay_strategy_scheduled_date(self):
        global_configs = configuration_mock.get_configuration_default()
        global_configs.relay_slot_floor_limit = 60

        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.relay = True

        date_ = datetime(2017, 5, 2)
        date_str = date_.strftime(utils.DATE_FORMAT)
        next_day = date_ + timedelta(days=1)
        next_day_str = next_day.strftime(utils.DATE_FORMAT)

        maria = resources_mock.get_maria()
        ana = resources_mock.get_ana()
        ricardo = resources_mock.get_ricardo()

        maria.available_slots = {}
        maria.available_slots[date_str] = [Slot(date_, datetime(2017, 5, 2, 8), datetime(2017, 5, 2, 9))]
        maria.available_slots[next_day_str] = [Slot(next_day, datetime(2017, 5, 3, 8), datetime(2017, 5, 3, 12))]

        ana.available_slots = {}
        ana.available_slots[date_str] = [Slot(date_, datetime(2017, 5, 2, 9), datetime(2017, 5, 2, 13))]
        ana.available_slots[next_day_str] = [Slot(next_day, datetime(2017, 5, 3, 8), datetime(2017, 5, 3, 12))]

        ricardo.available_slots = {}
        ricardo.available_slots[date_str] = [Slot(date_, datetime(2017, 5, 2, 8), datetime(2017, 5, 2, 13))]

        ana_ou_maria = DesiredResource([ResourceCharacteristic(resources=[maria.id, ana.id])])
        ricardo_ = DesiredResource([ResourceCharacteristic(resources=[ricardo.id])])
        planjob = Planjob(240, 1, [ana_ou_maria, ricardo_], configs_pj)
        planjob.scheduled_date = datetime(2017, 5, 2, 8)

        self.assertEquals(len(planjob.execution_slots), 0)

        scheduler = Scheduler([maria, ana, ricardo], [planjob], global_configs)
        scheduler.allocate_planjob(planjob)

        self.assertNotEquals(len(planjob.execution_slots), 0)
        self.assertEquals(len(planjob.execution_slots), 2)
        self.assertEquals(planjob.execution_slots[0].start_time, datetime(2017, 5, 2, 8))
        self.assertEquals(planjob.execution_slots[-1].finish_time, datetime(2017, 5, 2, 12))
        self.assertTrue(ana in planjob.allocated_resources)
        self.assertTrue(maria in planjob.allocated_resources)
        self.assertTrue(ricardo in planjob.allocated_resources)

        self.assertTrue(maria in planjob.execution_slots[0].resources)
        self.assertTrue(ricardo in planjob.execution_slots[0].resources)
        self.assertTrue(ana not in planjob.execution_slots[0].resources)

        self.assertTrue(ana in planjob.execution_slots[1].resources)
        self.assertTrue(ricardo in planjob.execution_slots[1].resources)
        self.assertTrue(maria not in planjob.execution_slots[1].resources)

    def test_relay_strategy_scheduled_date_error(self):
        global_configs = configuration_mock.get_configuration_default()
        global_configs.relay_slot_floor_limit = 60

        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.relay = True

        date_ = datetime(2017, 5, 2)
        date_str = date_.strftime(utils.DATE_FORMAT)
        next_day = date_ + timedelta(days=1)
        next_day_str = next_day.strftime(utils.DATE_FORMAT)

        ana = resources_mock.get_ana()
        ricardo = resources_mock.get_ricardo()

        ana.available_slots = {}
        ana.available_slots[date_str] = [Slot(date_, datetime(2017, 5, 2, 9), datetime(2017, 5, 2, 13))]
        ana.available_slots[next_day_str] = [Slot(next_day, datetime(2017, 5, 3, 8), datetime(2017, 5, 3, 12))]

        ricardo.available_slots = {}
        ricardo.available_slots[date_str] = [Slot(date_, datetime(2017, 5, 2, 8), datetime(2017, 5, 2, 13))]

        ana_ = DesiredResource([ResourceCharacteristic(resources=[ana.id])])
        ricardo_ = DesiredResource([ResourceCharacteristic(resources=[ricardo.id])])
        planjob = Planjob(240, 1, [ana_, ricardo_], configs_pj)
        planjob.scheduled_date = datetime(2017, 5, 2, 8)

        self.assertEquals(len(planjob.execution_slots), 0)

        scheduler = Scheduler([ricardo, ana], [planjob], global_configs)
        try:
            scheduler.allocate_planjob(planjob)
            assert False
        except InsufficientResourceCalendarException as e:
            self.assertTrue(isinstance(e.value, dict))
            self.assertTrue(planjob.id in e.value['planjobs'])
            self.assertTrue(ana.id in e.value['resources'])
            self.assertTrue(ricardo.id in e.value['resources'])

    def test_is_same_start_and_same_finish(self):
        planjob_A = Planjob(30, "pj_a", [])
        planjob_B = Planjob(60, "pj_b", [])
        planjob_C = Planjob(30, "pj_c", [])

        planjob_A.same_start.append("pj_b")
        planjob_B.same_start.append("pj_a")
        planjob_B.same_finish.append("pj_c")
        planjob_C.same_finish.append("pj_b")

        scheduler = Scheduler([], [planjob_A, planjob_B, planjob_C], {})

        self.assertTrue(scheduler.is_same_start_and_same_finish(planjob_A))
        self.assertTrue(scheduler.is_same_start_and_same_finish(planjob_B))
        self.assertTrue(scheduler.is_same_start_and_same_finish(planjob_C))

    def test_can_allocate_start_and_same_finish(self):
        planjob_A = Planjob(30, "pj_a", [])
        planjob_A.deepness = 0
        planjob_B = Planjob(60, "pj_b", [])
        planjob_B.deepness = 0
        planjob_C = Planjob(30, "pj_c", [])
        planjob_C.deepness = 1

        planjob_A.same_start.append("pj_b")
        planjob_B.same_start.append("pj_a")
        planjob_B.same_finish.append("pj_c")
        planjob_C.same_finish.append("pj_b")

        scheduler = Scheduler([], [planjob_A, planjob_B, planjob_C], {})

        self.assertFalse(scheduler.can_allocate_planjob(planjob_A))
        self.assertFalse(scheduler.can_allocate_planjob(planjob_B))
        self.assertTrue(scheduler.can_allocate_planjob(planjob_C))

    def test_can_allocate_simple_task(self):
        planjob_A = Planjob(30, "pj_a", [])
        planjob_A.deepness = 0
        planjob_B = Planjob(60, "pj_b", [])
        planjob_B.deepness = 1

        planjob_A.successors.append("pj_b")
        planjob_B.predecessors.append("pj_a")

        scheduler = Scheduler([], [planjob_A, planjob_B], {})


        self.assertTrue(scheduler.can_allocate_planjob(planjob_A))
        self.assertFalse(scheduler.can_allocate_planjob(planjob_B))

        planjob_A.execution_slots.append(Slot(datetime.today(), datetime.today(), datetime.today()))
        self.assertTrue(scheduler.can_allocate_planjob(planjob_B))

    def test_can_allocate_same_finish(self):
        planjob_A = Planjob(30, "pj_a", [])
        planjob_A.deepness = 0
        planjob_B = Planjob(60, "pj_b", [])
        planjob_B.deepness = 1
        planjob_C = Planjob(30, "pj_c", [])
        planjob_C.deepness = 1

        planjob_A.successors.append("pj_b")
        planjob_B.predecessors.append("pj_a")
        planjob_B.same_finish.append("pj_c")
        planjob_C.same_finish.append("pj_b")

        scheduler = Scheduler([], [planjob_A, planjob_B, planjob_C], {})

        self.assertTrue(scheduler.can_allocate_planjob(planjob_A))
        self.assertFalse(scheduler.can_allocate_planjob(planjob_B))
        self.assertFalse(scheduler.can_allocate_planjob(planjob_C))

        planjob_A.execution_slots.append(Slot(datetime.today(), datetime.today(), datetime.today()))
        self.assertTrue(scheduler.can_allocate_planjob(planjob_B))
        self.assertTrue(scheduler.can_allocate_planjob(planjob_C))

    def test_allocate_planjob_same_start_and_same_finish(self):
        '''
            _____
        -- |__A__|
       |
       |    __________
        -- |____B_____| --
                          |
                 _____    |
                |__c__| --
        :return:
        '''
        grid = resources_mock.grid_todo_livre()
        global_configs = configuration_mock.get_configuration_default()
        configs_pj = configuration_mock.get_default_configs_planjob()

        acabamento = DesiredResource([ResourceCharacteristic(hour_type=1, sectors=["acabamento"])])
        planjob_A = Planjob(30, "pj_a", [acabamento], configs_pj)
        planjob_A.deepness = 0
        planjob_B = Planjob(60, "pj_b", [acabamento], configs_pj)
        planjob_B.deepness = 0
        planjob_C = Planjob(30, "pj_c", [acabamento], configs_pj)
        planjob_C.deepness = 1

        planjob_A.same_start.append("pj_b")
        planjob_B.same_start.append("pj_a")
        planjob_B.same_finish.append("pj_c")
        planjob_C.same_finish.append("pj_b")

        self.assertTrue(planjob_A.allocated_resources is None)
        self.assertTrue(planjob_B.allocated_resources is None)
        self.assertTrue(planjob_C.allocated_resources is None)

        scheduler = Scheduler(grid, [planjob_A, planjob_B, planjob_C], global_configs)

        scheduler.allocate_planjob(planjob_C)

        self.assertEquals(len(planjob_A.allocated_resources), 1)
        self.assertEquals(len(planjob_B.allocated_resources), 1)
        self.assertEquals(len(planjob_C.allocated_resources), 1)

        self.assertEquals(len(planjob_A.execution_slots), 1)
        self.assertEquals(len(planjob_B.execution_slots), 1)
        self.assertEquals(len(planjob_C.execution_slots), 1)

        self.assertEquals(planjob_A.execution_slots[0].start_time, planjob_B.execution_slots[0].start_time)
        self.assertEquals(planjob_B.execution_slots[-1].finish_time, planjob_C.execution_slots[-1].finish_time)

        self.assertEquals(planjob_A.execution_slots[0].minutes(), planjob_A.time+planjob_A.setup)
        self.assertEquals(planjob_B.execution_slots[0].minutes(), planjob_B.time+planjob_B.setup)
        self.assertEquals(planjob_C.execution_slots[0].minutes(), planjob_C.time+planjob_C.setup)

    def test_group_as_subset(self):
        configs = configuration_mock.get_configuration_default()
        configs.groups_as_subset = True
        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.fractioned_between_planjobs = True

        planjob = Planjob(60, 146, [DesiredResource([ResourceCharacteristic(hour_type=1, resources=[176])]),
                                    DesiredResource([ResourceCharacteristic(hour_type=1, groups=["94"])])], pj_configs)

        r1 = Resource(172, "LUCAS", groups=[str(i) for i in range(94, 124)], hour_type=1)
        r1.available_slots = {}
        r1.available_slots["2017/09/28"] = [
            Slot(datetime(2017, 9, 28), datetime(2017, 9, 28, 10), datetime(2017, 9, 28, 12)),
            Slot(datetime(2017, 9, 28), datetime(2017, 9, 28, 13), datetime(2017, 9, 28, 18))]

        r1.available_slots["2017/09/29"] = [
            Slot(datetime(2017, 9, 29), datetime(2017, 9, 29, 11), datetime(2017, 9, 29, 12)),
            Slot(datetime(2017, 9, 29), datetime(2017, 9, 29, 13), datetime(2017, 9, 29, 17, 30))]

        r2 = Resource(174, "HOMOLOGACAO", hour_type=1)
        r2.available_slots = {}
        r2.available_slots["2017/09/28"] = [
            Slot(datetime(2017, 9, 28), datetime(2017, 9, 28, 8), datetime(2017, 9, 28, 12)),
            Slot(datetime(2017, 9, 28), datetime(2017, 9, 28, 13), datetime(2017, 9, 28, 17, 30))]

        r2.available_slots["2017/09/29"] = [
            Slot(datetime(2017, 9, 29), datetime(2017, 9, 29, 8), datetime(2017, 9, 29, 12)),
            Slot(datetime(2017, 9, 29), datetime(2017, 9, 29, 13), datetime(2017, 9, 29, 17, 30))]

        r3 = Resource(176, "ALUNO 1", hour_type=1)
        r3.available_slots = {}
        r3.available_slots["2017/09/28"] = [
            Slot(datetime(2017, 9, 28), datetime(2017, 9, 28, 10), datetime(2017, 9, 28, 12)),
            Slot(datetime(2017, 9, 28), datetime(2017, 9, 28, 13), datetime(2017, 9, 28, 17, 30))]

        r3.available_slots["2017/09/29"] = [
            Slot(datetime(2017, 9, 29), datetime(2017, 9, 29, 11), datetime(2017, 9, 29, 12)),
            Slot(datetime(2017, 9, 29), datetime(2017, 9, 29, 13), datetime(2017, 9, 29, 17, 30))]

        scheduler = Scheduler([r1, r2, r3], [planjob], configs)
        scheduler.allocate_planjob(planjob)

    def test_deadline_planjob_keep_same_resource_availability(self):
        today = datetime.now()
        global_configs = configuration_mock.get_configuration_default()

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.available_slots = resources_mock.get_scheduler_by_journey(maria.journey, mes=today.month, ano=today.year)

        time_available_previous = 0
        for date_str in maria.available_slots:
            for slot in maria.available_slots[date_str]:
                time_available_previous += slot.minutes()

        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.is_deadline = True
        planjob = Planjob(30, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])], configs=pj_configs)

        self.assertIsNone(planjob.allocated_resources)
        self.assertEquals(len(planjob.execution_slots), 0)

        scheduler = Scheduler([maria], [planjob], global_configs)
        scheduler.allocate_planjob(planjob)

        time_available_current = 0
        for date_str in maria.available_slots:
            for slot in maria.available_slots[date_str]:
                time_available_current += slot.minutes()

        self.assertEquals(len(planjob.allocated_resources), 1)
        self.assertTrue(maria in planjob.allocated_resources)
        self.assertEquals(len(planjob.execution_slots), 1)
        self.assertTrue(planjob.execution_slots[0].minutes() >= 30)
        self.assertEquals(time_available_previous, time_available_current)

    def test_deadline_planjob_finish_time_outside_journey_error(self):
        global_configs = configuration_mock.get_configuration_default()

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.available_slots = {}

        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.is_deadline = True
        planjob = Planjob(30, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])], configs=pj_configs)

        scheduler = Scheduler([maria], [planjob], global_configs)
        try:
            scheduler.allocate_planjob(planjob)
            assert False
        except InsufficientResourceCalendarException as e:
            self.assertTrue(isinstance(e.value, dict))
            self.assertTrue(planjob.id in e.value["planjobs"])
            self.assertTrue(maria.id in e.value["resources"])

    def test_planjob_deadline_non_working_days(self):
        today = datetime(2018, 8, 1)
        global_configs = configuration_mock.get_configuration_default()
        non_working_days = ['2018/08/04', '2018/08/05']

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_default()
        maria.available_slots = resources_mock.get_scheduler_by_journey(maria.journey, mes=8, ano=2018)

        time_available_previous = 0
        for date_str in maria.available_slots:
            for slot in maria.available_slots[date_str]:
                time_available_previous += slot.minutes()

        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.is_deadline = True
        pj_configs.only_working_days = True
        planjob = Planjob(7200, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])], configs=pj_configs)

        self.assertIsNone(planjob.allocated_resources)
        self.assertEquals(len(planjob.execution_slots), 0)

        scheduler = Scheduler([maria], [planjob], global_configs, non_working_days)
        scheduler.allocate_planjob(planjob)

        time_available_current = 0
        for date_str in maria.available_slots:
            for slot in maria.available_slots[date_str]:
                time_available_current += slot.minutes()

        self.assertEquals(len(planjob.allocated_resources), 1)
        self.assertTrue(maria in planjob.allocated_resources)
        self.assertEquals(len(planjob.execution_slots), 1)
        self.assertEquals(planjob.execution_slots[0].finish_time.strftime(utils.DATE_FORMAT), "2018/08/08")
        self.assertEquals(time_available_previous, time_available_current)

if __name__ == '__main__':
    unittest.main()
