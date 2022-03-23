class LoopDetector:
    def __init__(self, plan_jobs):
        self.plan_jobs = plan_jobs
        self.loop = []
        self.has_loop = False

    def detect_loop(self):
        for plan_job in self.plan_jobs:
            loop = plan_job.find_loop([])
            if len(loop) > 0 and (len(loop) < len(self.loop) or len(self.loop) == 0):
                self.loop = loop
                self.has_loop = True
        return self.has_loop
