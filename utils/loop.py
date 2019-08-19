# coding: utf-8

"""参考博客: https://www.zlovezl.cn/articles/two-tips-on-loop-writing/"""

import datetime
from itertools import product, islice, takewhile
import time


def find_twelve(l1, l2, l3):
    """使用product函数扁平化多层循环."""
    for n1, n2, n3 in product(l1, l2, l3):
        if n1 + n2 + n3 == 12:
            return n1, n2, n3


def parse(filename):
    """使用islice函数实现循环内隔行处理"""
    with open(filename, 'r') as fp:
        for line in islice(fp, 0, None, step=2):
            yield line.strip()


def should_take(x):
    return x < 2


def take_while(ll):
    """
      使用takewhile函数代替break
      takewhile(predicate, iterable) 会在迭代iterable的过程中不断使用当前对象作为参数调用predicate函数并测试返回结果，
    如果函数返回值为真，则生成当前对象，循环继续。否则立即中断当前循环
    """
    for i in takewhile(should_take, ll):
        print('Yielding:', i)


# ---------------
"""利用生成器函数解耦循环体"""

def gen_weekend_ts_ranges(days_ago, hour_start, hour_end):
    """生成过去一段时间内周六日特定时间段范围，并以 UNIX 时间戳返回"""
    for days_delta in range(days_ago):
        dt = datetime.date.today() - datetime.timedelta(days=days_delta)
        # 5: Saturday, 6: Sunday
        if dt.weekday() not in (5, 6):
            continue

        time_start = datetime.datetime(dt.year, dt.month, dt.day, hour_start, 0)
        time_end = datetime.datetime(dt.year, dt.month, dt.day, hour_end, 0)

        # 转换为 unix 时间戳
        ts_start = time.mktime(time_start.timetuple())
        ts_end = time.mktime(time_end.timetuple())
        yield ts_start, ts_end


def award_active_users_in_last_30days():
    """发送奖励积分"""
    for ts_start, ts_end in gen_weekend_ts_ranges(30, hour_start=20, hour_end=23):
        pass


def notify_nonsleep_users_in_last_30days():
    """发送通知"""
    for ts_start, ts_end in gen_weekend_ts_ranges(30, hour_start=3, hour_end=6):
        pass
