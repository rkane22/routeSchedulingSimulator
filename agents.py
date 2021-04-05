from Graph import AisleGraph, Vertex
from Solution import Solution
from helpers import calc_path, compute_sum, pair_max, buildMaxHeap
import Graph
import copy
import sys

MAX_COST = sys.maxsize

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

    # paper 1

    def Gdy(self):
        g = self.graph
        # initialize the solution with starting node v[1,1] 
        starting_node = g.get(1, 1)
        s = Solution(g)
        s.nodes.add(starting_node)
        self.current_node = starting_node
        # construct a max heap of all the other vertices according to their rewards
        node_list = g.get_node_list()
        node_list.remove(starting_node)
        heap = buildMaxHeap(node_list)
        # iterate through the heap, stop if the cost of the trip exceeds the budget or if 
        #   no greater reward can be reached
        while not heap.empty() and s.cost() <= self.budget and heap.peekMax() > 0:
            # with the largest reward, if it is reachable within budget, travel to it
            new_node = heap.extractMax()
            s_new = s.copy()
            s_new.nodes.add(new_node)
            # check if node is feasibly reached
            if s_new.cost() < self.budget:
                s.nodes.add(new_node)
            # otherwise discard and continue
        # return the solution
        return s

    def GdyME(self):
        self.graph.set_compare_mode(Graph.DEFAULT)
        return self.Gdy()

    def GdyMC(self):
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        return self.Gdy()
        
    # paper 2
    
    # Multiagent strategies
    def sectioning(self, num_agents):
        # section each part of the vineyard so that the agents
        # only operate on disjoint subsets of the graph.
        # For our Aisle Graph we separate by full rows
        full_sol = Solution(self.graph)
        full_sol.nodes = set(self.graph.get_node_list())
        total_reward = full_sol.sum()
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        agents = []
        j = 1
        for _ in range(num_agents):
            # track which row we left off from
            i = j
            # calculate section of graph using percentage of reward
            #  vs percentage of budget each agent will have.
            s = Solution(self.graph)
            b_agent = int(self.budget / num_agents)
            p_agent = b_agent / self.budget
            while  j < self.graph.rows():
                # add the next row to the sum
                s.nodes.add(self.graph.aisle[j][-1])
                s.path_schedule()
                if s.sum()/total_reward <= p_agent:
                    # agent moves to next row
                    j += 1
                else: 
                    break

            # get copy of graph
            temp_graph = self.graph.copy()
            # set nodes not in the span of rows i,j to 0
            for row in range(1, temp_graph.rows()+1):
                for col in range(0, temp_graph.cols()):
                    if row < i or row > j:
                        temp_graph.aisle[row-1][col].c_val = 0
            j+=1
            new_agent = Traverser(temp_graph, b_agent)
            agents.append(new_agent)
        sols = []

        for agent in agents:
            sol = agent.Gdy()
            sol.graph.set_compare_mode(Graph.CUMULATIVE)
            sols.append(sol)
        return sols

    def series(self, num_agents):
        # run single agent algorithm in series, except with a time conflict map
        # to avoid collision
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        agents = []
        temp_graph = self.graph.copy()
        conflicts = []
        sols = []
        for _ in range(num_agents):
            b_agent = int(self.budget / num_agents)
            new_agent = Traverser(temp_graph, b_agent)
            agents.append(new_agent)
            sol = new_agent.Gdy_WA(conflicts)
            conflicts.append(sol)
            sols.append(sol)
            # set all visited vertices reward to 0
            for node in sol.nodes:
                temp_graph.aisle[node.row-1][node.col-1].c_val = 0
        for sol in sols:
            sol.graph.set_compare_mode(Graph.CUMULATIVE)
        return sols

    def Gdy_WA(self, conflicts):
        # the main difference in this modification of the algorithm
        # is the addition of waiting
        g = self.graph
        # initialize the solution with starting node v[1,1] 
        starting_node = g.get(1, 1)
        s = Solution(g)
        s.nodes.add(starting_node)
        self.current_node = starting_node
        # construct a max heap of all the other vertices according to their rewards
        node_list = g.get_node_list()
        node_list.remove(starting_node)
        heap = buildMaxHeap(node_list)
        blacklist = set()
        # iterate through the heap, stop if the cost of the trip exceeds the budget or if 
        #   no greater reward can be reached
        while (not heap.empty()) and (s.cost() < self.budget) and (heap.peekMax().get_val() > 0):
            # if the current max node has been blacklisted discard it
            if heap.peekMax() in blacklist:
                heap.extractMax()
                continue
            # find best node with no time conflicts
            new_node = None
            temp_heap = heap.copy()
            while (not temp_heap.empty()) and (temp_heap.peekMax().get_val() > 0):
                max_node = temp_heap.extractMax()
                if max_node in blacklist:
                    continue
                s_new = s.copy()
                s_new.nodes.add(max_node)
                if s_new.check_conflicts(conflicts):
                    if max_node.row < s.get_last_node().row:
                        blacklist.add(max_node)
                    continue
                new_node = max_node
                break
            if new_node is None:
                # if there are no available nodes due to time conflicts, wait 1 time unit
                s.waits.append(s.get_last_node())
            else:
                # otherwise add the max node to the solution if feasible
                s_new = s.copy()
                s_new.nodes.add(new_node)
                if s_new.cost() < self.budget:
                    # node is feasible
                    s.nodes.add(new_node)
                    s.path_schedule()
                    for n in s.nodes:
                        # blacklist all visited nodes
                        blacklist.add(n)
                else:
                    # node is infeasible, blacklist it
                    blacklist.add(new_node)
            # print(s.get_last_node(), len(s.nodes), s.cost(), len(s.waits))
            if len(s.waits) > 30:
                return s
            
        # return the solution
        return s

    def parallel(self, num_agents):
        # this requires a new form of the greedy algorithm because
        # we need to compute the routes in parallel
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        g = self.graph
        # initialize the solution with starting node v[1,1] 
        starting_node = g.get(1, 1)
        s = Solution(g)
        s.nodes.add(starting_node)
        self.current_node = starting_node
        # construct a max heap of all the other vertices according to their rewards
        node_list = g.get_node_list()
        node_list.remove(starting_node)
        heap = buildMaxHeap(node_list)
        b_agent = int(self.budget/num_agents)
        # create pairs of solutions and agents
        agents = [s.copy() for _ in range(num_agents)]
        # iterate through the heap, stop if the cost of the trip exceeds the budget or if 
        #   no greater reward can be reached
        blacklists = [set() for _ in range(num_agents)]
        while (not heap.empty()) and (sol.cost() < b_agent for sol in agents) and (heap.peekMax().val > 0):
            # if the current best node has already been visited, discard it
            for blacklist in blacklists:
                if heap.peekMax() in blacklist:                    
                    heap.extractMax()
                    continue
            candidates = set()
            for i in range(num_agents):
                choice = None
                done = True
                # check for conflicts
                conflicts = [s for s in agents]
                conflicts = conflicts[:i] + conflicts[i+1:]
                agent_heap = heap.copy()
                while not agent_heap.empty() and agent_heap.peekMax().get_val() > 0:
                    # find best node for this agent without time conflicts
                    new_node = agent_heap.extractMax()
                    if new_node in blacklists[i]:
                        continue
                    new_sol = agents[i].copy()
                    new_sol.nodes.add(new_node)
                    if new_sol.check_conflicts(conflicts):
                        if new_node.row >= agents[i].get_last_node().row:
                            done = False
                    else:
                        choice = new_node
                        break
                if (choice is None) or (done is False):
                    agents[i].waits.append(agents[i].get_last_node())
                else:
                    candidates.add(choice)
            for node in candidates:
                # find best agent
                best_agent = -1
                min_cost = MAX_COST
                for i in range(len(agents)):
                    s_new = agents[i].copy()
                    s_new.nodes.add(node)
                    conflicts = [sol for sol in agents]
                    conflicts = conflicts[:i] + conflicts[i+1:]
                    # if no conflicts
                    if (not s_new.check_conflicts(conflicts)):
                        # if feasible
                        if (not node in blacklists[i]) and s_new.cost() < b_agent:
                            # measure cost
                            new_cost = len(calc_path(s.graph, node, s.get_last_node(), []))
                            if new_cost < min_cost:
                                min_cost = new_cost
                                best_agent = i
                        else:
                            blacklists[i].add(node)
                if best_agent >= 0:
                    agents[best_agent].nodes.add(node)
                    for n in agents[best_agent].path_schedule():
                        for blacklist in blacklists:
                            blacklist.add(n)
        # return the solution
        return agents

    def parallel2(self, num_agents):
        # this requires a new form of the greedy algorithm because
        # we need to compute the routes in parallel
        self.graph.set_compare_mode(Graph.CUMULATIVE)
        g = self.graph
        # initialize the solution with starting node v[1,1] 
        starting_node = g.get(1, 1)
        s = Solution(g)
        s.nodes.add(starting_node)
        self.current_node = starting_node
        # construct a max heap of all the other vertices according to their rewards
        node_list = g.get_node_list()
        node_list.remove(starting_node)
        heap = buildMaxHeap(node_list)
        b_agent = int(self.budget/num_agents)
        # create pairs of solutions and agents
        agents = [s.copy() for _ in range(num_agents)]
        # iterate through the heap, stop if the cost of the trip exceeds the budget or if 
        #   no greater reward can be reached
        blacklists = [set() for _ in range(num_agents)]
        while (not heap.empty()) and (sol.cost() < b_agent for sol in agents) and (not sol.done for sol in agents)and (heap.peekMax().val > 0):
            # if the current best node has already been visited, discard it
            for blacklist in blacklists:
                if heap.peekMax() in blacklist:                    
                    heap.extractMax()
                    continue
            candidates = set()
            for i in range(num_agents):
                choice = None
                done = True
                # check for conflicts
                conflicts = [s for s in agents]
                conflicts = conflicts[:i] + conflicts[i+1:]
                agent_heap = heap.copy()
                if agents[i].done:
                    continue
                elif agents[i].sum() >= b_agent:
                    agents[i].done = True
                while not agent_heap.empty() and agent_heap.peekMax().get_val() > 0:
                    # find best node for this agent without time conflicts
                    new_node = agent_heap.extractMax()
                    if new_node in blacklists[i]:
                        continue
                    new_sol = agents[i].copy()
                    new_sol.nodes.add(new_node)
                    if new_sol.check_conflicts(conflicts):
                        if new_node.row >= agents[i].get_last_node().row:
                            done = False
                    else:
                        choice = new_node
                        break
                if (choice is None):
                    if (done is False):
                        agents[i].waits.append(agents[i].get_last_node())
                    else:
                       agents[i].done = True 
                else:
                    candidates.add(choice)
            for node in candidates:
                # find best agent
                best_agent = -1
                min_cost = MAX_COST
                for i in range(len(agents)):
                    if agents[i].done:
                        continue
                    s_new = agents[i].copy()
                    s_new.nodes.add(node)
                    conflicts = [sol for sol in agents]
                    conflicts = conflicts[:i] + conflicts[i+1:]
                    # if no conflicts
                    if (not s_new.check_conflicts(conflicts)):
                        # if feasible
                        if (not node in blacklists[i]) and s_new.cost() < b_agent:
                            # measure cost
                            new_cost = len(calc_path(s.graph, node, s.get_last_node(), []))
                            if new_cost < min_cost:
                                min_cost = new_cost
                                best_agent = i
                        else:
                            blacklists[i].add(node)
                if best_agent >= 0:
                    agents[best_agent].nodes.add(node)
                    for n in agents[best_agent].path_schedule():
                        for blacklist in blacklists:
                            blacklist.add(n)
        # return the solution
        return agents
