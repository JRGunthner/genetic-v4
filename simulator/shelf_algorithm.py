class Shelf:
    max_width = -1
    itens = []
    disposing = {}
    inter_reel_space = 0

    def __init__(self, width, itens, inter_reel_space, max_parallel_items):
        self.max_width = width
        self.itens = itens
        self.inter_reel_space = inter_reel_space
        self.max_parallel_items = max_parallel_items


    def alocate(self):
        sorted_items = sorted(self.itens, key=lambda item: (item[1], item[0]), reverse=False)
        still_width = self.max_width
        maxY = 0
        nextY = 0
        nextX = 0
        self.disposing = {}
        self.disposing[nextY] = []
        parallel_items = 0
        while self.itens:
            size = len(sorted_items) -1
            for id in range(size, -1, -1):
                if sorted_items[id][0] <= still_width and parallel_items < self.max_parallel_items:
                    self.disposing[nextY].append((nextX,nextY, sorted_items[id][0], sorted_items[id][1], sorted_items[id][2]))
                    nextX += sorted_items[id][0] + self.inter_reel_space
                    still_width -= sorted_items[id][0] + self.inter_reel_space
                    if maxY < nextY + sorted_items[id][1]:
                        maxY = nextY + sorted_items[id][1]
                    self.itens.remove(sorted_items[id])
                    del sorted_items[id]
                    parallel_items += 1
                else:
                    self.itens.remove(sorted_items[id])

            nextY = maxY
            still_width = self.max_width
            self.disposing[nextY] = []
            parallel_items = 0
            nextX = 0
        return self.disposing
