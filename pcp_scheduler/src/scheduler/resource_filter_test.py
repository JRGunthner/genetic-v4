import unittest

from datetime import datetime

from .resource_filter import ResourceFilter
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.src.model.ResourceCharacteristic import ResourceCharacteristic
from pcp_scheduler.mock import resources_mock, configuration_mock, journey_mock
from pcp_scheduler.utils import utils


class ResourceFilterTestCase(unittest.TestCase):

    def test_choose_by_hour_type(self):
        MAN_HOUR = 1
        MACHINE_HOUR = 2

        grid = resources_mock.grid_todo_livre()
        resource_filter = ResourceFilter([], {}, grid)

        resorces_man_hour = resource_filter.choose_by_hour_type(MAN_HOUR)
        resorces_machine_hour = resource_filter.choose_by_hour_type(MACHINE_HOUR)

        for resource in resorces_man_hour:
            self.assertEqual(resource.hour_type, MAN_HOUR)

        for resource in resorces_machine_hour:
            self.assertEqual(resource.hour_type, MACHINE_HOUR)

        self.assertEqual(len(resorces_man_hour) + len(resorces_machine_hour), len(grid))

    def test_choose_by_sectors(self):
        MAN_HOUR = 1
        sectors = ['acabamento']

        grid = resources_mock.grid_todo_livre()
        resource_filter = ResourceFilter([], {}, grid)

        qnt = 0
        for resource in grid:
            if set(sectors).intersection(resource.sectors) != {} and resource.hour_type == MAN_HOUR:
                qnt += 1

        resources = resource_filter.choose_by_sector(sectors, MAN_HOUR)

        for resource in resources:
            self.assertEqual(resource.hour_type, MAN_HOUR)
            self.assertNotEqual(set(sectors).intersection(resource.sectors), {})

        self.assertEqual(qnt, len(resources))

    def test_choose_by_group(self):
        MACHINE_HOUR = 2
        groups = ['mimaki']

        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()
        resource_filter = ResourceFilter([], configs, grid)

        qnt = 0
        for resource in grid:
            if set(groups).intersection(resource.groups) != {} and resource.hour_type == MACHINE_HOUR:
                qnt += 1

        resources = resource_filter.choose_by_group(groups, MACHINE_HOUR)

        for resource in resources:
            self.assertEqual(resource.hour_type, MACHINE_HOUR)
            self.assertNotEqual(set(groups).intersection(resource.sectors), {})

        self.assertEqual(qnt, len(resources))

    def test_choose_by_resourcesId(self):
        resources_id = [1,2]

        grid = resources_mock.grid_todo_livre()
        resource_filter = ResourceFilter([], {}, grid)

        qnt = 0
        for resource in grid:
            if resource.id in resources_id:
                qnt += 1

        resources = resource_filter.choose_by_resource(resources_id)

        for resource in resources:
            self.assertTrue(resource.id in resources_id)

        self.assertEqual(qnt, len(resources))

    def test_resource_is_suitable_scheduled_date_simple_planjob(self):
        global_configs = configuration_mock.get_configuration_default()
        pj_configs = configuration_mock.get_default_configs_planjob()

        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.um_mes_livre(mes=4, ano=2017)

        planjob1 = Planjob(60, 1, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob1.scheduled_date = datetime(2017, 4, 2, 9)

        planjob2 = Planjob(360, 2, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob2.scheduled_date = datetime(2017, 4, 2, 9)

        resource_filter = ResourceFilter([planjob1, planjob2], global_configs, [maria])

        self.assertTrue(resource_filter.resource_is_suitable(maria, planjob1, planjob1.scheduled_date))
        self.assertFalse(resource_filter.resource_is_suitable(maria, planjob2, planjob2.scheduled_date))

    def test_resource_is_suitable_scheduled_date_simple_planjob_fractioned_btw_planjobs(self):
        global_configs = configuration_mock.get_configuration_default()
        global_configs.fractioned_floor_limit = 30
        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.fractioned_between_planjobs = True

        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.um_mes_livre(mes=4, ano=2017)

        planjob1 = Planjob(60, 1, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob1.scheduled_date = datetime(2017, 4, 2, 11, 30)

        planjob2 = Planjob(360, 2, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob2.scheduled_date = datetime(2017, 4, 2, 11, 45)

        resource_filter = ResourceFilter([planjob1, planjob2], global_configs, [maria])

        self.assertTrue(resource_filter.resource_is_suitable(maria, planjob1, planjob1.scheduled_date))
        self.assertFalse(resource_filter.resource_is_suitable(maria, planjob2, planjob2.scheduled_date))

    def test_resource_is_suitable_scheduled_date_simple_planjob_fractioned_btw_intervals(self):
        global_configs = configuration_mock.get_configuration_default()
        global_configs.fractioned_floor_limit = 30
        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.fractioned_between_intervals = True

        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.um_mes_livre(mes=4, ano=2017)
        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre(mes=4, ano=2017)

        planjob1 = Planjob(60, 1, DesiredResource(ResourceCharacteristic(resources=[ana.id])), pj_configs)
        planjob1.scheduled_date = datetime(2017, 4, 2, 11, 00)

        planjob2 = Planjob(360, 2, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob2.scheduled_date = datetime(2017, 4, 2, 9)

        target_date_str = planjob2.scheduled_date.strftime(utils.DATE_FORMAT)
        maria.journey = journey_mock.get_journey_default()
        maria.available_slots[target_date_str] = \
            [Slot(datetime(2017, 4, 2), datetime(2017, 4, 2, 9), datetime(2017, 4, 2, 10)),
             Slot(datetime(2017, 4, 2), datetime(2017, 4, 2, 11), datetime(2017, 4, 2, 12)),
             Slot(datetime(2017, 4, 2), datetime(2017, 4, 2, 13), datetime(2017, 4, 2, 18))]

        resource_filter = ResourceFilter([planjob1, planjob2], global_configs, [maria, ana])

        self.assertTrue(resource_filter.resource_is_suitable(ana, planjob1, planjob1.scheduled_date))
        self.assertFalse(resource_filter.resource_is_suitable(maria, planjob2, planjob2.scheduled_date))

    def test_resource_is_suitable_scheduled_date_simple_planjob_nonstop_vigily(self):
        global_configs = configuration_mock.get_configuration_default()
        global_configs.nonstop_vigily_floor_limit = 30
        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.nonstop_vigily_mode = True

        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.um_mes_livre(mes=4, ano=2017)

        planjob1 = Planjob(60, 1, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob1.scheduled_date = datetime(2017, 4, 2, 11, 30)

        planjob2 = Planjob(360, 2, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob2.scheduled_date = datetime(2017, 4, 2, 11, 45)

        resource_filter = ResourceFilter([planjob1, planjob2], global_configs, [maria])

        self.assertTrue(resource_filter.resource_is_suitable(maria, planjob1, planjob1.scheduled_date))
        self.assertFalse(resource_filter.resource_is_suitable(maria, planjob2, planjob2.scheduled_date))

    def test_resource_is_suitable_scheduled_date_simple_planjob_nonstop_infinity(self):
        global_configs = configuration_mock.get_configuration_default()
        global_configs.nonstop_vigily_floor_limit = 30
        pj_configs = configuration_mock.get_default_configs_planjob()
        pj_configs.nonstop_infinity = True

        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.um_mes_livre(mes=4, ano=2017)
        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre(mes=4, ano=2017)

        planjob1 = Planjob(60, 1, DesiredResource(ResourceCharacteristic(resources=[ana.id])), pj_configs)
        planjob1.scheduled_date = datetime(2017, 4, 2, 11, 30)

        planjob2 = Planjob(360, 2, DesiredResource(ResourceCharacteristic(resources=[maria.id])), pj_configs)
        planjob2.scheduled_date = datetime(2017, 4, 2, 9)

        target_date_str = planjob2.scheduled_date.strftime(utils.DATE_FORMAT)
        maria.journey = journey_mock.get_journey_default()
        maria.available_slots[target_date_str] = \
            [Slot(datetime(2017, 4, 2), datetime(2017, 4, 2, 9), datetime(2017, 4, 2, 10)),
             Slot(datetime(2017, 4, 2), datetime(2017, 4, 2, 11), datetime(2017, 4, 2, 12)),
             Slot(datetime(2017, 4, 2), datetime(2017, 4, 2, 13), datetime(2017, 4, 2, 18))]

        resource_filter = ResourceFilter([planjob1, planjob2], global_configs, [maria, ana])

        self.assertTrue(resource_filter.resource_is_suitable(ana, planjob1, planjob1.scheduled_date))
        self.assertFalse(resource_filter.resource_is_suitable(maria, planjob2, planjob2.scheduled_date))

if __name__ == '__main__':
    unittest.main()
