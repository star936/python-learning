# coding: utf-8

"""串匹配算法"""


def naive_matching(s, sub):
    """朴素的串匹配算法"""
    m, n = len(sub), len(s)
    i, j = 0, 0
    while i < m and j < n:
        if sub[i] == s[j]:
            i, j = i+1, j+1
        else:
            j, j = 0, j-i+1
    if i == m:
        return j - 1
    return -1
