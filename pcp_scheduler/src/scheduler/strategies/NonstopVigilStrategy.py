# coding: utf-8

from datetime import datetime, timedelta

from pcp_scheduler.src.model.Slot import Slot
from pcp_scheduler.src.scheduler import scheduler_utils, scheduler_config_evaluating
from pcp_scheduler.src.exceptions.Exceptions import InsufficientResourceCalendarException
from pcp_scheduler.utils import utils


class NonstopVigilyStrategy:
    def __init__(self, planjob, solutions, configs, predecessors=[]):
        self.planjob = planjob
        self.solutions = solutions
        self.configs = configs
        self.predecessors = predecessors
        self.start_times = self.get_start_times()

    def allocate(self):
        self.allocate_simple_planjob()

    def allocate_simple_planjob(self):
        intersections = None
        for start_time in sorted(self.start_times):
            finish_time = start_time + timedelta(minutes=self.planjob.time + self.planjob.setup)
            intersections = self.find_intersection(start_time, finish_time)
            if intersections is not None:
                break

        if intersections is None:
            resources = set([resource.id for solution in self.solutions for resource in solution])
            values = {'planjobs': [self.planjob.id],
                      'resources': list(resources)}
            raise InsufficientResourceCalendarException(values)

        used_resources = set([])
        slot = Slot(start_time, start_time, finish_time)
        slot.vigils = {}

        for intersection in intersections:
            used_resources.update(set(intersection.values()))
            for (key, resource) in intersection.items():
                slot.vigils[resource.id] = slot.vigils.get(resource.id, [])
                slot.vigils[resource.id].append(key)

        self.planjob.execution_slots = [slot]
        self.planjob.allocated_resources = scheduler_utils.get_resources_copy(used_resources)

    def find_intersection(self, start_time, finish_time):
        desired_resources = self.build_desired_resources()
        positions = [i for i in range(len(desired_resources))]
        permutations = utils.get_all_permutations(positions)
        for perm in permutations:
            vigily_per_desired_resource = []
            found = True
            for position in perm:
                desired_resource = desired_resources[position]
                vigily = self.build_vigily(desired_resource, vigily_per_desired_resource, start_time, finish_time)
                if vigily is None:
                    found = False
                    break
                vigily_per_desired_resource.append(vigily)

            if found:
                return vigily_per_desired_resource

    def build_vigily(self, desired_resource, vigils, start_time, finish_time):
        start = start_time
        vigily = {}

        not_found = False
        while True:
            if start == finish_time: break

            couple = self.find_major_slot_from(desired_resource, start, finish_time, vigils)
            if couple is None or not self.couple_is_allowed(couple, finish_time):
                not_found = True
                break
            else:
                vigily[couple[0]] = couple[1]
                start = couple[0].finish_time

        if not_found: return None

        return vigily

    def find_major_slot_from(self, desired_resource, start_time, finish_time, vigils):
        major_slot = None
        owner = None
        date_str = start_time.strftime(utils.DATE_FORMAT)
        for resource in desired_resource:
            if date_str in resource.available_slots:
                for slot in resource.available_slots[date_str]:
                    if slot.start_time <= start_time <= slot.finish_time:
                        correct_finish_time = self.get_correct_finish_time(vigils, resource, start_time,
                                                                           finish_time, slot.finish_time)
                        if correct_finish_time is not None:
                            duration = (correct_finish_time - start_time).total_seconds() // 60
                            if duration > 0 and(major_slot is None or duration > major_slot.minutes()):
                                major_slot = Slot(start_time, start_time, correct_finish_time)
                                owner = resource

        return None if major_slot is None else (major_slot, owner)

    def couple_is_allowed(self, couple, finish_time):
        rest = Slot(couple[0].finish_time, couple[0].finish_time, finish_time)
        if scheduler_config_evaluating.is_slot_nonstop_vigily_valid(couple[0], self.planjob, self.configs):
            if scheduler_config_evaluating.is_slot_nonstop_vigily_valid(rest, self.planjob, self.configs) or \
                    rest.start_time == rest.finish_time:
                return True
            else:
                diff = scheduler_config_evaluating.get_diff_to_be_valid(rest, self.planjob, self.configs)
                new_slot = couple[0].light_copy()
                new_slot.finish_time = new_slot.finish_time - timedelta(minutes=diff)
                if scheduler_config_evaluating.is_slot_nonstop_vigily_valid(new_slot, self.planjob, self.configs):
                    couple[0].finish_time = new_slot.finish_time
                    return True
        return False

    def build_desired_resources(self):
        desired_resources = []
        for solution in self.solutions:
            for j in range(len(solution)):
                if len(desired_resources) < j + 1:
                    desired_resources.insert(j, set([]))
                desired_resources[j].add(solution[j])

        return desired_resources

    def get_correct_finish_time(self, vigils, resource, start_time, finish_time_desired, finish_time_found):
        finish_time = min(finish_time_desired, finish_time_found)
        for vigily in vigils:
            for (key, value) in vigily.items():
                if value.id == resource.id:
                    max_start = max(start_time, key.start_time)
                    min_finish = min(finish_time, key.finish_time)

                    if max_start < min_finish:
                        if key.start_time <= start_time: return None
                        else:
                            return max_start

        return finish_time

    def get_start_times(self):
        if self.planjob.scheduled_date is not None: return [self.planjob.scheduled_date]

        start_times = set([])
        time_limit = scheduler_utils.get_max_finish_time_predecessor(self.planjob, self.predecessors)
        date_limit_str = time_limit.strftime(utils.DATE_FORMAT) if time_limit is not None \
            else None

        for solution in self.solutions:
            for resource in solution:
                min_date = self.get_min_start_time_valid(resource, time_limit, date_limit_str)
                if min_date is not None: start_times.add(min_date)

        return list(start_times)

    def get_min_start_time_valid(self, resource, time_limit, date_limit_str):
        for date_str in sorted(resource.available_slots.keys()):
            if date_limit_str is None or (date_limit_str is not None and date_str >= date_limit_str):
                for slot in sorted(resource.available_slots[date_str]):
                    if slot.finish_time <= time_limit:
                        continue

                    tmp = slot.light_copy()
                    tmp.start_time = time_limit if slot.start_time <= time_limit < slot.finish_time else slot.start_time
                    if scheduler_config_evaluating.is_slot_nonstop_vigily_valid(tmp, self.planjob, self.configs):
                        return tmp.start_time
