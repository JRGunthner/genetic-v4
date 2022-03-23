import unittest
from datetime import datetime, timedelta

from pcp_scheduler.mock import resources_mock, configuration_mock, journey_mock, load_balancer_mock
from pcp_scheduler.src.exceptions.Exceptions import LoadBalancerViolationException
from pcp_scheduler.src.model.DesideredResource import DesiredResource
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.ResourceCharacteristic import ResourceCharacteristic
from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler.strategies.SchedledDateStrategy import ScheduledDateStrategy
from pcp_scheduler.utils import utils

class ScheduledDateStrategyTestCase(unittest.TestCase):

    def test_allocate_simple_planjob(self):
        maria = resources_mock.get_maria()
        maria.available_slots = resources_mock.um_mes_livre()

        planjob = Planjob(120, 1, [], configs=configuration_mock.get_default_configs_planjob())
        planjob.scheduled_date = datetime(2017, 5, 5, 13)
        planjob.allocated_resources = [maria]

        self.assertEqual(len(planjob.execution_slots), 0)

        strategy = ScheduledDateStrategy(planjobs=[planjob], configs=configuration_mock.get_configuration_default())
        strategy.allocate()

        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)
        finish_time_expected = planjob.scheduled_date + timedelta(minutes=planjob.time+planjob.setup)
        self.assertEqual(planjob.execution_slots[0].finish_time, finish_time_expected)

    def test_allocate_simple_planjob_fractioned(self):
        configs = configuration_mock.get_default_configs_planjob()
        configs.fractioned_between_planjobs = True

        ricardo = resources_mock.get_ricardo()
        ricardo.available_slots = resources_mock.um_mes_livre()

        planjob = Planjob(420, 1, [DesiredResource([ResourceCharacteristic(resources=[ricardo.id])])], configs)
        planjob.scheduled_date = datetime(2017, 5, 5, 13)
        planjob.allocated_resources = [ricardo]

        self.assertEqual(len(planjob.execution_slots), 0)

        strategy = ScheduledDateStrategy(planjobs=[planjob], configs=configuration_mock.get_configuration_default())
        strategy.allocate()

        self.assertEqual(len(planjob.execution_slots), 2)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)
        self.assertEqual(len(planjob.allocated_resources), 1)

        total = 0
        for slot in planjob.execution_slots:
            duration = (slot.finish_time - slot.start_time).total_seconds() / 60
            total += duration + planjob.setup

        duracao_esperada = planjob.time + 2*planjob.setup
        self.assertEqual(duracao_esperada, total)

    def test_allocate_same_start(self):
        global_configs = configuration_mock.get_configuration_default()
        config = configuration_mock.get_default_configs_planjob()
        scheduled_date = datetime(2017, 5, 12, 9)

        pedro = resources_mock.get_pedro()
        pedro.available_slots = resources_mock.um_mes_livre()
        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        ricardo = resources_mock.get_ricardo()
        ricardo.available_slots = resources_mock.um_mes_livre()

        acabamento = DesiredResource([ResourceCharacteristic(sectors=["acabamento"], hour_type=1)])
        planjob1 = Planjob(150, "planjob1", [acabamento], configs=config)
        planjob1.allocated_resources = [pedro]

        planjob2 = Planjob(120, "planjob2", [acabamento], configs=config)
        planjob2.allocated_resources = [ana]

        planjob3 = Planjob(140, "planjob3", [acabamento], configs=config)
        planjob3.allocated_resources = [ricardo]
        planjob3.scheduled_date = scheduled_date

        planjob1.same_start = ["planjob2", "planjob3"]
        planjob2.same_start = ["planjob1", "planjob3"]
        planjob3.same_start = ["planjob2", "planjob1"]

        planjob1.allocated_resources = [resources_mock.maria]
        planjob2.allocated_resources = [resources_mock.joao]
        planjob3.allocated_resources = [resources_mock.pedro]

        planjobs = [planjob1, planjob2, planjob3]

        self.assertEqual(len(planjob1.execution_slots), 0)
        self.assertEqual(len(planjob2.execution_slots), 0)
        self.assertEqual(len(planjob3.execution_slots), 0)

        strategy = ScheduledDateStrategy(planjobs=planjobs, configs=global_configs)
        strategy.allocate()

        self.assertEqual(len(planjob1.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(len(planjob3.execution_slots), 1)

        for planjob in planjobs:
            self.assertEqual(planjob.execution_slots[0].start_time, scheduled_date)

    def test_allocate_same_start_fractioned(self):
        global_configs = configuration_mock.get_configuration_default()
        config = configuration_mock.get_default_configs_planjob()
        config.fractioned_between_planjobs = True
        scheduled_date = datetime(2017, 5, 12, 9)

        pedro = resources_mock.get_pedro()
        pedro.available_slots = resources_mock.um_mes_livre()
        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        ricardo = resources_mock.get_ricardo()
        ricardo.available_slots = resources_mock.um_mes_livre()

        acabamento = DesiredResource([ResourceCharacteristic(sectors=["acabamento"], hour_type=1)])
        planjob1 = Planjob(180, "planjob1", [acabamento], configs=config)
        planjob1.allocated_resources = [pedro]

        planjob2 = Planjob(320, "planjob2", [acabamento], configs=config)
        planjob2.allocated_resources = [ana]

        planjob3 = Planjob(540, "planjob3", [acabamento], configs=config)
        planjob3.allocated_resources = [ricardo]
        planjob3.scheduled_date = scheduled_date

        planjob1.same_start = ["planjob2", "planjob3"]
        planjob2.same_start = ["planjob1", "planjob3"]
        planjob3.same_start = ["planjob2", "planjob1"]

        planjobs = [planjob1, planjob2, planjob3]

        self.assertEqual(len(planjob1.execution_slots), 0)
        self.assertEqual(len(planjob2.execution_slots), 0)
        self.assertEqual(len(planjob3.execution_slots), 0)

        strategy = ScheduledDateStrategy(planjobs=planjobs, configs=global_configs)
        strategy.allocate()

        self.assertEqual(len(planjob1.execution_slots), 1)
        self.assertEqual(len(planjob2.execution_slots), 2)
        self.assertEqual(len(planjob3.execution_slots), 3)

        for planjob in planjobs:
            self.assertEqual(planjob.execution_slots[0].start_time, scheduled_date)

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
        planjob.scheduled_date = datetime(2017, 5, 1, 10)

        strategy = ScheduledDateStrategy(planjobs=[planjob], configs=configs)
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
        planjob.scheduled_date = datetime(2017, 5, 1, 10)

        joao = resources_mock.joao
        joao.available_slots = resources_mock.um_dia_livre(target_date)

        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_start.append(planjob2)
        planjob2.same_start.append(planjob)

        strategy = ScheduledDateStrategy(planjobs=[planjob, planjob2], configs=configs)
        strategy.allocate()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertNotEqual(planjob.allocated_resources[0].id, maria.id)
        self.assertEqual(planjob.allocated_resources[0].id, luisa.id)

        self.assertEqual(len(planjob2.allocated_resources), 1)
        self.assertEqual(planjob2.allocated_resources[0].id, joao.id)

        self.assertEqual(planjob.execution_slots[0].start_time, planjob2.execution_slots[0].start_time)
        self.assertEqual(planjob.execution_slots[0].start_time, datetime(2017, 5, 1, 10))
        self.assertEqual(planjob2.execution_slots[0].start_time, datetime(2017, 5, 1, 10))

    def test_load_balancer_violation_simple_planjob(self):
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

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]
        planjob.scheduled_date = datetime(2017, 5, 1, 10)

        strategy = ScheduledDateStrategy(planjobs=[planjob], configs=configs)

        try:
            strategy.allocate()
        except LoadBalancerViolationException as e:
            self.assertTrue(isinstance(e.value, dict))
            self.assertEqual(e.value["resource_id"], maria.id)
            self.assertEqual(e.value["planjob_id"], planjob.id)
            self.assertEqual(e.value["desired_date"], target_date_str)

    def test_load_balancer_same_start_violation(self):
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

        planjob = Planjob(45, 1, [DesiredResource([ResourceCharacteristic(resources=[maria.id])])])
        planjob.process_id = process_id
        planjob.configs = configuration_mock.get_default_configs_planjob()
        planjob.allocated_resources = [maria]
        planjob.scheduled_date = datetime(2017, 5, 1, 10)

        joao = resources_mock.get_joao()
        joao.available_slots = resources_mock.um_dia_livre(target_date)

        planjob2 = Planjob(45, 2, [DesiredResource([ResourceCharacteristic(resources=[joao.id])])])
        planjob2.process_id = 2
        planjob2.configs = configuration_mock.get_default_configs_planjob()
        planjob2.allocated_resources = [joao]

        planjob.same_start.append(planjob2)
        planjob2.same_start.append(planjob)
        strategy = ScheduledDateStrategy(planjobs=[planjob, planjob2], configs=configs)

        try:
            strategy.allocate()
            assert False #ToDo colocar um assert fail aqui, deveia ter lançado exceção
        except LoadBalancerViolationException as e:
            self.assertTrue(isinstance(e.value, dict))
            self.assertEqual(e.value["resource_id"], maria.id)
            self.assertEqual(e.value["planjob_id"], planjob.id)
            self.assertEqual(e.value["desired_date"], target_date_str)

    def test_simple_planjob_fractioned_between_intervals(self):
        configs = configuration_mock.get_configuration_default()
        configs_pj1 = configuration_mock.get_default_configs_planjob()
        configs_pj1.fractioned_between_intervals = True

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

        planjob = Planjob(420, 1, [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs_pj1)
        planjob.scheduled_date = datetime(today.year, today.month, today.day, 11, 30)
        planjob.allocated_resources = [ana]

        strategy = ScheduledDateStrategy(planjobs=[planjob], configs=configs)
        strategy.allocate()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, ana.id)

        self.assertEqual(len(planjob.execution_slots), 3)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)

        tomorrow = today + timedelta(days=1)
        self.assertEqual(planjob.execution_slots[-1].date.date(), tomorrow.date())

        sum = 0
        for slot in planjob.execution_slots:
            sum += ((slot.finish_time - slot.start_time).total_seconds() // 60)

        self.assertEqual(sum, planjob.time + planjob.setup*len(planjob.execution_slots))

    def test_same_start_planjob_fractioned_between_intervals(self):
        configs = configuration_mock.get_configuration_default()
        configs_pj1 = configuration_mock.get_default_configs_planjob()
        configs_pj2 = configuration_mock.get_default_configs_planjob()
        configs_pj2.fractioned_between_intervals = True

        today = datetime.today()
        today_str = today.strftime(utils.DATE_FORMAT)

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.dois_dias_livres_seguidos(today)
        pedro = resources_mock.get_pedro()
        pedro.available_slots = {today_str: [Slot(datetime(today.year, today.month, today.day),
                                  datetime(today.year, today.month, today.day, 9),
                                  datetime(today.year, today.month, today.day, 15))]}

        first_slot = Slot(datetime(today.year, today.month, today.day),
                          datetime(today.year, today.month, today.day, 9),
                          datetime(today.year, today.month, today.day, 10))
        second_slot = Slot(datetime(today.year, today.month, today.day),
                           datetime(today.year, today.month, today.day, 11),
                           datetime(today.year, today.month, today.day, 12))

        ana.available_slots[today_str][0] = first_slot
        ana.available_slots[today_str].insert(1, second_slot)

        planjob = Planjob(420, 1, [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs_pj2)
        planjob.scheduled_date = datetime(today.year, today.month, today.day, 11, 30)
        planjob.allocated_resources = [ana]
        planjob2 = Planjob(120, 2, [DesiredResource([ResourceCharacteristic(resources=[pedro.id])])], configs_pj1)
        planjob2.allocated_resources = [pedro]

        planjob.same_start.append(planjob2)
        planjob2.same_start.append(planjob)

        strategy = ScheduledDateStrategy(planjobs=[planjob, planjob2], configs=configs)
        strategy.allocate()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, ana.id)

        self.assertEqual(len(planjob.execution_slots), 3)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)

        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(planjob2.execution_slots[0].start_time, planjob.scheduled_date)

        tomorrow = today + timedelta(days=1)
        self.assertEqual(planjob.execution_slots[-1].date.date(), tomorrow.date())

        sum = 0
        for slot in planjob.execution_slots:
            sum += ((slot.finish_time - slot.start_time).total_seconds() // 60)

        self.assertEqual(sum, planjob.time + planjob.setup*len(planjob.execution_slots))

    def test_allocate_simple_planjob_nonstop_infinity(self):
        configs_pj = configuration_mock.get_default_configs_planjob()
        configs_pj.nonstop_infinity = True
        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()

        planjob = Planjob(920, 1, [], configs=configs_pj)
        planjob.scheduled_date = datetime(2017, 5, 5, 13)
        planjob.allocated_resources = [ana]

        self.assertEqual(len(planjob.execution_slots), 0)

        strategy = ScheduledDateStrategy(planjobs=[planjob], configs=configuration_mock.get_configuration_default())
        strategy.allocate()

        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)
        finish_time_expected = planjob.scheduled_date + timedelta(minutes=planjob.time+planjob.setup)
        self.assertEqual(planjob.execution_slots[0].finish_time, finish_time_expected)

    def test_same_start_planjob_nonstop_infinity(self):
        configs = configuration_mock.get_configuration_default()
        configs_pj1 = configuration_mock.get_default_configs_planjob()
        configs_pj2 = configuration_mock.get_default_configs_planjob()
        configs_pj2.nonstop_infinity = True

        today = datetime.today()
        today_str = today.strftime(utils.DATE_FORMAT)

        ana = resources_mock.get_ana()
        ana.available_slots = resources_mock.um_mes_livre()
        pedro = resources_mock.get_pedro()
        pedro.available_slots = resources_mock.um_mes_livre()

        planjob = Planjob(1420, 1, [DesiredResource([ResourceCharacteristic(resources=[ana.id])])], configs_pj2)
        planjob.scheduled_date = datetime(2017, 5, 15, 11, 30)
        planjob.allocated_resources = [ana]

        planjob2 = Planjob(120, 2, [DesiredResource([ResourceCharacteristic(resources=[pedro.id])])], configs_pj1)
        planjob2.allocated_resources = [pedro]

        planjob.same_start.append(planjob2)
        planjob2.same_start.append(planjob)

        strategy = ScheduledDateStrategy(planjobs=[planjob, planjob2], configs=configs)
        strategy.allocate()

        self.assertEqual(len(planjob.allocated_resources), 1)
        self.assertEqual(planjob.allocated_resources[0].id, ana.id)

        self.assertEqual(len(planjob.execution_slots), 1)
        self.assertEqual(planjob.execution_slots[0].start_time, planjob.scheduled_date)

        self.assertEqual(len(planjob2.execution_slots), 1)
        self.assertEqual(planjob2.execution_slots[0].start_time, planjob.scheduled_date)

        next_day = planjob.scheduled_date + timedelta(days=1)
        self.assertEqual(planjob.execution_slots[0].finish_time.date(), next_day.date())

        sum = 0
        for slot in planjob.execution_slots:
            sum += ((slot.finish_time - slot.start_time).total_seconds() // 60)

        self.assertEqual(sum, planjob.time + planjob.setup*len(planjob.execution_slots))


    def test_planjob_deadline_non_working_days(self):
        schedule_date = datetime(2018, 8, 1)
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
        planjob.scheduled_date = schedule_date
        planjob.allocated_resources = [maria]

        self.assertEquals(len(planjob.execution_slots), 0)

        strategy = ScheduledDateStrategy(planjobs=[planjob],
                                         configs=global_configs,
                                         non_working_days=non_working_days)
        strategy.allocate()


        time_available_current = 0
        for date_str in maria.available_slots:
            for slot in maria.available_slots[date_str]:
                time_available_current += slot.minutes()

        self.assertEquals(len(planjob.allocated_resources), 1)
        self.assertTrue(maria in planjob.allocated_resources)
        self.assertEquals(len(planjob.execution_slots), 1)
        self.assertEquals(planjob.execution_slots[0].start_time.strftime(utils.DATE_FORMAT), "2018/08/01")
        self.assertEquals(planjob.execution_slots[0].finish_time.strftime(utils.DATE_FORMAT), "2018/08/08")
        self.assertEquals(time_available_previous, time_available_current)

if __name__ == '__main__':
    unittest.main()
