# coding: utf-8

import time
import functools


class DelayFunc(object):
    def __init__(self, duration, func):
        self.duration = duration
        self.func = func

    def __call__(self, *args, **kwargs):
        print(f'Wait for {self.duration} seconds...')
        time.sleep(self.duration)
        return self.func(*args, **kwargs)

    def eager_call(self, *args, **kwargs):
        print('Call without delay')
        return self.func(*args, **kwargs)


def delay(duration):
    """装饰器：推迟某个函数的执行。同时提供 .eager_call 方法立即执行"""
    return functools.partial(DelayFunc, duration)

@delay(duration=2)
def add(a, b):
    return a + b


def counter(func):
    """装饰器: 记录并打印调用次数"""
    count = 0
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal count
        count += 1
        print(f'Count: {count}')
        return func(args, kwargs)
    return wrapper


if __name__ == '__main__':
    # 这次调用将会延迟 2 秒
    add(1, 2)
    # 这次调用将会立即执行
    add.eager_call(1, 2)