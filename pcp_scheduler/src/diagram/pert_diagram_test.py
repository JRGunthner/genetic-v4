import unittest
from pcp_scheduler.mock import tasks_mock
from pcp_scheduler.src.diagram.PertDiagram import PertDiagram

class TestPertDiagram(unittest.TestCase):
    def test_constructor(self):
        dependent_tasks = tasks_mock.get_dependent_tasks()
        pert_diagram = PertDiagram(dependent_tasks)

        self.assertEqual(len(pert_diagram.tasks), len(dependent_tasks))
        self.assertEqual(len(pert_diagram.roots), 2)

    def test_get_leaves(self):
        dependent_tasks = tasks_mock.get_dependent_tasks()
        pert_diagram = PertDiagram(dependent_tasks)

        leaves = pert_diagram.get_leaves_tasks()
        self.assertEqual(len(leaves), 2)

    def test_build_diagram(self):
        dependent_tasks = tasks_mock.get_dependent_tasks()
        pert_diagram = PertDiagram(dependent_tasks)

        pert_diagram.build_pert_diagram()

        self.assertEqual(pert_diagram.tasks[0].early_start, 0)
        self.assertEqual(pert_diagram.tasks[0].early_end, 1)
        self.assertEqual(pert_diagram.tasks[0].late_start, 0)
        self.assertEqual(pert_diagram.tasks[0].late_end, 1)

        self.assertEqual(pert_diagram.tasks[1].early_start, 1)
        self.assertEqual(pert_diagram.tasks[1].early_end, 3)
        self.assertEqual(pert_diagram.tasks[1].late_start, 1)
        self.assertEqual(pert_diagram.tasks[1].late_end, 3)

        self.assertEqual(pert_diagram.tasks[2].early_start, 3)
        self.assertEqual(pert_diagram.tasks[2].early_end, 7)
        self.assertEqual(pert_diagram.tasks[2].late_start, 3)
        self.assertEqual(pert_diagram.tasks[2].late_end, 7)

        self.assertEqual(pert_diagram.tasks[3].early_start, 7)
        self.assertEqual(pert_diagram.tasks[3].early_end, 11)
        self.assertEqual(pert_diagram.tasks[3].late_start, 7)
        self.assertEqual(pert_diagram.tasks[3].late_end, 11)

        self.assertEqual(pert_diagram.tasks[4].early_start, 7)
        self.assertEqual(pert_diagram.tasks[4].early_end, 10)
        self.assertEqual(pert_diagram.tasks[4].late_start, 7)
        self.assertEqual(pert_diagram.tasks[4].late_end, 10)

        self.assertEqual(pert_diagram.tasks[5].early_start, 0)
        self.assertEqual(pert_diagram.tasks[5].early_end, 3)
        self.assertEqual(pert_diagram.tasks[5].late_start, 2)
        self.assertEqual(pert_diagram.tasks[5].late_end, 5)

        self.assertEqual(pert_diagram.tasks[6].early_start, 3)
        self.assertEqual(pert_diagram.tasks[6].early_end, 5)
        self.assertEqual(pert_diagram.tasks[6].late_start, 5)
        self.assertEqual(pert_diagram.tasks[6].late_end, 7)

    def test_build_diagram_2(self):
        dependent_tasks = tasks_mock.get_dependent_tasks_2()
        pert_diagram = PertDiagram(dependent_tasks)

        pert_diagram.build_pert_diagram()

        self.assertEqual(pert_diagram.tasks[0].early_start, 0)
        self.assertEqual(pert_diagram.tasks[0].early_end, 2)
        self.assertEqual(pert_diagram.tasks[0].late_start, 1)
        self.assertEqual(pert_diagram.tasks[0].late_end, 3)

        self.assertEqual(pert_diagram.tasks[1].early_start, 0)
        self.assertEqual(pert_diagram.tasks[1].early_end, 3)
        self.assertEqual(pert_diagram.tasks[1].late_start, 0)
        self.assertEqual(pert_diagram.tasks[1].late_end, 3)

        self.assertEqual(pert_diagram.tasks[2].early_start, 0)
        self.assertEqual(pert_diagram.tasks[2].early_end, 1)
        self.assertEqual(pert_diagram.tasks[2].late_start, 2)
        self.assertEqual(pert_diagram.tasks[2].late_end, 3)

        self.assertEqual(pert_diagram.tasks[3].early_start, 2)
        self.assertEqual(pert_diagram.tasks[3].early_end, 6)
        self.assertEqual(pert_diagram.tasks[3].late_start, 4)
        self.assertEqual(pert_diagram.tasks[3].late_end, 8)

        self.assertEqual(pert_diagram.tasks[4].early_start, 2)
        self.assertEqual(pert_diagram.tasks[4].early_end, 5)
        self.assertEqual(pert_diagram.tasks[4].late_start, 4)
        self.assertEqual(pert_diagram.tasks[4].late_end, 7)

        self.assertEqual(pert_diagram.tasks[5].early_start, 3)
        self.assertEqual(pert_diagram.tasks[5].early_end, 4)
        self.assertEqual(pert_diagram.tasks[5].late_start, 3)
        self.assertEqual(pert_diagram.tasks[5].late_end, 4)

        self.assertEqual(pert_diagram.tasks[6].early_start, 1)
        self.assertEqual(pert_diagram.tasks[6].early_end, 6)
        self.assertEqual(pert_diagram.tasks[6].late_start, 4)
        self.assertEqual(pert_diagram.tasks[6].late_end, 9)

        self.assertEqual(pert_diagram.tasks[7].early_start, 4)
        self.assertEqual(pert_diagram.tasks[7].early_end, 7)
        self.assertEqual(pert_diagram.tasks[7].late_start, 4)
        self.assertEqual(pert_diagram.tasks[7].late_end, 7)

        self.assertEqual(pert_diagram.tasks[8].early_start, 6)
        self.assertEqual(pert_diagram.tasks[8].early_end, 8)
        self.assertEqual(pert_diagram.tasks[8].late_start, 8)
        self.assertEqual(pert_diagram.tasks[8].late_end, 10)

        self.assertEqual(pert_diagram.tasks[9].early_start, 7)
        self.assertEqual(pert_diagram.tasks[9].early_end, 10)
        self.assertEqual(pert_diagram.tasks[9].late_start, 7)
        self.assertEqual(pert_diagram.tasks[9].late_end, 10)

        self.assertEqual(pert_diagram.tasks[10].early_start, 6)
        self.assertEqual(pert_diagram.tasks[10].early_end, 7)
        self.assertEqual(pert_diagram.tasks[10].late_start, 9)
        self.assertEqual(pert_diagram.tasks[10].late_end, 10)

        self.assertEqual(pert_diagram.tasks[11].early_start, 10)
        self.assertEqual(pert_diagram.tasks[11].early_end, 10)
        self.assertEqual(pert_diagram.tasks[11].late_start, 10)
        self.assertEqual(pert_diagram.tasks[11].late_end, 10)

if __name__ == '__main__':
    unittest.main()
