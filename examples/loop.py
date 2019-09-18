# coding: utf-8
"""
使用for的死循环
iter的第二种形式: iter(callable, sentinel) -> iterator
    当callable的返回值等于sentinel时callable停止调用; 否则一直调用callable
int()的返回值为0
"""

for i in iter(int, 1):
    pass
