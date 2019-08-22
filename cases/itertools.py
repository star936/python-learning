# coding: utf-8

import itertools as it


def grouper(lst, n, fillvalue=None):
    iters = [iter(lst)] * n    # 创建了对同一个迭代器的n个引用
    return it.zip_longest(*iters, fillvalue=fillvalue)


def group_bills_to_100():
    """
    暴力求解: 你有三张20美元的钞票，五张10美元的钞票，两张5美元的钞票和五张1美元的钞票。可以通过多少种方式得到100美元？
    """
    bills = [20, 20, 20, 10, 10, 10, 10, 10, 5, 5, 1, 1, 1, 1, 1]
    makes_100 = []
    for n in range(1, len(bills) + 1):
        for combination in it.combinations(bills, n):
            if sum(combination) == 100:
                makes_100.append(combination)
    return makes_100


def evens():
    """偶数"""
    return it.count(step=2)


def odds():
    """奇数"""
    return it.count(start=1, step=2)


def chain_repeat_slice():
    cycle = it.chain.from_iterable(it.repeat('abc'))
    return it.islice(cycle, 8)
