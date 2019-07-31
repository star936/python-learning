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
