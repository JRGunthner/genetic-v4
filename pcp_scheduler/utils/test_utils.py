def get_last_predecessor_to_execute(predecessors):
    major = predecessors[0]
    for i in range(len(predecessors)):
        if predecessors[i].execution_slots[-1].finish_time > major.execution_slots[-1].finish_time:
            major = predecessors[i]
    return major


def get_requirement_by_id(requirements, id):
    for requirement in requirements:
        if requirement.planjob.id == id:
            return requirement
