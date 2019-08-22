# coding: utf-8

from cases.itertools import grouper, group_bills_to_100, evens, odds, chain_repeat_slice


class TestIterTools():
    def test_groper(self):
        num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        real = grouper(num, 4, fillvalue=None)
        expected = [(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, None, None)]
        assert list(real) == expected

    def test_group_bills_to_100(self):
        expected = {(20, 20, 10, 10, 10, 10, 10, 5, 1, 1, 1, 1, 1),
                    (20, 20, 10, 10, 10, 10, 10, 5, 5),
                    (20, 20, 20, 10, 10, 10, 5, 1, 1, 1, 1, 1),
                    (20, 20, 20, 10, 10, 10, 5, 5),
                    (20, 20, 20, 10, 10, 10, 10)}
        real = group_bills_to_100()
        assert set(real) == expected

    def test_even(self):
        expected = [0, 2, 4, 6, 8]
        data = evens()
        real = [next(data) for _ in range(5)]
        assert real == expected

    def test_odd(self):
        expected = [1, 3, 5, 7, 9]
        data = odds()
        real = [next(data) for _ in range(5)]
        assert real == expected

    def test_chain_repeat_slice(self):
        expected = ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b']
        real = chain_repeat_slice()
        assert list(real) == expected
