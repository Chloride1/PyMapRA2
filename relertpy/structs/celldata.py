# -*- coding: utf-8 -*-
# @Time: 2022/04/25 20:01
# @Author: Chloride
"""
Cell data could be anything on that cell. Basically,
there could be these following items on a cell:

- Waypoint
- Terrain object
- CellTag
- Smudge
- Tile (won't parse in relertpy)
- Overlay (won't parse in relertpy)
- Object instance(s) (in objects.py)

WPs, Terrains, CellTags are all recorded as a tuple:
one is Coord, the other is celldata, which isn't ordered.
"""
from ..types import Array, Coord


class Waypoint(Array):
    __CHARS = list(map(lambda x: chr(x), range(ord('A'), ord('Z') + 1)))

    def __init__(self, kv: tuple):
        self.pid = int(kv[0])
        super().__init__(Coord.split(kv[1]))

    @staticmethod
    def tostring(num):
        ret = []
        if num > 25:
            while True:
                d = int(num / 26)
                remainder = num % 26
                if d <= 26:
                    ret.insert(0, Waypoint.__CHARS[remainder])
                    ret.insert(0, Waypoint.__CHARS[d - 1])
                    break
                else:
                    ret.insert(0, Waypoint.__CHARS[remainder])
                    num = d - 1
        else:
            ret.append(Waypoint.__CHARS[num])
        return "".join(ret)

    @staticmethod
    def toint(wp: str):
        length = len(wp)
        ret = 0
        if length > 1:
            for i in range(length - 1):
                index = Waypoint.__CHARS.index(wp[i])
                # print(index)
                num = pow(26, length - 1) * (index + 1)
                # print(num)
                length -= 1
                ret += num
            ret += Waypoint.__CHARS.index(wp[-1])
        else:
            ret += Waypoint.__CHARS.index(wp[-1])
        return ret

    def apply(self):
        return str(self.pid), Coord.join(self)

    def __repr__(self) -> str:
        return f'WP {self.pid}: {tuple(self)}'


class Terrain(Array):
    def __init__(self, kv: tuple):
        self.terrain = kv[1]
        super().__init__(Coord.split(kv[0]))

    def apply(self):
        return Coord.join(self), self.terrain

    def __repr__(self) -> str:
        return f'Terrain {self.terrain}: {tuple(self)}'


class CellTag(Array):
    def __init__(self, kv: tuple):
        super().__init__(Coord.split(kv[0]))
        self.tagof = kv[1]

    def apply(self):
        return Coord.join(self), self.tagof

    def __repr__(self) -> str:
        return f'Tag {self.tagof}: {tuple(self)}'


class Smudge:
    def __init__(self, args: str):
        params = args.split(",")
        self.typeof = params[0]
        self.coord = Array(map(int, params[1:3]))
        self.ignored = params[3] == '1'

    def apply(self):
        return ",".join(
            map(str,
                [self.typeof, self.coord, int(self.ignored)]
                )
        )

    def __repr__(self) -> str:
        return f'Smudge {self.typeof} TopCell{self.coord}'
