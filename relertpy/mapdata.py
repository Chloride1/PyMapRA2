# -*- coding: utf-8 -*-
# @Time: 2022/04/22 0:17
# @Author: Chloride
from os import PathLike, path
from types import MappingProxyType
from uuid import uuid4

from . import structs as meta
from .ccini import INIClass
from .types import Bool

__all__ = ['MapClass']


class MapClass(INIClass):
    """
    RA2 (and/or YR, within mods) MAP Structure.
    """

    def __init__(self, pathref: PathLike | str, encoding='ansi'):
        """
        Initialize a MAP instance.

        :param pathref: map file (*.map, *.mpr, *.yrm) source.
        :param encoding: FA2 using ANSI, while Relert Sharp using UTF-8.
        """
        # private props
        self.__full = path.abspath(pathref)
        self.__codec = encoding

        if not path.exists(pathref):
            raise FileNotFoundError(pathref)

        super().__init__()
        self.load(pathref, encoding)

        self.waypoints = self._load_ins(meta.Waypoint, 'Waypoints',
                                        raw=True, pair=True)
        self.terrains = self._load_ins(meta.Terrain, 'Terrain',
                                       raw=True, pair=True)
        self.celltags = self._load_ins(meta.CellTag, 'CellTags',
                                       raw=True, pair=True)
        self.smudges = self._load_ins(meta.Smudge, 'Smudge', raw=True)

        self.taskforces = self._load_infos(meta.TaskForce, 'TaskForces')
        self.scripts = self._load_infos(meta.Script, 'ScriptTypes')
        self.teams = self._load_infos(meta.Team, 'TeamTypes')
        self.aitriggers = self._load_ins(meta.AITrigger, 'AITriggerTypes',
                                         pair=True)

        self.triggers = self._load_ins(meta.Trigger, 'Triggers',
                                       pair=True, iniptr=True)
        self.tags = self._load_ins(meta.Tag, 'Tags', pair=True)
        self.localvars = self._load_ins(meta.LocalVar, 'VariableNames')

        self.houses = (
            {idx: f'<Player @ {chr(loc)}>'
             for idx, loc in zip(range(4475, 4483), range(65, 73))}
            if self.ismultiplay else
            self._load_infos(meta.House, 'Houses', iniptr=True)
        )
        self.countries = self._load_infos(meta.Country, 'Countries',
                                          iniptr=True)

        self.infantries = self._load_ins(meta.Infantry.loadinf, 'Infantry')
        self.units = self._load_ins(meta.Vehicle.loadunit, 'Units')
        self.buildings = self._load_ins(meta.Building.loadbuilding,
                                        'Structures')
        self.aircrafts = self._load_ins(meta.Aircraft.loadair, 'Aircrafts')

    def _load_infos(self, constructor, section: str, *,
                    rp_origin=True, iniptr=False):
        ti = []
        for i in self.gettypelist(section):
            ti.append(constructor(self, i)
                      if iniptr else
                      constructor(i, source=self[i]))
            if rp_origin:
                self[i] = ti[-1]
        return ti

    def _load_ins(self, constructor, section: str, *,
                  raw=False, pair=False, iniptr=False):
        return (
            [constructor(*((self, i) if iniptr else (i,)))
             for i in self.getsection(section).items(useraw=raw)]
            if pair else
            [constructor(*((self, i) if iniptr else (i,)))
             for i in self.getsection(section).values(useraw=raw)]
        )

    def getfreeregid(self):
        while True:
            idx = '{0:0>8}-G'.format(str(uuid4())
                                     .split("-")[0]
                                     .upper())
            if not self.hassection(idx):
                break
        return idx

    # global settings
    @property
    def bridge_destroy(self):
        return self.getvalue('SpecialFlags',
                             'DestroyableBridges',
                             True)

    @bridge_destroy.setter
    def bridge_destroy(self, val):
        self.setvalue('SpecialFlags',
                      'DestroyableBridges',
                      Bool.tostring(val))

    @property
    def init_elite(self):
        return self.getvalue('SpecialFlags',
                             'InitialVeteran',
                             False)

    @init_elite.setter
    def init_elite(self, val):
        self.setvalue('SpecialFlags',
                      'InitialVeteran',
                      Bool.tostring(val))

    @property
    def mapdata(self):
        return MappingProxyType(self["Map"])

    @property
    def ismultiplay(self):
        return ((not self.getvalue("Basic", "Player")) or
                self.getvalue("Basic", "MultiplayerOnly", False))

    @property
    def light_changerate(self):
        # apart from RulesMD I could only preset a value
        # in vanilla YR.
        return self.getvalue('AudioVisual',
                             'AmbientChangeRate',
                             0.2)

    @light_changerate.setter
    def light_changerate(self, value):
        self.setvalue('AudioVisual',
                      'AmbientChangeRate',
                      str(float(value)))

    @property
    def light_changestep(self):
        # same as above one.
        return self.getvalue('AudioVisual',
                             'AmbientChangeStep',
                             0.2)

    @light_changestep.setter
    def light_changestep(self, value):
        self.setvalue('AudioVisual',
                      'AmbientChangeStep',
                      str(float(value)))

    def save(self, dst=None, encoding=None, withspace=True):
        """
        Save as a map file.

        :param dst: target path, overwrite the source map by default
        :param encoding: by default using the encoding when initialize
        :param withspace: shall we use spaces around '='?
        """
        dst = self.__full if dst is None else dst
        encoding = self.__codec if encoding is None else encoding

        # the sections wouldn't allow repeat values,
        # since in game it'll pick the first one among them.
        # as for keys, should be the last one.

        # inline functions making the process little tidier.
        def regsync(array, src: str):
            if len(array) != len(self[src]):
                self[src] = {
                    str(array.index(reg.section)): reg.section
                    for reg in array
                }

        def objsync(array, src: str):
            if len(array) != 0:
                self[src] = {
                    str(idx): obj.apply()
                    for idx, obj in zip(range(len(array)), array)
                }

        def objsync_pair(array, src: str):
            if len(array) != 0:
                self[src] = {
                    pair.apply()[0]: pair.apply()[1]
                    for pair in array
                }

        if not self.ismultiplay:
            regsync(self.houses, "Houses")
            regsync(self.countries, "Countries")
        regsync(self.scripts, "ScriptTypes")
        regsync(self.taskforces, "TaskForces")
        regsync(self.teams, "TeamTypes")

        objsync(self.localvars, "VariableNames")
        objsync(self.smudges, "Smudge")
        objsync(self.infantries, "Infantry")
        objsync(self.units, "Units")
        objsync(self.buildings, "Structures")
        objsync(self.aircrafts, "Aircrafts")

        objsync_pair(self.terrains, "Terrain")
        objsync_pair(self.celltags, "CellTags")
        objsync_pair(self.aitriggers, "AITriggerTypes")
        objsync_pair(self.triggers, "Triggers")
        objsync_pair(self.tags, "Tags")

        # I have to split as these are special cases = =
        if len(self.triggers) != 0:
            self['Events'] = {
                e.applyevents()[0]: e.applyevents()[1]
                for e in self.triggers
            }
            self['Actions'] = {
                a.applyactions()[0]: a.applyactions()[1]
                for a in self.triggers
            }

        super().save(dst, encoding, withspace)

    def __repr__(self):
        return self.__full
