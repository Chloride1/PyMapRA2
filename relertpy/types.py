# -*- coding: utf-8 -*-
# @Time: 2022/04/20 21:08
# @Author: Chloride
from typing import Sequence, NewType as TypeDef


class Array(Sequence):
    """Just like arrays in C family."""
    def __init__(self, *args):
        if not args:
            self._lst = list()
        elif isinstance(args[0], (list, tuple, set)):
            self._lst = list(*args)
        else:
            self._lst = list(args)

    def __setitem__(self, k, o):
        if not -len(self._lst) < k < len(self._lst):
            raise IndexError("assignment not in the array.")
        return self._lst.__setitem__(k, o)

    def __getitem__(self, k):
        return self._lst.__getitem__(k)

    def __len__(self):
        return len(self._lst)

    def __iter__(self):
        return self._lst.__iter__()

    def __repr__(self):
        return "@({})".format(str(self._lst)[1:-1])

    def __str__(self):
        return ",".join(map(str, self._lst))


class Coord:
    @staticmethod
    def split(obj_coord: str):
        x = int(obj_coord) % 1000
        y = int(obj_coord.rsplit('{:0>3d}'.format(x), 1)[0])
        return x, y

    @staticmethod
    def join(point: TypeDef('Point2D', Array)):
        return "%d" % (1000 * point[1] + point[0])


class Bool:
    __TRUESTR = ('yes', '1', 'true', 'on')
    __FALSESTR = ('no', '0', 'false', 'off')
    bool_like = [j for i in (__FALSESTR, __TRUESTR) for j in i]

    @staticmethod
    def parse(string: str):
        if string.lower() in Bool.__TRUESTR:
            return True
        elif string.lower() in Bool.__FALSESTR:
            return False
        else:
            return None

    @staticmethod
    def tostring(boolean):
        return 'yes' if boolean else 'no'
