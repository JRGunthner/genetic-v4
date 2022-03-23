from pcp_scheduler.src.model.Configuration import Configuration


def get_configuration_default():
    configs = Configuration()
    configs.groups_as_subset = False
    configs.max_priority_allowed = 0
    configs.prob_to_choose_between_resource = {"priority": 1, "cost": 0, "availability": 0, "random": 0}
    configs.allocator_params = {"elitism": 3, "gens_num": 1000, "early_stop": 10, "pop_size": 20}
    configs.fractioned_between_planjobs = False
    configs.same_day = False
    configs.fractioned_floor_limit = 0
    configs.fractioned_floor_limit_percentual = 0
    configs.nonstop_vigily_floor_limit_percentual = 0
    configs.nonstop_vigily_floor_limit = 0
    configs.must_respect_load_limit = False
    configs.fractioned_between_intervals = False
    configs.deadline_hour = 10
    configs.relay_slot_floor_limit = 0
    configs.relay_slot_floor_limit_percentual = 0
    configs.same_start_finish_dates_range = 10
    return configs


def get_default_configs_planjob():
    configs = Configuration()
    configs.fractioned_between_planjobs = False
    configs.same_day = False
    configs.fractioned_floor_limit = None
    configs.fractioned_floor_limit_percentual = None
    configs.fractioned_between_intervals = False
    configs.nonstop_infinity = False
    configs.nonstop_vigily_mode = False
    configs.is_deadline = False
    configs.relay = False
    configs.not_in_same_day_predecessor = False
    configs.only_working_days = False
    return configs
