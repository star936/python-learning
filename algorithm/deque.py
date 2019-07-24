# coding: utf-8


class Deque(object):
    """双端队列"""
    def __init__(self):
        self.items = []

    def is_empty(self):
        self.items == []

    def add_front(self, item):
        self.items.append(item)

    def add_rear(self, item):
        self.items.insert(0, item)

    def remove_front(self):
        return self.items.pop()

    def remove_rear(self):
        return self.items.pop(0)

    def size(self):
        return len(self.items)


def palchecker(s):
    """利用deque解决回文词问题"""
    char_deque = Deque()
    for ch in s:
        char_deque.add_rear(ch)
    equal = True
    while char_deque.size() > 1 and equal:
        first = char_deque.remove_front()
        end = char_deque.remove_rear()
        if first != end:
            equal = False
    return equal

