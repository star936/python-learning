# coding: utf-8

from __future__ import division


def binary_search(alist, item):
    """二分搜索: alist为一个有序列表"""
    first = 0
    last = len(alist) - 1
    found = False
    while first <= last and not found:
        middle = (first + last) // 2
        if alist[middle] == item:
            found = True
        else:
            if item < alist[middle]:
                last = middle - 1
            else:
                first = middle + 1
    return found
