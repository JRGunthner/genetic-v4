# coding: utf-8
from __future__ import print_function

from pcp_scheduler.mock import tasks_mock, resources_mock, configuration_mock
from pcp_scheduler.src.scheduler import scheduler_ag
from encoder.CustomEncoder import CustomEncoder
import json

# gerando json das alocações

def invoke2(grid, tasks, configs):
    tasks_2 = scheduler_ag.generate_allocation(grid, tasks, configs)

    for task in tasks_2:
        resources = [allocated_resource.id for allocated_resource in task.allocated_resources]
        utc_date_start = task.start_date.strftime('%Y,%m,%d,%H,%M')
        utc_date_finish = task.finish_date.strftime('%Y,%m,%d,%H,%M')
        dependencies = ','.join([s for s in task.predecessors])
        dependencies = "'" + dependencies + "'" if dependencies != '' else 'null'
        print("['%s', '%s', \"%s\", new Date(%s), new Date(%s), minutesToMilliseconds(30), 100, %s]," % (
            task.id, task.id, resources, utc_date_start, utc_date_finish, dependencies))


def main():
    grid_mock = resources_mock.grid_todo_livre()
    taskss_mock = tasks_mock.get_10_dependent_tasks()
    configs_mock = configuration_mock.get_configuration_default()

    tasks_dumps = json.dumps(taskss_mock, indent=4, cls=CustomEncoder)
    grid_dumps = json.dumps(grid_mock, indent=4, cls=CustomEncoder)
    configs_dumps = json.dumps(configs_mock, indent=4, cls=CustomEncoder)

    payload = {
        "planjobs": taskss_mock,
        "grid": grid_mock,
        "configs": configs_mock}

    p2 = json.dumps(payload, cls=CustomEncoder)
    print(p2)


if __name__ == '__main__':
    main()
