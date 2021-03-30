from Graph import AisleGraph, Vertex
import Graph


class MaxHeap:
    def __init__(self):
        self.Heap = [None] # first index is a placeholder and should never be accessed
        self.root = 1 # for index operations it has to be 1 

    def size(self):
        return len(self.Heap) -1 # to account for the null at pos 0

    def parent(self, i):
        return i // 2

    def leftChild(self, i):
        return i*2

    def rightChild(self, i):
        return (i * 2) + 1

    def isLeaf(self, i):
        if i >= (self.size()//2) and i <= self.size():
            return True
        else:
            return False

    def swap(self, i, j):
        self.Heap[i], self.Heap[j] = (self.Heap[j], self.Heap[i])

    def maxHeapify(self, i):
        
        if not self.isLeaf(i):
            if ((self.Heap[i]< self.Heap[self.leftChild(i)]) 
                or (self.Heap[i]< self.Heap[self.rightChild(i)])):
                
                if self.Heap[self.leftChild(i)] > self.Heap[self.rightChild(i)]:
                    self.swap(i, self.leftChild(i))
                    self.maxHeapify(self.leftChild(i))
                else: 
                    self.swap(i, self.rightChild(i))
                    self.maxHeapify(self.rightChild(i))

    def insert(self, element):
        self.Heap.append(element)
        current = self.size()
        while ((current != self.root) and (self.Heap[current] > self.Heap[self.parent(current)])):
            self.swap(current, self.parent(current))
            current = self.parent(current)
    
    def extractMax(self):
        if self.empty():
            return None
        popped = self.Heap[self.root]
        self.Heap[self.root] = self.Heap[self.size()]
        del self.Heap[-1]
        if not self.empty():
            self.maxHeapify(self.root)
        return popped
    
    def empty(self):
        if len(self.Heap) <=1:
            return True
        else:
            return False
        
    def __str__(self):
        return str(self.Heap[1:])

    def __repr__(self):
        return str(self.Heap[1:])

def buildMaxHeap(l):
    # inserts elements from a list into a maxheap
    # returns: maxheap
    mh = MaxHeap()
    for elem in l:
        mh.insert(elem)
    return mh

class Traverser():
    # uses the strategy pattern to select how it will traverse a graph
    #   ie: which algorithm to use
    def __init__(self, graph: AisleGraph, budget: int):
        # super.__init__(self)
        #Graph
        self.graph = graph

        # Budget 
        self.initial_budget = budget
        self.budget = budget
    
    def reset(self):
        # reset Traverser
        self.budget = self.initial_budget
        # reset graph
        self.graph.reset()

    def cost(self, node_set):
        # The structure of an aisle graph means the shortest path to each nodes is uniqie
        nodes = node_set
        costs = {}
        for node in nodes:
            if node.pos_y in costs.keys():
                if node.pos_x > costs[node.pos_y]:
                    costs[node.pos_y] = node.pos_x - 1
            else:
                costs[node.pos_y] = node.pos_x - 1
        # return sum of costs
        cost = 0
        y_max = 0
        for y in costs.keys():
            cost += costs[y] - 1
            if y > y_max:
                y_max = y
        cost += y_max
        # cost to get back to start
        return cost + y_max + costs[y_max]


    def calc_path(self, target_node, current_node, path):
        # calculate the shortest path from current_node to the node passed
        #   in the argument
        # return all nodes on the path to node including node, but not the 
        #   starting point
        
        # firstly, if the node is in the same row, we move towards it
        next_node = None
        if current_node.pos_y == target_node.pos_y:
            j = 1 if current_node.pos_x < target_node.pos_x else -1
            next_node = self.graph.get_xy(current_node.pos_x + j, current_node.pos_y)
        # if we are at the aisle
        elif current_node.pos_x == 1:
            i = 1 if current_node.pos_y < target_node.pos_y else -1
            next_node = self.graph.get_xy(current_node.pos_x, current_node.pos_y + i)
        # if we are not at the aisle and in the wrong row
        else:
            next_node = self.graph.get_xy(current_node.pos_x-1, current_node.pos_y)
        path.append(next_node)
        return path if next_node == target_node else self.calc_path(target_node, next_node, path)

    # algorithms from paper 1

    def Gdy(self):
        g = self.graph
        # initialize the solution with starting node v[1,1] 
        starting_node = g.get(1, 1)
        s = set()
        s.add(starting_node)
        self.current_node = starting_node
        # construct a max heap of all the other vertices according to their rewards
        node_list = g.get_node_list()
        node_list.remove(starting_node)
        heap = buildMaxHeap(node_list)
        # iterate through the heap, stop if the cost of the trip exceeds the budget
        while not heap.empty() and self.cost(s) <= self.budget:
            # with the largest reward, if it is reachable within budget, travel to it
            new_node = heap.extractMax()
            path = self.calc_path(new_node, starting_node, [])
            s_new = s.copy()
            s_new.add(new_node)
            if self.cost(s_new) < self.budget:
                # when travelling to the vertex, add all intermediate vertices to the solution
                # as well since the rewards are collected on the way
                for n in path:
                    s.add(n) # since s is a set we cant add twice
            # otherwise discard and continue
                
        # return the reward for all vertices in the solution space
        return s, sum_node_set(s)

    def GdyME(self):
        return self.Gdy()

    def GdyMC(self):
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        return self.Gdy()

    def ApxMRE(self):
        r_max = -1
        s_1 = set()
        g = self.graph
        starting_node = g.get_xy(1,1)
        s_2 = set()
        s_2.add(starting_node)
        # construct a 2d matrix H[i,d]
        H = []
        for i in range(g.rows()):
            # print(i, H)
            H.append([])
            for d in range(i+1):
                H[i].append([])
                for j in range(g.cols()):
                    v = g.get(i, j)
                    H[i][d].append(((v.val/(2*(j)+2*d) if j > 0 else 0), v))
                    if (2*(j) + 2*d) <= self.budget:
                        if v.val > r_max:
                            r_max = v.val
                            s_1.add(v)
        i_max = 1
        while self.cost(s_2) < self.budget:
            M = []
            for i in range(1, g.rows() + 1):
                M.append(i)
            for i in range(g.rows()):
                if i <= i_max:
                    M[i] = pair_max(H[i][0])
                else:
                    M[i] = pair_max(H[i][i-i_max])

            v = pair_max(M)
            s_2new = s_2.copy()
            s_2new.add(v[1])
            if self.cost(s_2new) <= self.budget:
                path = self.calc_path(v[1], starting_node, [])
                # when travelling to the vertex, add all intermediate vertices to the solution
                # as well since the rewards are collected on the way
                for n in path:
                    for d in range(n.pos_y):
                        H[n.pos_y-1][d][n.pos_x-1] = (0, n)
                    s_2.add(n) # since s is a set it will not repeat nodes
                for k in range(v[1].pos_x, g.cols()):
                    H[v[1].pos_y-1][0][k] = (v[1].val/(2*(k - (v[1].pos_x-1))), v[1])
            else:
                break
            print(s_2)
            print(self.cost(s_2))
            print(M)
            i_max = max([v[1].pos_y-1, i_max])
        print(self.cost(s_1), sum_node_set(s_1), s_1)
        print(self.cost(s_2), sum_node_set(s_2), s_2)
        return (sum_node_set(s_1), s_1) if sum_node_set(s_1) > sum_node_set(s_2) else (sum_node_set(s_2), s_2)
        
    # algorithms from paper 2
    
    # Multiagent strategies
    def sectioning(self, num_agents):
        # section each part of the vineyard so that the agents
        # only operate on disjoint subsets of the graph.
        # For our Aisle Graph we separate by full rows
        total_reward = sum_node_set(set(self.graph.get_node_list()))
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        agents = []
        j = 1
        for i in range(num_agents):
            # track where we started from
            i = j
            # calculate section of graph using percentage of reward
            #  vs percentage of budget each agent will have.
            s = 0
            b_agent = int(self.budget / num_agents)
            p_agent = b_agent / self.budget
            while s/total_reward < p_agent:
                # agent takes next row
                j += 1
                s += sum_node_set(self.graph.get_xy(-1, j))
            # get copy of graph
            temp_graph = self.graph.copy()
            # set nodes not in the span of rows i,j to 0
            for row in range(i, j):
                for col in range(1, temp_graph.cols + 1):
                    temp_graph.set(row,col,0)
            new_agent = Traverser(temp_graph, b_agent)
            agents.append(new_agent)
        
        sols = []
        sol_sets = []

        for agent in agents:
            sol, sol_set = agent.Gdy()
            sols.append(sol)
            sol_sets.append(sol_set)
        return sum(sols), sol_sets

    def series(self, num_agents):
        # run single agent algorithm in series, except with a time conflict map
        # to avoid collision
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        

    def parallel(self, num_agents):
        # this requires a new form of the greedy algorithm because
        # we need to compute the routes in parallel
        self.graph.set_compare_mode(Graph.CUMULATIVE)

        # while all the agent tours are not completed
        # 
        pass

def sum_node_set(node_set):
    r = 0
    for node in node_set:
        r += node.val
    return r

def pair_max(l):
        # l is a list of lists, we want to return the item with the max in the first position
        cur_max = l[0][0]
        max_item = l[0]
        for i in l:
            if i[0] > cur_max:
                cur_max = i[0]
                max_item = i
        return max_item