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

        self.waypoints = [meta.Waypoint(wp) for wp in
                          self.getsection("Waypoints").items(useraw=True)]
        self.terrains = [meta.Terrain(t) for t in
                         self.getsection("Terrain").items(useraw=True)]
        self.celltags = [meta.CellTag(c) for c in
                         self.getsection("CellTags").items(useraw=True)]
        self.smudges = [meta.Smudge(s) for s in
                        self.getsection("Smudge").values()]
        self.taskforces = [meta.TaskForce(tf, source=self[tf]) for tf in
                           self.gettypelist("TaskForces")]
        self.scripts = [meta.Script(s, source=self[s]) for s in
                        self.gettypelist("ScriptTypes")]
        self.teams = [meta.Team(t, source=self[t]) for t in
                      self.gettypelist("TeamTypes")]
        self.aitriggers = [meta.AITrigger((idx, raw)) for idx, raw in
                           self.getsection("AITriggerTypes").items()]
        self.triggers = [meta.Trigger(self, t) for t in
                         self.getsection("Triggers").items()]
        self.tags = [meta.Tag(t) for t in
                     self.getsection("Tags").items()]
        self.localvars = [meta.LocalVar(lv) for lv in
                          self.getsection("VariableNames").values()]
        self.houses = (
            {idx: f'<Player @ {chr(loc)}>'
             for idx, loc in zip(range(4475, 4483), range(65, 73))}
            if self.ismultiplay
            else [meta.House(self, h) for h in
                  self.gettypelist("Houses")]
        )
        self.countries = [meta.Country(self, cts) for cts in
                          self.gettypelist("Countries")]
        self.infantries = [meta.Infantry.loadinf(i) for i in
                           self.getsection("Infantry").values()]
        self.units = [meta.Vehicle.loadunit(v) for v in
                      self.getsection("Units").values()]
        self.buildings = [meta.Building.loadbuilding(b) for b in
                          self.getsection("Structures").values()]
        self.aircrafts = [meta.Aircraft.loadair(a) for a in
                          self.getsection("Aircrafts").values()]

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
        return MappingProxyType(self["Maps"])

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

        # inline functions making the process l--ittle bit tidier.
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
