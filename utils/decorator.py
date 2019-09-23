# coding: utf-8

import time
import threading
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


def logged(func=None, *, level='debug', name=None, message=None):
    """适用于不带参数和带参数的装饰器"""
    if func is None:
        return functools.partial(logged,
                                 level=level,
                                 name=name,
                                 message=message)

    logname = name if name else func.__module__
    logmsg = message if message else func.__name__

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(level, logname, logmsg, sep=' - ')
        return func(*args, **kwargs)

    return wrapper


def retry(times, traced_exceptions=None, reraise_exception=None):
    """
    当被装饰的函数调用抛出指定的异常时，函数会被重新调用，直到达到指定的最大调用次数才重新抛出指定的异常
    :param times: 最大重试次数
    :param traced_exceptions: 需要捕获的错误, 值: None(所有异常类型) or 异常类 or 异常类tuple
    :param reraise_exception: raise错误类型
    :return: 
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            n = times
            trace_specified = traced_exceptions is not None
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    traced = trace_specified and isinstance(
                        e, traced_exceptions)
                    # 若traced_exceptions=None or 未发生指定错误类型 or 已达最大重试次数
                    if not traced or n == 0:
                        if reraise_exception is not None:
                            raise reraise_exception
                        raise
                    n -= 1

        return wrapper

    return decorator


class Singleton(object):
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super().__new__(cls)
        return cls._instance


if __name__ == '__main__':
    # 这次调用将会延迟 2 秒
    add(1, 2)
    # 这次调用将会立即执行
    add.eager_call(1, 2)
