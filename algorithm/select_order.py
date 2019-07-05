# coding: utf-8


def find_smallest(arr):
    smallest = arr[0]
    smallest_index = 0
    for i in range(0, len(arr)):
        if arr[i] < smallest:
            smallest = arr[i]
            smallest_index = i
    return smallest_index


def select_order(arr):
    new_arr = []
    for i in range(len(arr)):
        index = find_smallest(arr)
        new_arr.append(arr.pop(index))
    return new_arr


if __name__ == '__main__':
    print(select_order([5, 3, 6, 2, 10]))
