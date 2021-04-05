
import copy

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
    
    def peekMax(self):
        return self.Heap[self.root]

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
    
    def copy(self):
        return copy.deepcopy(self)

