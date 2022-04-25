# -*- coding: utf-8 -*-
# @Time: 2022/04/25 20:31
# @Author: Chloride
"""
Just those you can build, like infantries, aircrafts,
buildings, vehicles.
"""
from ..types import Array


class CInfantry:
    def __init__(self):
        self.owner = 'Neutral House'
        self.typeof = 'E1'
        self.health = 256
        self.coord = Array(0, 0)
        self.subcell = 0
        self.mission = 'Guard'
        self.facing = 0
        self.tag = None
        self.veteran = 0
        self.group = -1
        self.onbridge = False
        self.autocreate_no = False
        self.autocreate_yes = True

    @classmethod
    def loadinf(cls, args: str):
        args = args.split(',')
        ret = cls()
        ret.owner = args[0]
        ret.typeof = args[1]
        ret.health = int(args[2])
        ret.coord = Array(map(int, args[3:5]))
        ret.subcell = int(args[5])
        ret.mission = args[6]
        ret.facing = int(args[7])
        ret.tag = None if args[8] == 'None' else args[8]
        ret.veteran = int(args[9])
        ret.group = int(args[10])
        ret.onbridge = args[11] == '1'
        ret.autocreate_no = args[12] == '1'
        ret.autocreate_yes = args[13] == '1'
        return ret

    def apply(self):
        return ",".join(map(str, [
            self.owner, self.typeof, self.health, self.coord, self.subcell,
            self.mission, self.facing, self.tag, self.veteran, self.group,
            int(self.onbridge),
            int(self.autocreate_no), int(self.autocreate_yes)
        ]))

    def __repr__(self) -> str:
        return f'Infantry {self.typeof} {self.coord}'


class CVehicle:
    def __init__(self):
        self.owner = 'Neutral House'
        self.typeof = 'AMCV'
        self.health = 256
        self.coord = Array(0, 0)
        self.facing = 0
        self.mission = 'Guard'
        self.tag = None
        self.veteran = 0
        self.group = -1
        self.onbridge = False
        self.train_follow = False
        self.autocreate_no = False
        self.autocreate_yes = True

    @classmethod
    def loadunit(cls, args: str):
        args = args.split(',')
        ret = cls()
        ret.owner = args[0]
        ret.typeof = args[1]
        ret.health = int(args[2])
        ret.coord = Array(map(int, args[3:5]))
        ret.facing = int(args[5])
        ret.mission = args[6]
        ret.tag = None if args[7] == 'None' else args[7]
        ret.veteran = int(args[8])
        ret.group = int(args[9])
        ret.onbridge = args[10] == '1'
        ret.train_follow = args[11] == '1'
        ret.autocreate_no = args[12] == '1'
        ret.autocreate_yes = args[13] == '1'
        return ret

    def apply(self):
        return ",".join(map(str, [
            self.owner, self.typeof, self.health, self.coord, self.facing,
            self.mission, self.tag, self.veteran, self.group,
            int(self.onbridge), int(self.train_follow),
            int(self.autocreate_no), int(self.autocreate_yes)
        ]))

    def __repr__(self) -> str:
        return f'Vehicle {self.typeof} {self.coord}'


class CBuilding:
    def __init__(self):
        self.owner = 'Neutral House'
        self.typeof = 'GAPOWR'
        self.health = 256
        self.coord = Array(0, 0)  # only consider the top
        self.facing = 0
        self.tag = None
        self.ai_sellable = False
        self.ai_rebuildable = False  # obsolete, as base node implemented
        self.powered = True
        self.upgrades = []
        self.spotlight = 0
        self.ai_repair = True
        self.norminal = False  # EnemyUIName doesn't work until Ares0b.

    @classmethod
    def loadbuilding(cls, args: str):
        args = args.split(',')
        ret = cls()
        ret.owner = args[0]
        ret.typeof = args[1]
        ret.health = int(args[2])
        ret.coord = Array(map(int, args[3:5]))
        ret.facing = int(args[5])
        ret.tag = None if args[6] == 'None' else args[6]
        ret.ai_sellable = args[7] == '1'
        ret.ai_rebuildable = args[8] == '1'
        ret.powered = args[9] == '1'
        ret.upgrades = [args[12:15][i]
                        for i in range(int(args[10]))
                        if args[12:15][i] != 'None']
        ret.spotlight = int(args[11])
        ret.ai_repair = args[15] == '1'
        ret.norminal = args[16] == '1'
        return ret

    def apply(self):
        ups = self.upgrades.copy()
        ups.extend('None' for _ in range(3 - len(self.upgrades)))
        return ",".join(map(str, [
            self.owner, self.typeof, self.health, self.coord, self.facing,
            self.tag, int(self.ai_sellable), int(self.ai_rebuildable),
            int(self.powered), len(self.upgrades), self.spotlight,
            ",".join(ups), int(self.ai_repair), int(self.norminal)
        ]))

    def __repr__(self) -> str:
        return f'Building {self.typeof} TopCell{self.coord}'


class CAircraft:
    def __init__(self):
        self.owner = 'Neutral House'
        self.typeof = 'ORCA'
        self.health = 256
        self.coord = Array(0, 0)
        self.facing = 0
        self.mission = 'Guard'
        self.tag = None
        self.veteran = 0
        self.group = -1
        self.autocreate_no = True
        self.autocreate_yes = False

    @classmethod
    def loadair(cls, args: str):
        args = args.split(',')
        ret = cls()
        ret.owner = args[0]
        ret.typeof = args[1]
        ret.health = int(args[2])
        ret.coord = Array(map(int, args[3:5]))
        ret.facing = int(args[5])
        ret.mission = args[6]
        ret.tag = None if args[7] == 'None' else args[7]
        ret.veteran = int(args[8])
        ret.group = int(args[9])
        ret.autocreate_no = args[10] == '1'
        ret.autocreate_yes = args[11] == '1'

    def apply(self):
        return ",".join(map(str, [
            self.owner, self.typeof, self.health,
            self.coord, self.facing, self.mission,
            self.tag, self.veteran, self.group,
            int(self.autocreate_no),
            int(self.autocreate_yes)
        ]))

    def __repr__(self) -> str:
        return f'Aircraft {self.typeof} {self.coord}'
