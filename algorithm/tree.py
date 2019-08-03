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


class TreeNode(object):
    def __init__(self, key, value, left=None, right=None, parent=None):
        self.key = key
        self.payload = value
        self.leftchild = left
        self.rightchild = right
        self.parent = parent

    def has_leftchild(self):
        return self.leftchild

    def has_rightchild(self):
        return self.rightchild

    def is_leftchild(self):
        return self.parent and self.parent.leftchild == self

    def is_rightchild(self):
        return self.parent and self.parent.rightchild == self

    def is_root(self):
        return not self.parent

    def is_leaf(self):
        return not (self.leftchild or self.rightchild)

    def has_any_children(self):
        return self.leftchild or self.rightchild

    def has_both_children(self):
        return self.leftchild and self.rightchild

    def replace_node_data(self, key, value, lc, rc):
        self.key = key
        self.payload = value
        self.leftchild = lc
        self.rightchild = rc
        if self.has_leftchild():
            self.leftchild.parent = self
        if self.has_rightchild():
            self.rightchild.parent = self

    def splice_out(self):
        if self.is_leaf():
            if self.is_leftchild():
                self.parent.leftchild = None
            else:
                self.parent.rightchild = None
        elif self.has_any_children():
            if self.has_leftchild():
                if self.is_leftchild():
                    self.parent.leftchild = self.leftchild
                else:
                    self.parent.rightchild = self.leftchild
                    self.leftchild.parent = self.parent
            else:
                if self.is_leftchild():
                    self.parent.leftchild = self.rightchild
                else:
                    self.parent.rightchild = self.rightchild
                    self.rightchild.parent = self.parent

    def find_successor(self):
        success = None
        if self.has_rightchild():
            success = self.rightchild.find_min()
        else:
            if self.parent:
                if self.is_leftchild():
                    success = self.parent
                else:
                    self.parent.rightchild = None
                    success = self.parent.find_successor()
                    self.parent.rightchild = self
        return success

    def find_min(self):
        """最小值在左子树"""
        current = self
        while current.has_leftchild():
            current = current.leftchild
        return current


class BinarySearchTree(object):
    def __init__(self):
        self.root = None
        self.size = 0

    def __len__(self):
        return self.size

    def put(self, key, value):
        if self.root:
            self._put(key, value, self.root)
        else:
            self.root = TreeNode(key, value)
            self.size = self.size + 1

    def _put(self, key, value, current):
        if key < current.key:
            if current.has_leftchild():
                self._put(key, value, current.leftchild)
            else:
                current.leftchild = TreeNode(key, value, parent=current)
        elif key == current.key:
            current.payload = value
        else:
            if current.has_rightchild():
                self._put(key, value, current.rightchild)
            else:
                current.rightchild = TreeNode(key, value, parent=current)

    def __setitem__(self, key, value):
        self.put(key, value)

    def get(self, key):
        if self.root:
            res = self._get(key, self.root)
            if res:
                return res.payload
            else:
                return None
        else:
            return None

    def _get(self, key, current):
        if not current:
            return None
        elif current.key == key:
            return current
        elif key < current.key:
            return self._get(key, current.leftchild)
        else:
            return self._get(key, current.rightchild)

    def __getitem__(self, key):
        self.get(key)

    def __contains__(self, key):
        if self._get(key, self.root):
            return True
        else:
            return False

    def delete(self, key):
        if self.size > 1:
            node = self._get(key, self.root)
            if node:
                # TODO remove node
                self.size = self.size - 1
            else:
                raise KeyError("Error, key not in tree")
        elif self.size == 1 and self.root.key == key:
            self.root = None
            self.size = self.size - 1
        else:
            raise KeyError("Error, key not in tree")

    def __delitem__(self, key):
        self.delete(key)

    def remove(self, current):
        if current.is_leaf():
            if current == current.parent.leftchild:
                current.parent.leftchild = None
            else:
                current.parent.rightchild = None
        elif current.has_both_children():
            success = current.find_successor()
            success.splice_out()
            current.key = success.key
            current.payload = success.payload
        else:
            if current.has_leftchild():
                if current.is_leftchild():
                    current.leftchild.parent = current.parent
                    current.parent.leftchild = current.leftchild
                elif current.is_rightchild():
                    current.leftchild.parent = current.parent
                    current.parent.rightchild = current.leftchild
                else:
                    current.replace_node_data(current.leftchild.key,
                                              current.leftchild.payload,
                                              current.leftchild.leftchild,
                                              current.leftchild.rightchild)
            else:
                if current.is_leftchild():
                    current.rightchild.parent = current.parent
                    current.parent.leftchild = current.rightchild
                elif current.is_rightchild():
                    current.rightchild.parent = current.parent
                    current.parent.rightchild = current.rightchild
                else:
                    current.replace_node_data(current.rightchild.key,
                                              current.rightchild.payload,
                                              current.rightchild.leftchild,
                                              current.rightchild.rightchild)

