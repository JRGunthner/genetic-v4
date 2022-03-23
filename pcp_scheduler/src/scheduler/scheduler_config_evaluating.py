# coding: utf-8

def evaluate_slot(slot, planjob, configs, resource=None, date=None):
    slot_duration = (slot.finish_time - slot.start_time).total_seconds() / 60
    if slot_duration >= planjob.time+planjob.setup:
        return True
    if is_slot_upper_than_limits(slot_duration, planjob, configs):
        if planjob.configs.fractioned_between_planjobs:
            return True
        elif planjob.configs.fractioned_between_intervals:
            if slot.complement is None: return False
            return complementary_slots_enough(slot, planjob)
        elif planjob.configs.nonstop_infinity:
            return slot.complement is not None and slot.complement != []

    return False


def is_slot_upper_than_limits(slot_duration, planjob, configs):
    absolute_limit = planjob.configs.fractioned_floor_limit \
                        if planjob.configs.fractioned_floor_limit is not None else configs.fractioned_floor_limit
    percentual_limit = planjob.configs.fractioned_floor_limit_percentual \
                        if planjob.configs.fractioned_floor_limit_percentual is not None else configs.fractioned_floor_limit_percentual

    if slot_duration < planjob.time and slot_duration < absolute_limit:
        return False

    percentual = (float(slot_duration) / float(planjob.time)) * 100
    if percentual < percentual_limit:
        return False

    return True


def is_slot_nonstop_vigily_valid(slot, planjob, configs):
    slot_duration = (slot.finish_time - slot.start_time).total_seconds() // 60

    if slot_duration < configs.nonstop_vigily_floor_limit:
        return False

    percentual = (float(slot_duration) / float(planjob.time)) * 100
    if percentual < configs.nonstop_vigily_floor_limit_percentual:
        return False

    return True


def is_relay_slot_valid(slot, planjob, configs):
    slot_duration = slot.minutes()
    if slot_duration < configs.relay_slot_floor_limit:
        return False

    percentual = (float(slot_duration) / float(planjob.time)) * 100
    if percentual < configs.relay_slot_floor_limit_percentual:
        return False

    return True


def get_diff_to_be_valid(slot, planjob, configs):
    slot_duration = (slot.finish_time - slot.start_time).total_seconds() // 60

    if configs.nonstop_vigily_floor_limit != 0:
        return configs.nonstop_vigily_floor_limit - slot_duration

    if configs.nonstop_vigily_floor_limit_percentual:
        limit = (configs.nonstop_vigily_floor_limit_percentual*(planjob.time+planjob.setup)) // 100
        return limit - slot_duration

    return 0


def get_diff_to_be_valid_relay_slot(slot, planjob, configs):
    slot_duration = slot.minutes()
    if configs.nonstop_vigily_floor_limit != 0:
        return configs.nonstop_vigily_floor_limit - slot_duration

    if configs.nonstop_vigily_floor_limit_percentual:
        limit = (configs.nonstop_vigily_floor_limit_percentual*(planjob.time+planjob.setup)) // 100
        return limit - slot_duration

    return 0


def complementary_slots_enough(slot, planjob):
    sum = (slot.finish_time - slot.start_time).total_seconds() // 60
    for other_slot in slot.complement:
        duration = (other_slot.finish_time - other_slot.start_time).total_seconds() // 60
        sum += duration

    return sum >= planjob.time + (planjob.setup * len(slot.complement))