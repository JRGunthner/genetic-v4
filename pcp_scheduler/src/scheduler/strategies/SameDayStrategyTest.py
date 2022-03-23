import unittest

from datetime import datetime, timedelta

from pcp_scheduler.src.scheduler.strategies.SameDayStrategy import SameDayStrategy
from pcp_scheduler.src.model.ResourceCharacteristic import ResourceCharacteristic
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler.SchedulerFilter import SchedulerFilter

from pcp_scheduler.mock import configuration_mock, resources_mock, journey_mock, load_balancer_mock
from pcp_scheduler.utils import utils


class SameDayStrategyTestCase(unittest.TestCase):

    def test_allocate_simple_planjob(self):
        global_configs = configuration_mock.get_configuration_default()
        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        default_configs_planjob.same_day = True

        maria = ResourceCharacteristic(1, resources=["5"])
        planjob1 = Planjob(180, "planjob1", [DesiredResource([maria])], configs=default_configs_planjob)
        planjob1.allocated_resources = [resources_mock.get_maria()]

        potential_slots = {}
        potential_slots["01/08/2017"] = {
            (datetime(2017, 8, 1, 22), datetime(2017, 8, 2, 3, 30)): {
                planjob1: [Slot(datetime(2017, 8, 1), datetime(2017, 8, 1, 22), datetime(2017, 8, 2, 3, 30))]},
        }
        potential_slots["02/08/2017"] = {
            (datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))]},
        }

        self.assertEqual(planjob1.execution_slots, [])
        strategy = SameDayStrategy([planjob1], potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob1.execution_slots, [])
        self.assertEqual(len(planjob1.execution_slots), 1)

        slot = planjob1.execution_slots[0]
        self.assertEqual(slot.date.strftime("%Y/%m/%d"), "2017/08/02")
        self.assertEqual(slot.start_time.strftime("%Y/%m/%d %H:%M"), "2017/08/02 08:00")
        self.assertEqual(slot.finish_time.strftime("%Y/%m/%d %H:%M"), "2017/08/02 11:00")

    def test_allocate_simple_planjob_fractioned(self):
        global_configs = configuration_mock.get_configuration_default()
        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        default_configs_planjob.same_day = True
        default_configs_planjob.fractioned_between_planjobs = True

        maria = ResourceCharacteristic(1, resources=["5"])
        planjob1 = Planjob(420, "planjob1", [DesiredResource([maria])], configs=default_configs_planjob)

        potential_slots = {}
        potential_slots["01/08/2017"] = {
            (datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 21)): {
                planjob1: [Slot(datetime(2017, 8, 1), datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 21))]
            },
            (datetime(2017, 8, 1, 22), datetime(2017, 8, 2, 3, 30)): {
                planjob1: [Slot(datetime(2017, 8, 1), datetime(2017, 8, 1, 22), datetime(2017, 8, 2, 3, 30))]
            }
        }
        potential_slots["02/08/2017"] = {
            (datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))]},
            (datetime(2017, 8, 2, 12), datetime(2017, 8, 2, 19)): {
                planjob1: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 12), datetime(2017, 8, 2, 19))]}
        }

        self.assertEqual(planjob1.execution_slots, [])
        strategy = SameDayStrategy([planjob1], potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob1.execution_slots, [])
        self.assertEqual(len(planjob1.execution_slots), 2)

        slot1 = planjob1.execution_slots[0]
        self.assertEqual(slot1.date.strftime("%Y/%m/%d"), "2017/08/02")
        self.assertEqual(slot1.start_time.strftime("%Y/%m/%d %H:%M"), "2017/08/02 08:00")
        self.assertEqual(slot1.finish_time.strftime("%Y/%m/%d %H:%M"), "2017/08/02 11:30")

        slot2 = planjob1.execution_slots[-1]
        self.assertEqual(slot2.date.strftime("%Y/%m/%d"), "2017/08/02")
        self.assertEqual(slot2.start_time.strftime("%Y/%m/%d %H:%M"), "2017/08/02 12:00")
        self.assertEqual(slot2.finish_time.strftime("%Y/%m/%d %H:%M"), "2017/08/02 15:30")

    def test_allocate_simple_planjob_fractioned_2(self):
        global_configs = configuration_mock.get_configuration_default()
        default_configs_planjob = configuration_mock.get_default_configs_planjob()
        default_configs_planjob.same_day = True
        default_configs_planjob.fractioned_between_planjobs = True

        maria = ResourceCharacteristic(1, resources=["5"])
        planjob1 = Planjob(420, "planjob1", [DesiredResource([maria])], configs=default_configs_planjob)

        potential_slots = {}
        potential_slots["01/08/2017"] = {
            (datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 23)): {
                planjob1: [Slot(datetime(2017, 8, 1), datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 21))]}
        }
        potential_slots["02/08/2017"] = {
            (datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))]}
        }
        potential_slots["03/08/2017"] = {
            (datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 11, 30))]},
            (datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19)): {
                planjob1: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19))]}
        }

        self.assertEqual(planjob1.execution_slots, [])
        strategy = SameDayStrategy([planjob1], potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob1.execution_slots, [])
        self.assertEqual(len(planjob1.execution_slots), 2)

        slot1 = planjob1.execution_slots[0]
        self.assertEqual(slot1.date.strftime("%Y/%m/%d"), "2017/08/03")
        self.assertEqual(slot1.start_time.strftime("%Y/%m/%d %H:%M"), "2017/08/03 08:00")
        self.assertEqual(slot1.finish_time.strftime("%Y/%m/%d %H:%M"), "2017/08/03 11:30")

        slot2 = planjob1.execution_slots[1]
        self.assertEqual(slot2.date.strftime("%Y/%m/%d"), "2017/08/03")
        self.assertEqual(slot2.start_time.strftime("%Y/%m/%d %H:%M"), "2017/08/03 12:00")
        self.assertEqual(slot2.finish_time.strftime("%Y/%m/%d %H:%M"), "2017/08/03 15:30")

    def test_allocate_same_start_planjobs_fractioned(self):
        global_configs = configuration_mock.get_configuration_default()
        config1 = configuration_mock.get_default_configs_planjob()
        config1.same_day = True
        config1.fractioned_between_planjobs = True

        config2 = configuration_mock.get_default_configs_planjob()
        config2.same_day = True

        acabamento = DesiredResource([ResourceCharacteristic(sectors=["acabamento"], hour_type=1)])
        planjob1 = Planjob(420, "planjob1", [acabamento], configs=config1)
        planjob2 = Planjob(120, "planjob2", [acabamento], configs=config2)
        planjob3 = Planjob(180, "planjob3", [acabamento], configs=config2)

        planjob1.allocated_resources = [resources_mock.get_maria()]
        planjob2.allocated_resources = [resources_mock.get_joao()]
        planjob3.allocated_resources = [resources_mock.get_pedro()]

        planjob1.same_start = ["planjob2", "planjob3"]
        planjob2.same_start = ["planjob1", "planjob3"]
        planjob3.same_start = ["planjob2", "planjob1"]

        potential_slots = {}
        potential_slots["2017/08/01"] = {
            (datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 23)): {
                planjob1: [Slot(datetime(2017, 8, 1), datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 23))]}
        }
        potential_slots["2017/08/02"] = {
            (datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))],
                planjob2: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))],
                planjob3: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))]}
        }
        potential_slots["2017/08/03"] = {
            (datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 11, 30))],
                planjob2: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 7), datetime(2017, 8, 3, 11, 30))],
                planjob3: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 12, 30))]},
            (datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19)): {
                planjob1: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19))],
                planjob2: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19))],
                planjob3: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19))]}
        }

        self.assertEqual(planjob1.execution_slots, [])
        self.assertEqual(planjob2.execution_slots, [])
        self.assertEqual(planjob3.execution_slots, [])

        strategy = SameDayStrategy([planjob2, planjob3, planjob1], potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob1.execution_slots, [])
        self.assertNotEqual(planjob2.execution_slots, [])
        self.assertNotEqual(planjob3.execution_slots, [])
        self.assertEqual(len(planjob1.execution_slots), 2)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(len(planjob3.execution_slots), 1)

        for planjob in [planjob1, planjob2, planjob3]:
            self.assertEqual(planjob.execution_slots[0].date.strftime("%Y/%m/%d"), "2017/08/03")
            self.assertEqual(planjob.execution_slots[0].start_time.strftime("%Y/%m/%d %H:%M"), "2017/08/03 08:00")

    def test_allocate_same_finish_planjobs(self):
        global_configs = configuration_mock.get_configuration_default()
        config1 = configuration_mock.get_default_configs_planjob()
        config1.same_day = True
        config1.fractioned_between_planjobs = True

        config2 = configuration_mock.get_default_configs_planjob()
        config2.same_day = True

        acabamento = DesiredResource([ResourceCharacteristic(sectors=["acabamento"], hour_type=1)])
        planjob1 = Planjob(420, "planjob1", [acabamento], configs=config1)
        planjob2 = Planjob(120, "planjob2", [acabamento], configs=config2)
        planjob3 = Planjob(180, "planjob3", [acabamento], configs=config2)

        planjob1.allocated_resources = [resources_mock.get_joao()]
        planjob2.allocated_resources = [resources_mock.get_pedro()]
        planjob3.allocated_resources = [resources_mock.get_luisa()]

        planjob1.same_finish = ["planjob2", "planjob3"]
        planjob2.same_finish = ["planjob1", "planjob3"]
        planjob3.same_finish = ["planjob2", "planjob1"]

        potential_slots = {}
        potential_slots["2017/08/01"] = {
            (datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 23)): {
                planjob1: [Slot(datetime(2017, 8, 1), datetime(2017, 8, 1, 18), datetime(2017, 8, 1, 23))]}
        }
        potential_slots["2017/08/02"] = {
            (datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))],
                planjob2: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))],
                planjob3: [Slot(datetime(2017, 8, 2), datetime(2017, 8, 2, 8), datetime(2017, 8, 2, 11, 30))]}
        }
        potential_slots["2017/08/03"] = {
            (datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 11, 30)): {
                planjob1: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 11, 30))],
                planjob2: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 7), datetime(2017, 8, 3, 11, 30))],
                planjob3: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 8), datetime(2017, 8, 3, 12, 30))]},
            (datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19)): {
                planjob1: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19))],
                planjob2: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19))],
                planjob3: [Slot(datetime(2017, 8, 3), datetime(2017, 8, 3, 12), datetime(2017, 8, 3, 19))]}
        }
        potential_slots["2017/08/04"] = {
            (datetime(2017, 8, 4, 8), datetime(2017, 8, 4, 16, 30)): {
                planjob1: [Slot(datetime(2017, 8, 4), datetime(2017, 8, 4, 8), datetime(2017, 8, 4, 17, 30))],
                planjob2: [Slot(datetime(2017, 8, 4), datetime(2017, 8, 4, 7), datetime(2017, 8, 4, 18, 30))],
                planjob3: [Slot(datetime(2017, 8, 4), datetime(2017, 8, 4, 8), datetime(2017, 8, 4, 16, 30))]}
        }

        self.assertEqual(planjob1.execution_slots, [])
        self.assertEqual(planjob2.execution_slots, [])
        self.assertEqual(planjob3.execution_slots, [])

        strategy = SameDayStrategy([planjob2, planjob3, planjob1], potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob1.execution_slots, [])
        self.assertNotEqual(planjob2.execution_slots, [])
        self.assertNotEqual(planjob3.execution_slots, [])
        self.assertEqual(len(planjob1.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(len(planjob3.execution_slots), 1)

        for planjob in [planjob1, planjob2, planjob3]:
            self.assertEqual(planjob.execution_slots[0].date.strftime("%Y/%m/%d"), "2017/08/04")
            self.assertEqual(planjob.execution_slots[0].finish_time.strftime("%Y/%m/%d %H:%M"), "2017/08/04 15:00")

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

        strategy = SameDayStrategy([planjob], potential_slots, configs)
        strategy.allocate()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertNotEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(planjob.allocated_resources[0].id, luisa.id)

    def test_load_balancer_same_start(self):
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

        strategy = SameDayStrategy([planjob, planjob2], potential_slots, configs)
        strategy.allocate()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertNotEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(planjob.allocated_resources[0].id, luisa.id)

        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)

        self.assertEqual(planjob.execution_slots[0].start_time, planjob2.execution_slots[0].start_time)

    def test_load_balancer_same_start(self):
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

        strategy = SameDayStrategy([planjob, planjob2], potential_slots, configs)
        strategy.allocate()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertNotEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(planjob.allocated_resources[0].id, luisa.id)

        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)

        self.assertEqual(planjob.execution_slots[0].finish_time, planjob2.execution_slots[0].finish_time)

    def test_allocate_simple_planjob_fractioned_intervals(self):
        global_configs = configuration_mock.get_configuration_default()
        config1 = configuration_mock.get_default_configs_planjob()
        config1.same_day = True
        config1.fractioned_between_intervals = True

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

        planjob = Planjob(420, "planjob1", [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs=config1)
        planjob.allocated_resources = [ana]
        filter = SchedulerFilter([planjob], global_configs, [planjob])
        potential_slots = filter.define_correspondent_slots()

        self.assertEqual(planjob.execution_slots, [])

        strategy = SameDayStrategy([planjob], potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob.execution_slots, [])
        self.assertEqual(len(planjob.execution_slots), 2)

        tomorrow = today + timedelta(days=1)
        start_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9)
        self.assertEqual(planjob.execution_slots[0].date.date(), tomorrow.date())
        self.assertEqual(planjob.execution_slots[0].start_time, start_time)

    def test_allocate_same_start_planjobs_fractioned_intervals(self):
        global_configs = configuration_mock.get_configuration_default()
        config1 = configuration_mock.get_default_configs_planjob()
        config1.same_day = True
        config1.fractioned_between_intervals = True
        config2 = configuration_mock.get_default_configs_planjob()
        config2.same_day = True

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

        joao = resources_mock.get_joao()
        joao.available_slots = resources_mock.dois_dias_livres_seguidos(today)
        pedro = resources_mock.get_pedro()
        pedro.available_slots = resources_mock.dois_dias_livres_seguidos(today)

        acabamento = DesiredResource([ResourceCharacteristic(sectors=["acabamento"], hour_type=1)])
        planjob1 = Planjob(420, "planjob1", [acabamento], configs=config1)
        planjob2 = Planjob(120, "planjob2", [acabamento], configs=config2)
        planjob3 = Planjob(180, "planjob3", [acabamento], configs=config2)

        planjob1.allocated_resources = [ana]
        planjob2.allocated_resources = [joao]
        planjob3.allocated_resources = [pedro]

        planjob1.same_start = ["planjob2", "planjob3"]
        planjob2.same_start = ["planjob1", "planjob3"]
        planjob3.same_start = ["planjob2", "planjob1"]

        planjobs = [planjob1, planjob2, planjob3]
        filter = SchedulerFilter(planjobs, global_configs, planjobs, same_start=True)
        potential_slots = filter.define_correspondent_slots()

        self.assertEqual(planjob1.execution_slots, [])
        self.assertEqual(planjob2.execution_slots, [])
        self.assertEqual(planjob3.execution_slots, [])

        strategy = SameDayStrategy([planjob2, planjob3, planjob1], potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob1.execution_slots, [])
        self.assertNotEqual(planjob2.execution_slots, [])
        self.assertNotEqual(planjob3.execution_slots, [])
        self.assertEqual(len(planjob1.execution_slots), 2)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(len(planjob3.execution_slots), 1)

        tomorrow = today + timedelta(days=1)
        for planjob in [planjob1, planjob2, planjob3]:
            self.assertEqual(planjob.execution_slots[0].date.date(), tomorrow.date())
            start_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9)
            self.assertEqual(planjob.execution_slots[0].start_time, start_time)

    def test_simple_planjob_nonstop_infinity_same_day(self):
        grid = resources_mock.grid_todo_livre()
        global_configs = configuration_mock.get_configuration_default()
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_infinity = True
        configs_pj.same_day = True

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        planjob = Planjob(899, 1, [DesiredResource([ResourceCharacteristic(resources=ana.id)])], configs=configs_pj)
        planjob.allocated_resources = [ana]

        filter = SchedulerFilter([planjob], global_configs, [planjob])
        potential_slots = filter.define_correspondent_slots()

        strategy = SameDayStrategy([planjob], potential_slots, global_configs)
        strategy.allocate()

        self.assertEqual(len(planjob.execution_slots), 1)

        time = (planjob.execution_slots[0].finish_time - planjob.execution_slots[0].start_time).total_seconds() // 60
        self.assertEqual(time, planjob.time+planjob.setup)

        execution_slot = planjob.execution_slots[0]
        self.assertEqual(execution_slot.start_time.date(), execution_slot.finish_time.date())

    def test_allocate_same_start_planjobs_nonstop_infinity(self):
        global_configs = configuration_mock.get_configuration_default()
        config1 = configuration_mock.get_default_configs_planjob()
        config1.same_day = True
        config1.nonstop_infinity = True

        config2 = configuration_mock.get_default_configs_planjob()
        config2.same_day = True

        acabamento = DesiredResource([ResourceCharacteristic(sectors=["acabamento"], hour_type=1)])
        planjob1 = Planjob(820, "planjob1",
                           [DesiredResource([ResourceCharacteristic(resources=resources_mock.ana.id)])], configs=config1)
        planjob2 = Planjob(120, "planjob2", [acabamento], configs=config2)
        planjob3 = Planjob(180, "planjob3", [acabamento], configs=config2)

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        joao = resources_mock.get_joao()
        joao.available_slots = resources_mock.um_mes_livre()
        pedro = resources_mock.get_pedro()
        pedro.available_slots = resources_mock.um_mes_livre()

        planjob1.allocated_resources = [ana]
        planjob2.allocated_resources = [joao]
        planjob3.allocated_resources = [pedro]

        planjob1.same_start = ["planjob2", "planjob3"]
        planjob2.same_start = ["planjob1", "planjob3"]
        planjob3.same_start = ["planjob2", "planjob1"]

        planjobs = [planjob1, planjob2, planjob3]
        filter = SchedulerFilter(planjobs, global_configs, planjobs, same_start=True)
        potential_slots = filter.define_correspondent_slots()

        self.assertEqual(planjob1.execution_slots, [])
        self.assertEqual(planjob2.execution_slots, [])
        self.assertEqual(planjob3.execution_slots, [])

        strategy = SameDayStrategy(planjobs, potential_slots, global_configs)
        strategy.allocate()

        self.assertNotEqual(planjob1.execution_slots, [])
        self.assertNotEqual(planjob2.execution_slots, [])
        self.assertNotEqual(planjob3.execution_slots, [])
        self.assertEqual(len(planjob1.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(len(planjob3.execution_slots), 1)

        self.assertEqual(planjob1.execution_slots[0].start_time, planjob2.execution_slots[0].start_time)
        self.assertEqual(planjob1.execution_slots[0].start_time, planjob3.execution_slots[0].start_time)
        self.assertEqual(planjob2.execution_slots[0].start_time, planjob3.execution_slots[0].start_time)



if __name__ == '__main__':
    unittest.main()
