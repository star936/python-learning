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


"""KMP算法"""


def gen_pnext(p):
    """生成针对p中各位置i的下一检查位置表，用于KMP算法"""
    i, k, m = 0, -1, len(p)
    pnext = [-1] * m
    while i < m-1:
        if k == -1 or p[i] == p[k]:
            i, k = i+1, k+1
            pnext[i] = k
        else:
            k = pnext[i]
    return pnext


def matching_kmp(t, p, pnext):
    """KMP串匹配"""
    j, i = 0, 0
    n, m = len(t), len(m)
    while j < n and i < m:
        if i == -1 or t[j] == p[i]:
            j, i = j+1, i+1
        else:
            i = pnext[i]
    if i == m:
        return j-i
    return -1

