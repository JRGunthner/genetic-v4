import sys


class Planjob:
    def __init__(self, time=0, id_=0, pj_name=(), desired_resources=[], configs=None, setup=0):
        self.id = id_
        self.pjName = pj_name
        self.time = time
        self.setup = setup
        self.desired_resources = desired_resources
        self.predecessors = []
        self.successors = []
        self.same_start = []
        self.same_finish = []
        self.configs = configs
        self.allocated_resources = None
        self.execution_slots = []
        self.finish_date = None
        self.start_date = None
        self.deepness = 0
        self.min_start_date = None
        self.early_start = 0
        self.early_end = 0
        self.late_start = 0
        self.late_end = 10000
        self.visited = False
        self.scheduled_date = None
        self.resources = []
        self.process_id = 0

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def clean_temp_atrr(self):
        self.resources = []
        if self.allocated_resources is not None:
            for resource in self.allocated_resources:
                resource.clean_temp_attrs()

    def clone(self, other):
        self.predecessors = other.predecessors
        self.successors = other.successors
        self.same_start = other.same_start
        self.same_finish = other.same_finish
        self.min_start_date = other.min_start_date
        self.scheduled_date = other.scheduled_date
        self.process_id = other.process_id
