# coding: utf-8

import redis


pool = redis.ConnectionPool(host='localhost', port=6379)
conn = redis.Redis(connection_pool=pool)


def string_to_score(string, ignore_case=False):
    """字符串转换成数字分值:基于数据的前6个字节(48位二进制)进行转换"""
    if ignore_case:
        string = string.lower()
    pieces = list(map(ord, string[:6]))
    while len(pieces) < 6:
        pieces.append(-1)

    score = 0
    for p in pieces:
        # 给每一个ASCII值加上1，使得0作为空字符的填充值
        score = score * 257 + p + 1
    # 加上len(string) > 6标示字符串长度是否超过6个字符
    return score * 2 + (len(string) > 6)


