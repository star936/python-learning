# coding: utf-8

from .node import LNode


class LinkedListUnderflow(ValueError):
    pass


class LList(object):
    """基于LNode定义的一个单链表"""
    def __init__(self):
        self._head = None

    def is_empty(self):
        """判断表是否为空"""
        return self._head is None

    def prepend(self, elem):
        """在表头插入数据"""
        self._head = LNode(elem, self._head)

    def pop(self):
        """删除表头节点并返回这个节点里的数据"""
        if self._head is None:
            raise LinkedListUnderflow("in pop")
        e = self._head.elem
        self._head = self._head.next_
        return e

    def append(self, elem):
        """在表尾插入数据"""
        if self._head is None:
            self._head = LNode(elem)
            return
        p = self._head
        while p.next_ is not None:
            p = p.next_
        p.next_ = LNode(elem)

    def pop_last(self):
        """删除表尾节点并返回这个节点里的数据"""
        if self._head is None:
            raise LinkedListUnderflow("in pop_last")
        p = self._head
        if p.next_ is None:
            e = p.elem
            self._head = None
            return e
        while p.next_.next_ is not None:
            p = p.next_
        e = p.next_.elem
        p.next_ = None
        return e

    def elements(self):
        """使用生成器返回每个节点的数据"""
        p = self._head
        while p is not None:
            yield p.elem
            p = p.next_

