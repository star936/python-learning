# coding: utf-8

from .node import LNode
from .sstack import StackUnderflow


class LStack(object):
    """采用链接表实现栈"""
    def __init__(self):
        self._top = None

    def is_empty(self):
        return self._top is None

    def top(self):
        if self.is_empty():
            raise StackUnderflow("in LStack.top")
        return self._top.elem

    def push(self, elem):
        self._top = LNode(elem, self._top)

    def pop(self):
        if self.is_empty():
            raise StackUnderflow("in LStack.pop")
        p = self._top
        self._top = p.next
        return p.elem

