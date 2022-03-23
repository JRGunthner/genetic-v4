import unittest

from aggregator.src.LoopDetector import LoopDetector
from aggregator.src.LoopResolver import LoopResolver
from aggregator.src.model.JobProcess import JobProcess
from aggregator.src.model.PlanJob import PlanJob
from aggregator.src.model.PlanJobProcessMapping import PlanJobProcessMapping


class LoopResolverTest(unittest.TestCase):

    def test_complex_loop_1(self):
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

        detector = LoopDetector([planjob_1, planjob_2, planjob_3])
        self.assertTrue(detector.detect_loop())

        resolver = LoopResolver()
        resolver.loop = detector.loop
        resolver.planjobs = [planjob_1, planjob_2, planjob_3]
        resolver.resolve_loop()
        self.assertEqual(len(resolver.planjobs), 4)
        self.assertListEqual(resolver.planjobs[0].paths, [planjob_3])
        self.assertListEqual(resolver.planjobs[1].paths, [resolver.planjobs[3]])
        self.assertListEqual(resolver.planjobs[2].paths, [planjob_2])
        detector = LoopDetector(resolver.planjobs)
        self.assertFalse(detector.detect_loop())

    def test_complex_loop_2(self):
        job_a_1 = JobProcess()
        job_a_1.uniqueId = "job_a_1"
        job_a_1.successors = ["job_b_1"]
        job_b_1 = JobProcess()
        job_b_1.uniqueId = "job_b_1"
        job_b_1.successors = []

        job_a_2 = JobProcess()
        job_a_2.uniqueId = "job_a_2"
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

        detector = LoopDetector([planjob_1, planjob_2])
        self.assertTrue(detector.detect_loop())

        resolver = LoopResolver()
        resolver.loop = detector.loop
        resolver.planjobs = [planjob_1, planjob_2]
        resolver.resolve_loop()
        self.assertEqual(len(resolver.planjobs), 3)
        detector = LoopDetector(resolver.planjobs)
        self.assertFalse(detector.detect_loop())