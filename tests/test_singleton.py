# coding: utf-8

from unittest import TestCase

from utils.decorator import Singleton


class TestSingleton(TestCase):
    def test_singleton(self):
        obj1 = Singleton()
        obj2 = Singleton()

        assert obj1 == obj2
        assert obj1 is obj2
