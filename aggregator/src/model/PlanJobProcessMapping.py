class PlanJobProcessMapping:
    def __init__(self):
        self.mapping_process_to_planjob = {}

    def map_planjobs(self, planjobs):
        for planjob in planjobs:
            for job_process in planjob.job_processes:
                self.mapping_process_to_planjob[job_process.uniqueId] = planjob

    def process_planjob_dependencies(self, processes):
        planjobs = map(lambda x: self.mapping_process_to_planjob[x], processes)
        return list(set(planjobs))
