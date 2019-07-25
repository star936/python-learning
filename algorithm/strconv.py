# coding: utf-8

from __future__ import division


def to_str(n, base):
    """利用递归将整数n转化为任意进制表示的字符串形式"""
    convert_string = "0123456789ABCDEF"
    if n < base:
        return convert_string[n]
    else:
        return to_str(n//base, base) + convert_string[n % base]


def rec_mc(coins, change, knowned):
    """利用递归解决'用最少的硬币找零'问题"""
    min_coins = change
    if change in coins:
        knowned[change] = 1
        return 1
    elif knowned[change] > 0:
        return knowned[change]

    else:
        for i in [c for c in coins if c <= change]:
            num_coins = 1 + rec_mc(coins, change-i, knowned)
            if num_coins < min_coins:
                min_coins = num_coins
                knowned[change] = min_coins
    return min_coins


