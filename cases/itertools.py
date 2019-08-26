# coding: utf-8
from collections import namedtuple
import csv
from datetime import datetime
import itertools as it
import functools as ft


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


# 原代码地址:https://juejin.im/post/5d09f8d5e51d45108223fc72
class DataPoint(namedtuple('DataPoint', ['date', 'value'])):
    __slots__ = ()

    def __le__(self, other):
        return self.value <= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value


def consecutive_positives(sequence, zero=0):
    def _consecutives():
        for itr in it.repeat(iter(sequence)):
            yield tuple(
                it.takewhile(lambda p: p > zero,
                             it.dropwhile(lambda p: p <= zero, itr)))

    return it.takewhile(lambda t: len(t), _consecutives())


def read_prices(csvfile, _strptime=datetime.strptime):
    with open(csvfile) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            yield DataPoint(date=_strptime(row['Date'], '%Y-%m-%d').date(),
                            value=float(row['Adj Close']))


def find_prices_result():
    # Read prices and calculate daily percent change.
    prices = tuple(read_prices('../data/SP500.csv'))
    gains = tuple(
        DataPoint(day.date, 100 * (day.value / prev_day.value - 1.))
        for day, prev_day in zip(prices[1:], prices))

    # Find maximum daily gain/loss.
    zdp = DataPoint(None, 0)    # zero DataPoint
    max_gain = ft.reduce(max, it.filterfalse(lambda p: p <= zdp, gains))
    max_loss = ft.reduce(min, it.filterfalse(lambda p: p > zdp, gains), zdp)

    # Find longest growth streak.
    growth_streaks = consecutive_positives(gains, zero=DataPoint(None, 0))
    longest_streak = ft.reduce(lambda x, y: x
                               if len(x) > len(y) else y, growth_streaks)

    # Display results.
    print('Max gain: {1:.2f}% on {0}'.format(*max_gain))
    print('Max loss: {1:.2f}% on {0}'.format(*max_loss))

    print('Longest growth streak: {num_days} days ({first} to {last})'.format(
        num_days=len(longest_streak),
        first=longest_streak[0].date,
        last=longest_streak[-1].date))
