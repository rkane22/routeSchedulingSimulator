import numpy
import copy

DEFAULT = 0
CUMULATIVE = 1

def gen_random_aisle_graph(aisles=1, rows=5, cols=5, theta=2):
    # use Zipf distribution 
    new_graph = AisleGraph()
    new_graph.aisles = 2
    aisle = []
    for i in range(rows):
        row = []
        for j in range(cols):
            reward = numpy.random.zipf(theta)
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
        return self.aisle[j][i]

    def get_xy(self, x, y):
        return self.aisle[x-1][y-1]
    
    def rows(self):
        return len(self.aisle)

    def cols(self):
        return len(self.aisle[0])

    def reset(self):
        self.set_compare_mode(DEFAULT)

    def set(self, row, col, val):
        # sets the reward values of the node at location [row, col] to val.
        self.aisle[row][col].val = val

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
    
    def copy(self):
        return copy.deepcopy(self)

    def get_node_list(self):
        node_list = []
        # return a list of all nodes, order does not matter
        for row in self.aisle:
            node_list += row
        return node_list
    
    def calc_cumulative_val(self):
        for row in self.aisle:
            c = 0
            for v in row:
                c += v.val
                v.c_val = c
    
    def set_compare_mode(self, mode):
        if mode == CUMULATIVE:
            self.calc_cumulative_val()
        for row in self.aisle:
            for v in row:
                v.compare = mode

    
class Vertex():
    # a vertex on the graph containing a single value
    def __init__(self, val, pos_x, pos_y, c_val=None):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.val = val
        self.c_val = c_val
        self.compare = DEFAULT

    def __eq__(self, other):
        if self.compare == CUMULATIVE:
            return (self.c_val == other.c_val) and \
                (self.pos_x == other.pos_x) and \
                (self.pos_y == other.pos_y)
        else:
            return (self.val == other.val) and \
                (self.pos_x == other.pos_x) and \
                (self.pos_y == other.pos_y)
    
    def __ge__(self, other):
        if self.compare == CUMULATIVE:
            return self.c_val >= other
        else:
            return self.val >= other
        

    def __le__(self, other):
        if self.compare == CUMULATIVE:
            return self.c_val <= other
        else:
            return self.val <= other

    def __gt__(self, other):
        if self.compare == CUMULATIVE:
            return self.c_val > other
        else:
            return self.val > other
    
    def __lt__(self, other):
        if self.compare == CUMULATIVE:
            return self.c_val < other
        else:
            return self.val < other

    def __str__(self):
        return "val: {}, pos_x: {}, pos_y: {}".format(self.val, self.pos_x, self.pos_y)
    
    def __repr__(self):
        return "(val: {}, pos_x: {}, pos_y: {})".format(self.val, self.pos_x, self.pos_y)

    def __hash__(self):
        return hash(str(self))