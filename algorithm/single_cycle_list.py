# coding: utf-8

from .node import LNode, LinkedListUnderflow


class CLList(object):
    """循环单链表"""
    def __init__(self):
        self._rear = None

    def is_empty(self):
        """判断表是否为空"""
        return self._rear is None

    def prepend(self, elem):
        """在表头插入数据"""
        p = LNode(elem)
        if self._rear is None:
            # 建立一个节点的环
            p.next_ = p
            self._rear = p
        else:
            p.next_ = self._rear.next_
            self._rear.next_ = p

    def append(self, elem):
        """在表尾插入数据"""
        self.prepend(elem)
        self._rear = self._rear.next_

    def pop(self):
        """删除表头节点并返回这个节点里的数据"""
        if self._rear is None:
            raise LinkedListUnderflow("in pop of CLList")
        p = self._rear.next_
        if self._rear is p:
            self._rear = None
        else:
            self._rear.next_ = p.next_
        return p.elem


