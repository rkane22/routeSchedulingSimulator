
# imports
from helpers import compute_sum, calc_path

import copy

class Solution():
    """A class that tracks a solution and provides methods and attributes unique for solutions"""
    def __init__(self, graph):
        self.p_cost = 0
        self.graph = graph
        self.nodes = set() # the set of nodes in the solution
        self.waits = [] # an integer representing the time step to wait on
        self.last_node = None
        self.done = False # for parallel algorithm

    def path_schedule(self):
        # similar to cost, find the unique path to
        #   visit all nodes in the inputted set
        nodes = self.nodes
        waits = self.waits.copy()
        max_nodes = [0 for i in range(self.graph.rows())]
        for node in nodes:
            if node.col > max_nodes[node.row-1]:
                max_nodes[node.row-1] = node.col
        # create path
        current_node = self.graph.get(1,1)
        path = [current_node]
        row = 1
        for col in max_nodes:
            if col > 1:
                target = self.graph.get(row, col)
                path = calc_path(self.graph, target, current_node, path)
                current_node = target
            row += 1
        # set last node to the furthest visited node
        self.last_node = current_node
        # at the end return to v[1,1]
        end = self.graph.get(1,1)
        path = calc_path(self.graph, end, current_node, path)
        self.p_cost = len(path)
        # assign each step in the path an incrementing timeslot (starting at 0)
        # when a wait is reached, the next timeslot is also at that position
        timed_path = []
        time = 0
        for step in path:
            timed_path.append(step)
            self.nodes.add(step)
            while len(waits) > 0 and step == waits[0]:
                waits.pop(0)
                # repeat
                timed_path.append(step)
                time+=1
             # fill in the nodes along the way
            time += 1
            
        return timed_path

    def check_conflicts(self, conflicts):
        a2_path = self.path_schedule()
        for conflict in conflicts:
            a1_path = conflict.path_schedule()
            # initialize previous step (no conflict on start)
            a1_prev = a1_path[0]
            a2_prev = a2_path[0]
            for step in range(len(a2_path)):
                # three cases:
                # a1_path is over and a2_path cannot have anymore conflicts
                if step >= len(a1_path):
                    break
                #  they land on the same node on a step
                if a1_path[step] == a2_path[step]:
                    # collisions do not happen in aisles
                    if a1_path[step].col == 1 and \
                        a2_path[step].col == 1:
                        continue
                    else:
                        return True
                # they cross over eachother during a step
                elif a1_prev == a2_path[step] and \
                    a2_prev == a1_path[step]:
                    # collisions do not happen in aisles
                    if (a1_prev.col == 1 and a2_path[step].col == 1) or \
                        (a2_prev.col == 1 and a1_path[step].col == 1):
                        continue
                    else:
                        return True
                a1_prev = a1_path[step]
                a2_prev = a2_path[step]
        return False

    def get_last_node(self):
        self.path_schedule()
        return self.last_node

    def cost(self):
        self.path_schedule()
        return self.p_cost

    def copy(self):
        return copy.deepcopy(self)

    def sum(self):
        return compute_sum(self.nodes)

    def total_reward(self):
        return compute_sum(set(self.graph.get_node_list()))

def combine(sols, graph):
    new_sol = Solution(graph)
    for sol in sols:
        for node in sol.nodes:
            new_sol.nodes.add(node)
    new_sol.path_schedule()
    return new_sol