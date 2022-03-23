class ProcessLoadInformation:
    def __init__(self, process_id=None, planjobs_per_time={}):
        self.process_id = process_id
        self.planjobs_per_time = planjobs_per_time

    def register_load_info(self, planjob_id, time):
        self.planjobs_per_time[planjob_id] = time