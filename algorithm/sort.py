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
