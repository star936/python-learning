# coding: utf-8


class BinaryTree(object):
    def __init__(self, root):
        self.key = root
        self.leftChild = None
        self.rightChild = None

    def insert_left(self, node):
        """插入一个左子节点，并将已存在的子节点降级"""
        if self.leftChild is None:
            self.leftChild = BinaryTree(node)
        else:
            t = BinaryTree(node)
            t.leftChild = self.leftChild
            self.leftChild = t

    def insert_right(self, node):
        """插入一个右子节点，并将已存在的子节点降级"""
        if self.rightChild is None:
            self.rightChild = BinaryTree(node)
        else:
            t = BinaryTree(node)
            t.rightChild = self.rightChild
            self.rightChild = t

    def get_rightchild(self):
        return self.rightChild

    def get_leftchild(self):
        return self.leftChild

    def set_rootvalue(self, root):
        self.key = root

    def get_rootvalue(self):
        return self.key


class BinHeap(object):
    """二叉堆"""
    def __init__(self):
        self.heapList = [0]
        self.currentSize = 0

    def percUp(self, i):
        """最小堆: 根节点存储最小值"""
        while i//2 > 0:
            if self.heapList[i] < self.heapList[i//2]:
                self.heapList[i//2], self.heapList[i] = self.heapList[i], self.heapList[i//2]
            i = i//2

    def insert(self, k):
        self.heapList.append(k)
        self.currentSize = self.currentSize + 1
        self.percUp(self.currentSize)

    def percDown(self, i):
        while (i*2) <= self.currentSize:
            mc = self.minChild(i)
            if self.heapList[i] > self.heapList[mc]:
                self.heapList[i], self.heapList[mc] = self.heapList[mc], self.heapList[i]
            i = mc

    def minChild(self, i):
        if i*2 + 1 > self.currentSize:
            return i*2
        else:
            if self.heapList[i*2] < self.heapList[i*2+1]:
                return i*2
            else:
                i*2 + 1

    def delMin(self):
        value = self.heapList[1]
        self.heapList[1] = self.heapList[self.currentSize]
        self.currentSize = self.currentSize - 1
        self.heapList.pop()
        self.percDown(1)
        return value

