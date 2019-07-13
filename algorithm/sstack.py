# coding: utf-8


class StackUnderflow(ValueError):
    pass


class SStack(object):
    """采用动态顺序表实现的栈"""
    def __init__(self):
        self._elems = []

    def is_empty(self):
        return len(self._elems) == 0

    def top(self):
        if self.is_empty():
            raise StackUnderflow("in SStack.top")
        return self._elems[-1]

    def push(self, elem):
        self._elems.append(elem)

    def pop(self):
        if self.is_empty():
            raise StackUnderflow("in SStack.pop")
        return self._elems.pop()

