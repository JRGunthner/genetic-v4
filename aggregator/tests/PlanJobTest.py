import unittest

from aggregator.src.model.JobProcess import JobProcess
from aggregator.src.model.PlanJob import PlanJob
from aggregator.src.model.PlanJobProcessMapping import PlanJobProcessMapping


class PlanJobTest(unittest.TestCase):

    def test_refresh_paths_1(self):
        job_a_1 = JobProcess()
        job_a_1.uniqueId = "job_a_1"
        job_a_1.successors = ["job_b_1"]
        job_b_1 = JobProcess()
        job_b_1.uniqueId = "job_b_1"
        job_b_1.successors = ["job_c_1"]
        job_c_1 = JobProcess()
        job_c_1.uniqueId = "job_c_1"

        job_a_2 = JobProcess()
        job_a_2.uniqueId = "job_a_2"
        job_b_2 = JobProcess()
        job_b_2.uniqueId = "job_b_2"
        job_b_2.successors = ["job_c_2"]
        job_c_2 = JobProcess()
        job_c_2.uniqueId = "job_c_2"
        job_c_2.successors = ["job_a_2"]

        planjob_1 = PlanJob()
        planjob_1.id = "pj1"
        planjob_1.job_processes = [job_a_1, job_a_2]
        planjob_2 = PlanJob()
        planjob_2.id = "pj2"
        planjob_2.job_processes = [job_b_1, job_b_2]
        planjob_3 = PlanJob()
        planjob_3.id = "pj3"
        planjob_3.job_processes = [job_c_1, job_c_2]

        planjobs = [planjob_1, planjob_2, planjob_3]
        mapping = PlanJobProcessMapping()
        mapping.map_planjobs(planjobs)
        planjob_1.refresh_paths(mapping)
        planjob_2.refresh_paths(mapping)
        planjob_3.refresh_paths(mapping)
        self.assertListEqual(planjob_1.paths, [planjob_2])
        self.assertListEqual(planjob_2.paths, [planjob_3])
        self.assertListEqual(planjob_3.paths, [planjob_1])

    def test_refresh_path_2(self):
        job_a_1 = JobProcess()
        job_a_1.uniqueId = "job_a_1"
        job_a_1.successors = ["job_b_1"]
        job_b_1 = JobProcess()
        job_b_1.uniqueId = "job_b_1"
        job_b_1.successors = []

        job_a_2 = JobProcess()
        job_a_2.uniqueId = "job_a_2"
        job_a_1.successors = ["job_b_2"]
        job_b_2 = JobProcess()
        job_b_2.uniqueId = "job_b_2"
        job_b_2.successors = []

        planjob_1 = PlanJob()
        planjob_1.id = "pj1"
        planjob_1.job_processes = [job_a_1, job_a_2]
        planjob_2 = PlanJob()
        planjob_2.id = "pj2"
        planjob_2.job_processes = [job_b_1, job_b_2]

        planjobs = [planjob_1, planjob_2]
        mapping = PlanJobProcessMapping()
        mapping.map_planjobs(planjobs)
        planjob_1.refresh_paths(mapping)
        planjob_2.refresh_paths(mapping)
        self.assertListEqual(planjob_1.paths, [planjob_2])
        self.assertListEqual(planjob_2.paths, [])

    def test_split_dependencies_1(self):
        job_a_1 = JobProcess()
        job_a_1.uniqueId = "job_a_1"
        job_a_1.successors = ["job_b_1"]
        job_b_1 = JobProcess()
        job_b_1.uniqueId = "job_b_1"
        job_b_1.successors = []

        job_a_2 = JobProcess()
        job_a_2.uniqueId = "job_a_2"
        job_a_2.successors = []
        job_b_2 = JobProcess()
        job_b_2.uniqueId = "job_b_2"
        job_b_2.successors = ["job_a_2"]

        planjob_1 = PlanJob()
        planjob_1.id = "pj1"
        planjob_1.job_processes = [job_a_1, job_a_2]
        planjob_2 = PlanJob()
        planjob_2.id = "pj2"
        planjob_2.job_processes = [job_b_1, job_b_2]

        planjobs = [planjob_1, planjob_2]
        mapping = PlanJobProcessMapping()
        mapping.map_planjobs(planjobs)
        planjob_1.refresh_paths(mapping)
        planjob_2.refresh_paths(mapping)
        result = planjob_1.split_dependencies([planjob_1, planjob_2], mapping)
        self.assertEqual(len(result), 2)
        self.assertListEqual(result[0].job_processes, [job_a_1])
        self.assertListEqual(result[1].job_processes, [job_a_2])
