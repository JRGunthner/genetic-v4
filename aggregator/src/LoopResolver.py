from aggregator.src.model.PlanJobProcessMapping import PlanJobProcessMapping


class LoopResolver:
    def __init__(self):
        self.loop = []
        self.planjobs = []
        self.dependencies_transformation = {}

    def resolve_loop(self):
        if len(self.loop) > 0:
            mapping = PlanJobProcessMapping()
            mapping.map_planjobs(self.planjobs)
            for loop_item in self.loop:
                result = loop_item.split_dependencies(self.loop, mapping)
                if len(result) > 1:
                    self.dependencies_transformation[loop_item.id] = result
                    break

            self.planjobs = [item for item in self.planjobs if item.id not in self.dependencies_transformation.keys()]

            for key, value in self.dependencies_transformation.items():
                self.planjobs = self.planjobs + value

            mapping = PlanJobProcessMapping()
            mapping.map_planjobs(self.planjobs)
            for planjob in self.planjobs:
                planjob.refresh_paths(mapping)

            return self.planjobs
