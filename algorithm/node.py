# coding: utf-8


class LNode(object):
    """节点类"""
    def __init__(self, elem, next_=None):
        self.elem = elem
        self.next_ = next_
