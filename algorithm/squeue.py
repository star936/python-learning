# coding: utf-8


class QueueUnderflow(ValueError):
    pass


class SQueue(object):
    """队列类实现"""
    def __init__(self, init_len=0):
        self._len = init_len  # 存储区长度
        self._elems = [0] * init_len  # 元素存储
        self._head = 0  # 表头元素下表
        self._num = 0  # 元素个数

    def is_empty(self):
        return self._num == 0

    def peek(self):
        if self.is_empty():
            raise QueueUnderflow("in SQueue.peek")
        return self._elems[self._head]

    def dequeue(self):
        if self.is_empty():
            raise QueueUnderflow("in SQueue.dequeue")
        e = self._elems[self._head]
        self._head = (self._head + 1) % self._len
        self._num -= 1
        return e

    def enqueue(self, e):
        if self._num == self._len:
            self.__expand()
        self._elems[(self._head+self._num) % self._len] = e
        self._num += 1

    def __expand(self):
        old_len = self._len
        self._len *= 2
        new_elems = [0] * self._len
        for i in range(old_len):
            new_elems[i] = self._elems[(self._head+i) % old_len]
        self._elems, self._head = new_elems, 0
