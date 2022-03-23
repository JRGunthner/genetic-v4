import unittest
from datetime import datetime, timedelta

from pcp_scheduler.mock import resources_mock, configuration_mock, journey_mock
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler.strategies.NonstopVigilStrategy import NonstopVigilyStrategy
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException


class NonStopVigilTestCase(unittest.TestCase):

    def test_allocate_simple_planjob(self):
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_vigily = True

        ana = resources_mock.get_ana()
        ana.journey = journey_mock.get_journey_6h_morning()
        ana.available_slots = resources_mock.get_scheduler_by_journey(ana.journey)

        pedro = resources_mock.get_pedro()
        pedro.journey = journey_mock.get_journey_6h_afternoon()
        pedro.available_slots = resources_mock.get_scheduler_by_journey(pedro.journey)

        ricardo = resources_mock.get_ricardo()
        ricardo.journey = journey_mock.get_journey_6h_evening()
        ricardo.available_slots = resources_mock.get_scheduler_by_journey(ricardo.journey)

        luisa = resources_mock.get_luisa()
        luisa.journey = journey_mock.get_journey_6h_night()
        luisa.available_slots = resources_mock.get_scheduler_by_journey(luisa.journey)

        solutions = [[ana], [pedro], [ricardo], [luisa]]

        planjob = Planjob(1520, 1, [], configs=configs_pj)
        planjob.scheduled_date = datetime(2017, 5, 5, 9)

        self.assertEqual(len(planjob.execution_slots), 0)

        strategy = NonstopVigilyStrategy(planjob, solutions, configuration_mock.get_configuration_default())
        strategy.allocate()

        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)
        finish_time_expected = planjob.scheduled_date + timedelta(minutes=planjob.time + planjob.setup)
        self.assertEqual(planjob.execution_slots[0].finish_time, finish_time_expected)

        self.assertEquals(len(planjob.allocated_resources), 4)
        self.assertTrue(ana in planjob.allocated_resources)
        self.assertTrue(ricardo in planjob.allocated_resources)
        self.assertTrue(pedro in planjob.allocated_resources)
        self.assertTrue(luisa in planjob.allocated_resources)

    def test_allocate_simple_planjob_with_predecessors(self):
        configs_pj_normal = configuration_mock.get_default_configs_planjob()
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_vigily = True

        ana = resources_mock.get_ana()
        ana.journey = journey_mock.get_journey_6h_morning()
        ana.available_slots = resources_mock.get_scheduler_by_journey(ana.journey)

        pedro = resources_mock.get_pedro()
        pedro.journey = journey_mock.get_journey_6h_afternoon()
        pedro.available_slots = resources_mock.get_scheduler_by_journey(pedro.journey)

        ricardo = resources_mock.get_ricardo()
        ricardo.journey = journey_mock.get_journey_6h_evening()
        ricardo.available_slots = resources_mock.get_scheduler_by_journey(ricardo.journey)

        luisa = resources_mock.get_luisa()
        luisa.journey = journey_mock.get_journey_6h_night()
        luisa.available_slots = resources_mock.get_scheduler_by_journey(luisa.journey)

        solutions = [[ana], [pedro], [ricardo], [luisa]]

        planjob_parent = Planjob(60, 2, [], configs=configs_pj_normal)
        planjob_parent.execution_slots = [Slot(datetime(2017, 5, 10), datetime(2017, 5, 10, 15), datetime(2017, 5, 10, 16))]

        planjob = Planjob(1520, 1, [], configs=configs_pj)

        self.assertEqual(len(planjob.execution_slots), 0)

        strategy = NonstopVigilyStrategy(planjob, solutions, configuration_mock.get_configuration_default(),
                                         predecessors=[planjob_parent])
        strategy.allocate()

        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertTrue(planjob.execution_slots[0].start_time >= planjob_parent.execution_slots[-1].finish_time)

        finish_time_expected = planjob.execution_slots[0].start_time + timedelta(minutes=planjob.time + planjob.setup)
        self.assertEqual(planjob.execution_slots[0].finish_time, finish_time_expected)

        self.assertEquals(len(planjob.allocated_resources), 4)
        self.assertTrue(ana in planjob.allocated_resources)
        self.assertTrue(ricardo in planjob.allocated_resources)
        self.assertTrue(pedro in planjob.allocated_resources)
        self.assertTrue(luisa in planjob.allocated_resources)

    def test_allocate_simple_planjob_insufficient_resources(self):
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_vigily = True

        ana = resources_mock.get_ana()
        ana.journey = journey_mock.get_journey_6h_morning()
        ana.available_slots = resources_mock.get_scheduler_by_journey(ana.journey)

        maria = resources_mock.get_maria()
        maria.journey = journey_mock.get_journey_6h_morning()
        maria.available_slots = resources_mock.get_scheduler_by_journey(maria.journey)

        pedro = resources_mock.get_pedro()
        pedro.journey = journey_mock.get_journey_6h_afternoon()
        pedro.available_slots = resources_mock.get_scheduler_by_journey(pedro.journey)

        ricardo = resources_mock.get_ricardo()
        ricardo.journey = journey_mock.get_journey_6h_evening()
        ricardo.available_slots = resources_mock.get_scheduler_by_journey(ricardo.journey)

        luisa = resources_mock.get_luisa()
        luisa.journey = journey_mock.get_journey_6h_night()
        luisa.available_slots = resources_mock.get_scheduler_by_journey(luisa.journey)

        solutions = [[ana, maria], [pedro, pedro], [ricardo], [luisa]]

        planjob = Planjob(1520, 1, [], configs=configs_pj)
        planjob.scheduled_date = datetime(2017, 5, 5, 9)

        self.assertEqual(len(planjob.execution_slots), 0)

        strategy = NonstopVigilyStrategy(planjob, solutions, configuration_mock.get_configuration_default())
        try:
            strategy.allocate()
            self.assertTrue(False)
        except InsufficientResourceCalendarException as e:
            self.assertTrue(isinstance(e.value, dict))
            self.assertTrue(planjob.id in e.value['planjobs'])
            self.assertTrue(ana.id in e.value['resources'])
            self.assertTrue(maria.id in e.value['resources'])
            self.assertTrue(pedro.id in e.value['resources'])
            self.assertTrue(ricardo.id in e.value['resources'])
            self.assertTrue(luisa.id in e.value['resources'])


if __name__ == '__main__':
    unittest.main()
