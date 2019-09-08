# coding: utf-8
"""装饰器模式示例"""

import random


def s32_to_u16(x):
    if x < 0:
        sign = 0xf000
    else:
        sign = 0
    bottom = x & 0x00007fff
    return bottom | sign


def seed_from_xy(x, y):
    return s32_to_u16(x) | (s32_to_u16(y) << 16)


class RandomSquare(object):
    def __init__(self, seed_modifier):
        self.seed_modifier = seed_modifier

    def get(self, x, y):
        seed = seed_from_xy(x, y) ^ self.seed_modifier
        random.seed(seed)
        return random.randint(0, 255)


class DataSquare(object):
    def __init__(self, initial_value=None):
        self.data = [initial_value] * 10 * 10

    def get(self, x, y):
        return self.data[(y * 10) + x]    # yes: these are all 10x10

    def set(self, x, y, u):
        self.data[(y * 10) + x] = u


class CacheDecorator(object):
    def __init__(self, decorated):
        self.decorated = decorated
        self.cache = DataSquare()

    def get(self, x, y):
        if self.cache.get(x, y) is None:
            self.cache.set(x, y, self.decorated.get(x, y))
        return self.cache.get(x, y)


class MaxDecorator(object):
    def __init__(self, decorated, max):
        self.decorated = decorated
        self.max = max

    def get(self, x, y):
        if self.decorated.get(x, y) > self.max:
            return self.max
        return self.decorated.get(x, y)


class MinDecorator(object):
    def __init__(self, decorated, min):
        self.decorated = decorated
        self.min = min

    def get(self, x, y):
        if self.decorated.get(x, y) < self.min:
            return self.min
        return self.decorated.get(x, y)


class VisibilityDecorator(object):
    def __init__(self, decorated):
        self.decorated = decorated

    def get(self, x, y):
        return self.decorated.get(x, y)

    def draw(self):
        for y in range(10):
            for x in range(10):
                print("%3d" % self.get(x, y))


# Now, build up a pipeline of decorators:
random_square = RandomSquare(635)
random_cache = CacheDecorator(random_square)
max_filtered = MaxDecorator(random_cache, 200)
min_filtered = MinDecorator(max_filtered, 100)
final = VisibilityDecorator(min_filtered)

final.draw()
