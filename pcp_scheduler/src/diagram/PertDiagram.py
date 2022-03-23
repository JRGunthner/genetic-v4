class PertDiagram:
    def __init__(self, tasks):
        self.tasks = tasks if tasks is not None else []
        self.roots = [task for task in self.tasks if len(task.predecessors) == 0]

    def add_task_root(self, task):
        self.roots.append(task)

    def add_dependent_task(self, parent, task):
        self.tasks.append(task)
        node_parent = self.get_task(parent)
        node_parent.successors.append(task)
        task.predecessors.append(node_parent)

    def build_pert_diagram(self):
        leaves = self.get_leaves_tasks()

        self.__define_early_time(self.roots)
        self.__define_late_time(leaves)

        return self.tasks

    def __define_early_time(self, roots):
        for root in roots:
            root.early_start = 0
            root.early_end = root.early_start + root.time
            for successor in root.successors:
                self.__define_early_time_child(successor, root)

    def __define_early_time_child(self, task, parent):
        task.early_start = parent.early_end if parent.early_end > task.early_start else task.early_start
        task.early_end = task.early_start + task.time

        if len(task.successors) == 0:
            return

        for successor in task.successors:
            self.__define_early_time_child(successor, task)

    def __define_late_time(self, leaves):
        # Define as datas de inicio mais tarde e fim mais tarde das tarefas
        for leave in leaves:
            leave.late_end = leave.early_end
            leave.late_start = leave.late_end - leave.time
            for predecessor in leave.predecessors:
                self.__define_late_time_child(predecessor, leave)

    def __define_late_time_child(self, task, child):
        task.late_end = child.late_start if child.late_start < task.late_end else task.late_end
        task.late_start = task.late_end - task.time

        if len(task.predecessors) == 0 or task.late_end < child.late_start:
            return

        for predecessor in task.predecessors:
            self.__define_late_time_child(predecessor, task)

    def get_task(self, task_to_search):
        for task in self.tasks:
            if task.id == task_to_search.id:
                return task

    def get_leaves_tasks(self):
        leaves = [task for task in self.tasks if len(task.successors) == 0]
        return leaves
