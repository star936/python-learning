# coding: utf-8

"""
背包问题：
    一个背包可以放入重量为weight的物品，现有n件物品的集合S，
    其中物品的重量分别为w0, w1, w2, ..., w(n-1).能否从中
    选出若干个物品，其重量之和正好等于weight?

分析:
    假设weight>=0, n>=0; 用记法knap(weight,n)表示n件物品
    相对于总重量weight的背包问题,在考虑它是否有解时，通过考虑
    一件物品的选或者不选，可以把问题分为两种情况：
    1：如果不选最后一件物品，那么knap(weight, n-1)的解就是
    knap(weight,n)的解；
    2：如果选最后一件物品,那么如果knap(weight-w(n-1),  n-1)
    有解，其解加上最后一件物品的knap(weight, n)的解。
"""


def knap_rec(weight, wlist, n):
    if weight == 0:
        return True
    if weight < 0 or (weight > 0 and n < 1):
        return False
    if knap_rec(weight - wlist[n-1], wlist, n-1):
        return True
    if knap_rec(weight, wlist, n-1):
        return True
    else:
        return False


