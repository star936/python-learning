# coding: utf-8


def bubble_sort(arr):
    """改进的冒泡排序: found表示在扫描检查中是否遇到了逆序，True: 存在逆序."""
    for i in range(len(arr)):
        found = False
        for j in range(1, len(arr)-i):
            if arr[j-1] > arr[j]:
                arr[j-1], arr[j] = arr[j], arr[j-1]
                found = True
        if not found:
            break


def quick_sort(arr):
    """快速排序"""
    def qsort(arr, begin, end):
        if begin >= end:
            return
        pivot = arr[begin]
        i = begin
        for j in range(begin+1, end+1):
            if arr[j] < pivot:  # 发现小元素
                i += 1
                arr[i], arr[j] = arr[j], arr[i]  # 小元素换位
        arr[begin], arr[i] = arr[i], arr[begin]  # 分界点就位
        qsort(arr, begin, i-1)
        qsort(arr, i+1, end)
    qsort(arr, 0, len(arr) - 1)


def insert_sort(alist):
    """插入排序"""
    for index in range(1, len(alist)):
        value = alist[index]
        pos = index
        while pos > 0 and alist[pos-1] > value:
            alist[pos] = alist[pos-1]
            pos = pos - 1
            alist[pos] = value


def gap_insertion_sort(sub_list, start, gap):
    for i in range(start+gap, len(sub_list), gap):
        value = sub_list[i]
        pos = i
        while pos >= gap and sub_list[pos-gap] > value:
            sub_list[pos] = sub_list[pos-gap]
            pos = pos-gap
            sub_list[pos] = value


def shell_sort(alist):
    """希尔排序"""
    sublist_count = len(alist) // 2
    while sublist_count > 0:
        for start_pos in range(sublist_count):
            gap_insertion_sort(alist, start_pos, sublist_count)
            print("After increments of size", sublist_count, "The list is", alist)
        sublist_count = sublist_count // 2

