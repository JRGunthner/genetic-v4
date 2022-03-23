class JobProcess:
    def __init__(self):
        self.uniqueId = ""
        self.processId = ""
        self.processMECId = ""
        self.predecessors = []
        self.successors = []
        self.same_start = []
        self.same_finish = []

    def get_dependencies(self):
        job_successors = self.successors
        job_same_start = self.same_start
        job_same_finish = self.same_finish
        job_dependencies = job_successors + job_same_start + job_same_finish
        return list(set(job_dependencies))
