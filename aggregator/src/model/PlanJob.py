import random
import string


class PlanJob:
    def __init__(self):
        self.id = ""
        self.job_processes = []
        self.paths = []
        self.predecessors = []
        self.successors = []
        self.same_start = []
        self.same_finish = []

    def find_loop(self, predecessors):
        for predecessor in predecessors:
            if predecessor.id == self.id:
                return predecessors
        predecessors.append(self)
        for node in self.paths:
            result = node.find_loop(predecessors)
            if len(list(filter(lambda x: x.id == node.id, result))) == 1:
                return result
        predecessors.remove(self)
        return predecessors

    def split_dependencies(self, loop, process_mapping):
        plan_jobs_created = {}
        for job_process in self.job_processes:
            process_dependencies = job_process.get_dependencies()
            plan_job_dependencies = process_mapping.process_planjob_dependencies(process_dependencies)
            plan_job_dependencies = list(filter(lambda x: x in loop, plan_job_dependencies))
            if len(plan_job_dependencies) == 0:
                if "empty" in plan_jobs_created.keys():
                    plan_jobs_created["empty"].job_processes.append(job_process)
                else:
                    new_planjob = self.create_planjob_from_process(job_process)
                    plan_jobs_created["empty"] = new_planjob
            elif len(plan_job_dependencies) == 1:
                if plan_job_dependencies[0].id in plan_jobs_created.keys():
                    plan_jobs_created[plan_job_dependencies[0].id].job_processes.append(job_process)
                else:
                    new_planjob = self.create_planjob_from_process(job_process)
                    plan_jobs_created[plan_job_dependencies[0].id] = new_planjob
        return [v for k, v in plan_jobs_created.items()]

    def create_planjob_from_process(self, job_process):
        new_planjob = PlanJob()
        new_planjob.id = self.id + ''.join(random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=20))
        new_planjob.job_processes.append(job_process)
        return new_planjob

    def refresh_paths(self, process_mapping):
        paths = []
        for job_process in self.job_processes:
            process_dependencies = job_process.get_dependencies()
            plan_job_dependencies = process_mapping.process_planjob_dependencies(process_dependencies)
            paths = list(set(paths + plan_job_dependencies))

        self.paths = paths
