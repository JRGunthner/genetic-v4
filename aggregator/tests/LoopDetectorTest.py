import unittest

from aggregator.src.LoopDetector import LoopDetector
from aggregator.src.model.PlanJob import PlanJob


class LoopDetectorTest(unittest.TestCase):

        def test_simple_loop_1(self):
            pj1 = PlanJob()
            pj2 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"

            pj1.paths = [pj2]
            pj2.paths = [pj1]
            loop_detector = LoopDetector([pj1, pj2])
            self.assertTrue(loop_detector.detect_loop())
            self.assertEqual([pj1, pj2], loop_detector.loop)

        def test_simple_loop_2(self):
            pj1 = PlanJob()
            pj2 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"

            pj1.paths = [pj2]
            pj2.paths = [pj2]
            loop_detector = LoopDetector([pj1, pj2])
            self.assertTrue(loop_detector.detect_loop())
            self.assertEqual([pj2], loop_detector.loop)

        def test_simple_loop_3(self):
            pj1 = PlanJob()
            pj2 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"

            pj1.paths = [pj1]
            pj2.paths = []
            loop_detector = LoopDetector([pj1, pj2])
            self.assertTrue(loop_detector.detect_loop())
            self.assertEqual([pj1], loop_detector.loop)

        def test_complex_loop_1(self):
            pj1 = PlanJob()
            pj2 = PlanJob()
            pj3 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"
            pj3.id = "pj3"

            pj1.paths = [pj2]
            pj2.paths = [pj3]
            pj3.paths = [pj1]

            loop_detector = LoopDetector([pj1, pj2, pj3])
            self.assertTrue(loop_detector.detect_loop())
            self.assertEqual([pj1, pj2, pj3], loop_detector.loop)

        def test_complex_loop_2(self):
            pj1 = PlanJob()
            pj2 = PlanJob()
            pj3 = PlanJob()
            pj4 = PlanJob()
            pj5 = PlanJob()
            pj6 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"
            pj3.id = "pj3"
            pj4.id = "pj4"
            pj5.id = "pj5"
            pj6.id = "pj6"

            pj1.paths = [pj5]
            pj2.paths = [pj1]
            pj3.paths = []
            pj4.paths = [pj6]
            pj5.paths = [pj4, pj2]
            pj6.paths = []

            loop_detector = LoopDetector([pj1, pj2, pj3, pj4, pj5, pj6])
            self.assertTrue(loop_detector.detect_loop())
            self.assertEqual([pj1, pj5, pj2], loop_detector.loop)

        def test_no_loop_1(self):
            pj1 = PlanJob()
            pj2 = PlanJob()
            pj3 = PlanJob()
            pj4 = PlanJob()
            pj5 = PlanJob()
            pj6 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"
            pj3.id = "pj3"
            pj4.id = "pj4"
            pj5.id = "pj5"
            pj6.id = "pj6"

            pj1.paths = [pj5]
            pj2.paths = [pj1]
            pj3.paths = []
            pj4.paths = [pj6]
            pj5.paths = [pj4]
            pj6.paths = []

            loop_detector = LoopDetector([pj1, pj2, pj3, pj4, pj5, pj6])
            self.assertFalse(loop_detector.detect_loop())
            self.assertEqual([], loop_detector.loop)

        def test_no_loop_2(self):
            pj1 = PlanJob()
            pj2 = PlanJob()
            pj3 = PlanJob()
            pj4 = PlanJob()
            pj5 = PlanJob()
            pj6 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"
            pj3.id = "pj3"
            pj4.id = "pj4"
            pj5.id = "pj5"
            pj6.id = "pj6"

            pj1.paths = [pj5]
            pj2.paths = []
            pj3.paths = []
            pj4.paths = [pj6]
            pj5.paths = [pj4, pj2]
            pj6.paths = []

            loop_detector = LoopDetector([pj1, pj2, pj3, pj4, pj5, pj6])
            self.assertFalse(loop_detector.detect_loop())
            self.assertEqual([], loop_detector.loop)

        def test_no_loop_3(self):
            loop_detector = LoopDetector([])
            self.assertFalse(loop_detector.detect_loop())
            self.assertEqual([], loop_detector.loop)

        def test_no_loop_4(self):
            pj1 = PlanJob()
            pj1.id = "pj1"
            loop_detector = LoopDetector([pj1])
            self.assertFalse(loop_detector.detect_loop())
            self.assertEqual([], loop_detector.loop)

        def test_disjoint_graph_1(self):
            pj1 = PlanJob()
            pj2 = PlanJob()
            pj3 = PlanJob()
            pj4 = PlanJob()
            pj5 = PlanJob()
            pj6 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"
            pj3.id = "pj3"
            pj4.id = "pj4"
            pj5.id = "pj5"
            pj6.id = "pj6"

            pj1.paths = [pj2]
            pj2.paths = []
            pj3.paths = [pj4]
            pj4.paths = []
            pj5.paths = [pj6]
            pj6.paths = []

            loop_detector = LoopDetector([pj1, pj2, pj3, pj4, pj5, pj6])
            self.assertFalse(loop_detector.detect_loop())
            self.assertEqual([], loop_detector.loop)


        def test_disjoint_graph_2(self):
            pj1 = PlanJob()
            pj2 = PlanJob()
            pj3 = PlanJob()
            pj4 = PlanJob()
            pj5 = PlanJob()
            pj6 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"
            pj3.id = "pj3"
            pj4.id = "pj4"
            pj5.id = "pj5"
            pj6.id = "pj6"

            pj1.paths = [pj2]
            pj2.paths = []
            pj3.paths = [pj4]
            pj4.paths = [pj5]
            pj5.paths = [pj3]
            pj6.paths = []

            loop_detector = LoopDetector([pj1, pj2, pj3, pj4, pj5, pj6])
            self.assertTrue(loop_detector.detect_loop())
            self.assertEqual([pj3, pj4, pj5], loop_detector.loop)

        def test_disjoint_graph_3(self):
            pj1 = PlanJob()
            pj2 = PlanJob()
            pj3 = PlanJob()
            pj4 = PlanJob()
            pj5 = PlanJob()
            pj6 = PlanJob()

            pj1.id = "pj1"
            pj2.id = "pj2"
            pj3.id = "pj3"
            pj4.id = "pj4"
            pj5.id = "pj5"
            pj6.id = "pj6"

            pj1.paths = [pj2]
            pj2.paths = []
            pj3.paths = [pj4]
            pj4.paths = [pj5]
            pj5.paths = [pj3]
            pj6.paths = [pj6]

            loop_detector = LoopDetector([pj1, pj2, pj3, pj4, pj5, pj6])
            self.assertTrue(loop_detector.detect_loop())
            self.assertEqual([pj6], loop_detector.loop)