import random

def gen_random_aisle_graph(aisles=1, rows=5, cols=5, rewards=None):
    new_graph = AisleGraph()
    new_graph.aisles = 2
    aisle = []
    for i in range(rows):
        row = []
        for j in range(cols):
            reward = random.choice(range(0, 10))
            row.append(Vertex(reward, i+1, j+1))
        aisle.append(row)
    new_graph.aisle = aisle
    return new_graph

class AisleGraph():
    def __init__(self):
        super().__init__()
        self.aisle = [] # [array of rows, each value in the rows is a vertex]
        self.aisles = 1

    def get(self, i, j):
        return self.aisle[i][j]

    def __str__(self):
        # display graph as text
        lines = ""
        for i in range(len(self.aisle)):
            for j in range(len(self.aisle[i])):
                lines += str(self.aisle[i][j].val)
                if j < len(self.aisle[i])-1:
                    lines+="-"
            lines += "\n"
            if(i < len(self.aisle)-1):
                lines += "|"
                lines += " " * (2*(len(self.aisle[i])-2))
                if self.aisles == 2:
                    lines += " |\n"
                else:
                    lines += "  \n"
        return lines
    
    def get_node_list(self):
        node_list = []
        # return a list of all nodes, order does not matter
        for row in self.aisle:
            node_list += row
        return node_list

    
class Vertex():
    # a vertex on the graph containing a single value
    def __init__(self, val, pos_x, pos_y):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.val = val

    def __eq__(self, other):
        return (self.val == other.val) and \
            (self.pos_x == other.pos_x) and \
            (self.pos_y == other.pos_y)
    
    def __ge__(self, other):
        return self.val >= other

    def __le__(self, other):
        return self.val <= other

    def __gt__(self, other):
        return self.val > other
    
    def __lt__(self, other):
        return self.val < other

    def __str__(self):
        return "val: {}, pos_x: {}, pos_y: {}".format(self.val, self.pos_x, self.pos_y)
    
    def __repr__(self):
        return "(val: {}, pos_x: {}, pos_y: {})".format(self.val, self.pos_x, self.pos_y)
