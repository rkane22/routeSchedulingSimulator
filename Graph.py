import numpy
import copy

DEFAULT = 0
CUMULATIVE = 1

def gen_random_aisle_graph(aisles=1, rows=5, cols=5, theta=2):
    # use Zipf distribution 
    new_graph = AisleGraph()
    aisle = []
    for row in range(rows):
        r = []
        for col in range(cols):
            reward = 0 if col == 0 else numpy.random.zipf(theta)
            r.append(Vertex(reward, row+1, col+1))
        aisle.append(r)
    new_graph.aisle = aisle
    return new_graph

class AisleGraph():
    def __init__(self):
        super().__init__()
        self.aisle = [] # [array of rows, each value in the rows is a vertex]

    def get(self, row, col):
        return self.aisle[row-1][col-1]

    def get_xy(self, x, y):
        return self.aisle[y-1][x-1]
    
    def rows(self):
        return len(self.aisle)

    def cols(self):
        return len(self.aisle[0])-1

    def reset(self):
        self.set_compare_mode(DEFAULT)

    def __str__(self):
        # display graph as text
        lines = ""
        for i in range(len(self.aisle)):
            for j in range(len(self.aisle[i])):
                lines += str(self.aisle[i][j].get_val())
                if j < len(self.aisle[i])-1:
                    lines+="-"
            lines += "\n"
            if(i < len(self.aisle)-1):
                lines += "|"
                lines += "\n"
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
        for row in range(len(self.aisle)):
            c = 0
            for col in range(len(self.aisle[row])):
                v = self.get(row+1, col+1)
                c += v.val
                # print(v.pos_x, v.pos_y, v.val, c)
                self.aisle[row][col].c_val = c
    
    def set_compare_mode(self, mode):
        if mode == CUMULATIVE:
            self.calc_cumulative_val()
        for row in self.aisle:
            for v in row:
                v.compare = mode

class Vertex():
    # a vertex on the graph containing a single value
    def __init__(self, val, row, col, c_val=None):
        super().__init__()
        self.row = row
        self.col = col
        self.val = val
        self.c_val = c_val
        self.compare = DEFAULT

    def __eq__(self, other):
        if (self.row == other.row) and (self.col == other.col):
            if self.compare == CUMULATIVE:
                return (self.c_val == other.c_val)
            else:
                return (self.val == other.val)
        else: 
            return False
                
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
    
    def get_val(self):
        if self.compare == CUMULATIVE:
            return self.c_val
        else:
            return self.val

    def __str__(self):
        return "val: {}, row: {}, col: {}".format(self.get_val(), self.row, self.col)
    
    def __repr__(self):
        return "(val: {}, row: {}, col: {})".format(self.get_val(), self.row, self.col)

    def __hash__(self):
        return hash('{} {} {}'.format(self.row, self.col, self.val))