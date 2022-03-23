#coding: utf-8

from pcp_scheduler.mock import tasks_mock, resources_mock, configuration_mock
from pcp_scheduler.src.scheduler import scheduler, scheduler_ag
from pcp_scheduler.src.model.Planjob import Planjob
from pcp_scheduler.src.model.Tree import Node
from pcp_scheduler.utils.utils import *


def main():
    grid = resources_mock.grid_todo_livre()
    tasks = tasks_mock.get_10_dependent_tasks()
    configs = configuration_mock.get_configuration_default()

    tasks2 = scheduler_ag.generate_allocation(grid, tasks, configs)

    for task in tasks2:
        resources = [id for id in task.allocated_resources_id]
        utc_date_start = task.execution_slots[0].start_time.strftime('%Y,%m,%d,%H,%M')
        utc_date_finish = task.execution_slots[0].finish_time.strftime('%Y,%m,%d,%H,%M')
        dependencies = ','.join([s for s in task.predecessors])
        dependencies = "'" + dependencies + "'" if dependencies != '' else 'null'
        print("['%s', '%s', \"%s\", new Date(%s), new Date(%s), minutesToMilliseconds(30), 100, %s]," % (task.id, task.id, resources, utc_date_start, utc_date_finish, dependencies))


if __name__ == '__main__':
    main()
