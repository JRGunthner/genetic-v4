import unittest

from pcp_scheduler.src.model.Resource import Resource
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Tree import build_graph, find_possible_allocations


class TestTree(unittest.TestCase):

    def test_build_graph(self):
        r1 = Resource("r1", "r1")
        r2 = Resource("r2", "r2")
        r4 = Resource("r3", "r3")
        r7 = Resource("r7", "r7")

        t1 = Planjob(30, 1, {})
        t1.resources = [r1]
        t2 = Planjob(30, 2, {})
        t2.resources = [r1, r2, r4]
        t3 = Planjob(30, 3, {})
        t3.resources = [r1, r4, r7]
        t4 = Planjob(30, 4, {})
        t4.resources = [r1, r2]

        roots = build_graph([t1,t2,t3,t4], 0)
        root = roots[0]
        self.assertEqual(len(roots), 1)
        self.assertEqual(root.data, r1)
        self.assertTrue(len(root.children) == len(t2.resources) or len(root.children) == len(t2.resources)-1)

        first_level = root.children
        self.assertTrue(len(first_level) <= len(t2.resources))

        for node in first_level:
            self.assertTrue(node.data in t2.resources)

        all_second_level = []
        for node in first_level:
            second_level = node.children
            for n in second_level:
                self.assertTrue(n.data in t3.resources)
                all_second_level.append(n)

        for node in all_second_level:
            for child_node in node.children:
                self.assertTrue(child_node.data in t4.resources)
                self.assertEqual(len(child_node.children), 0)

    def test_define_alloc(self):
        r1 = Resource("r1", "r1")
        r2 = Resource("r2", "r2")
        r3 = Resource("r3", "r3")
        r7 = Resource("r7", "r7")

        t1 = Planjob(30, 1, {})
        t1.resources = [r1]
        t2 = Planjob(30, 2, {})
        t2.resources = [r1, r2, r3]
        t3 = Planjob(30, 3, {})
        t3.resources = [r1, r3, r7]
        t4 = Planjob(30, 4, {})
        t4.resources = [r1, r2]

        roots = build_graph([t1, t2, t3, t4], 0)

        root = roots[0]
        solutions = []
        find_possible_allocations(root, [], solutions, 4)
        self.assertEqual(len(solutions), 1)

        perfect_solution = solutions[0]
        self.assertEqual(perfect_solution[0], r1)
        self.assertEqual(perfect_solution[1], r3)
        self.assertEqual(perfect_solution[2], r7)
        self.assertEqual(perfect_solution[3], r2)

