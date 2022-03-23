import unittest
from datetime import datetime, timedelta
from pcp_scheduler.mock import tasks_mock, resources_mock
from pcp_scheduler.src.scheduler import scheduler_ag
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.utils import test_utils


class TestScheduler(unittest.TestCase):

    def test_allocate_tasks_different_resources(self):
        grid = resources_mock.grid_todo_livre()
        tasks = tasks_mock.get_tasks_resources_granularity()

        tasks2 = scheduler_ag.generate_allocation(grid, tasks, {})

        for task in tasks2:
            self.assertTrue(task.start_date is not None)
            self.assertTrue(task.finish_date is not None)


if __name__ == '__main__':
    unittest.main()
