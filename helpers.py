from Structures import MaxHeap
# helper functions
def buildMaxHeap(l):
    # inserts elements from a list into a maxheap
    # returns: maxheap
    mh = MaxHeap()
    for elem in l:
        mh.insert(elem)
    return mh

def compute_sum(node_set):
    r = 0
    for node in node_set:
        r += node.val
    return r

def calc_path(graph, target, current, path):
    # calculate the shortest path from current_node to the node passed
        #   in the argument
        # return all nodes on the path to node including node, but not the 
        #   starting point
        if target == current:
            return path
        
        # firstly, if the node is in the same row, we move towards it
        next_node = None
        if current.row == target.row:
            j = 1 if current.col < target.col else -1
            next_node = graph.get(current.row, current.col + j)
        # elif we are at the aisle, but the wrong row
        elif current.col == 1:
            i = 1 if current.row < target.row else -1
            next_node = graph.get(current.row + i, current.col)
        # else we are not at the aisle and in the wrong row
        else:
            next_node = graph.get(current.row, current.col-1)
        path.append(next_node)
        return calc_path(graph, target, next_node, path)


def pair_max(l):
        # l is a list of lists, we want to return the item with the max in the first position
        cur_max = l[0][0]
        max_item = l[0]
        for i in l:
            if i[0] > cur_max:
                cur_max = i[0]
                max_item = i
        return max_item

