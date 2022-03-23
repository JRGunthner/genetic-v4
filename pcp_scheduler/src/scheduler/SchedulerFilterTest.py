import unittest

from datetime import datetime, timedelta
from copy import deepcopy

from pcp_scheduler.utils import utils

from pcp_scheduler.mock import resources_mock, configuration_mock
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.src.scheduler.SchedulerFilter import SchedulerFilter
from pcp_scheduler.src.model.ResourceCharacteristic import ResourceCharacteristic


class SchedulerFilterTestCase(unittest.TestCase):

    @unittest.skip("to do")
    def test_change_resources_availability(self):
        grid = resources_mock.grid_todo_livre()
        configs = configuration_mock.get_configuration_default()

        mimaki_desired = ResourceCharacteristic(2, sectors=['impressão'], groups=["high-quality"])
        planjob1 = Planjob(30, 'planjob1', [DesiredResource([mimaki_desired])])
        planjob1.min_start_date = datetime(2017, 5, 5, 10)
        planjob2 = Planjob(30, 'planjob2', [DesiredResource([mimaki_desired])])

        planjob1.successors.append('planjob2')
        planjob2.predecessors.append('planjob1')

        planjobs = [planjob1, planjob2]

        for resource in grid:
            if set(resource.sectors).intersection(mimaki_desired.sectors) != set([]) and \
                            set(resource.groups).intersection(mimaki_desired.groups) != set([]):
                resource_desired = resource
                break

        filter = SchedulerFilter(planjobs, configs, planjobs)
        resource_allocation = deepcopy(resource_desired.available_slots)

        filter.change_resource_availability(resource_allocation, planjob1)
        for date_str in resource_allocation.keys():
            date = datetime.strptime(date_str, utils.DATE_FORMAT).date()
            self.assertTrue(date >= planjob1.min_start_date.date())
            if date == planjob1.min_start_date.date():
                for time in resource_allocation[date_str]:
                    self.assertTrue(time.start_time >= planjob1.min_start_date)

        slot = Slot(datetime(2017, 5, 5, 10), datetime(2017, 5, 5, 10), datetime(2017, 5, 5, 10, 30))
        planjob1.execution_slots.append(slot)

        resource_allocation = deepcopy(resource_desired.available_slots)
        filter.change_resource_availability(resource_allocation, planjob2)
        for date_str in resource_allocation.keys():
            date = datetime.strptime(date_str, utils.DATE_FORMAT).date()
            self.assertTrue(date >= planjob1.execution_slots[-1].date.date())
            if date == planjob1.execution_slots[-1].date.date():
                for time in resource_allocation[date_str]:
                    self.assertTrue(time.start_time >= planjob1.execution_slots[-1].finish_time)

    def test_change_scheduler_by_intervals_fraction(self):
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

        planjob = Planjob(420, 1, [], planjob_configs)
        planjob.allocated_resources = [ana]

        filter = SchedulerFilter([planjob], configs, [planjob])
        filter.change_scheduler_by_intervals_fraction()

        self.assertEqual(len(ana.available_slots), 2)

        self.assertTrue(today_str in ana.available_slots.keys())
        self.assertEqual(len(ana.available_slots[today_str]), 2)
        self.assertEqual(len(list(ana.available_slots[today_str])[0].complement), 3)

        tomorrow = today + timedelta(days=1)
        tomorrow_str = tomorrow.strftime(utils.DATE_FORMAT)
        self.assertTrue(tomorrow_str in ana.available_slots.keys())

        self.assertEqual(len(ana.available_slots[tomorrow_str]), 1)

        self.assertTrue(ana.available_slots[tomorrow_str][0].complement is not None)
        self.assertEqual(len(ana.available_slots[tomorrow_str][0].complement), 1)

        self.assertTrue(ana.available_slots[tomorrow_str][0].complement[0].complement is None)

        self.assertEqual(ana.available_slots[tomorrow_str][0].start_time,
                        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9))
        self.assertEqual(ana.available_slots[tomorrow_str][0].finish_time,
                        datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12))

        self.assertEqual(ana.available_slots[tomorrow_str][0].complement[0].start_time,
                         datetime(tomorrow.year, tomorrow.month, tomorrow.day, 13))
        self.assertEqual(ana.available_slots[tomorrow_str][0].complement[0].finish_time,
                         datetime(tomorrow.year, tomorrow.month, tomorrow.day, 18))

    def test_filter_adjust_scheduler_to_planjobs_nonstop(self):
        global_configs = configuration_mock.get_configuration_default()
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_infinity = True

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        ana_dates_before = set(ana.available_slots.keys())
        planjob = Planjob(1440, 1, [], configs=configs_pj)
        planjob.allocated_resources = [ana]

        for (date, slots) in ana.available_slots.items():
            for slot in slots:
                self.assertLessEqual(slot.minutes(), planjob.time+planjob.setup)

        filter = SchedulerFilter([planjob], global_configs, [planjob])
        filter.change_scheduler_by_intervals_fraction()
        filter.adjust_scheduler_to_planjobs_nonstop()

        for (date, slots) in ana.available_slots.items():
            for slot in slots:
                self.assertGreaterEqual(slot.minutes(), planjob.time+planjob.setup)

        ana_dates_current = set(ana.available_slots.keys())
        self.assertTrue(ana_dates_current.issubset(ana_dates_before))
        self.assertEquals(len(ana_dates_before.difference(ana_dates_current)), 1)
        self.assertEquals(ana_dates_before.difference(ana_dates_current), {'2017/05/31'})

    def test_not_same_day_predecessor(self):
        global_configs = configuration_mock.get_configuration_default()
        configs_pj1 = configuration_mock.get_default_configs_planjob()
        configs_pj2 = configuration_mock.get_default_configs_planjob()
        configs_pj2.not_in_same_day_predecessor = True

        date_target = datetime(year=2017, month=11, day=1)
        date_target_nine_clock = date_target.replace(hour=9, minute=0, second=0)
        planjob = Planjob(40, 1, [], configs=configs_pj1)
        planjob2 = Planjob(60, 2, [], configs=configs_pj2)
        planjob3 = Planjob(60, 3, [], configs=configs_pj1)

        planjob.successors = [2, 3]
        planjob2.predecessors = [1]
        planjob3.predecessors = [1]
        planjob.execution_slots = [Slot(date_target, date_target_nine_clock, date_target_nine_clock+timedelta(minutes=planjob.time))]

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.uma_semana_livre(mes=date_target.month, ano=date_target.year)
        planjob.allocated_resources = [ana]

        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.uma_semana_livre(mes=date_target.month, ano=date_target.year)
        planjob2.allocated_resources = [maria]

        luisa = resources_mock.get_luisa()
        luisa.available_slots = resources_mock.uma_semana_livre(mes=date_target.month, ano=date_target.year)
        planjob3.allocated_resources = [luisa]

        self.assertTrue(date_target.date().strftime(utils.DATE_FORMAT) in maria.available_slots)
        self.assertTrue(date_target.date().strftime(utils.DATE_FORMAT) in luisa.available_slots)

        filter = SchedulerFilter([planjob2, planjob3], global_configs, [planjob, planjob2, planjob3])
        filter.change_scheduler_by_predecessors()

        self.assertFalse(date_target.date().strftime(utils.DATE_FORMAT) in maria.available_slots)
        self.assertTrue(date_target.date().strftime(utils.DATE_FORMAT) in luisa.available_slots)

if __name__ == '__main__':
    unittest.main()
