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

        def _getreg(_meta, _section: str, *,
                    rp_origin=True, iniptr=False):
            ti = []
            for i in self.gettypelist(_section):
                ti.append(
                    _meta(self, i) if iniptr else
                    _meta(i, source=dict(self[i].items(useraw=True)))
                )
                if rp_origin:
                    self[i] = ti[-1]
            return ti

        def _gettype(_meta, _sect: str, *,
                     raw=False, pair=False, iniptr=False):
            return (
                [_meta(*((self, i) if iniptr else (i,)))
                 for i in self.getsection(_sect).items(useraw=raw)]
                if pair else
                [_meta(*((self, i) if iniptr else (i,)))
                 for i in self.getsection(_sect).values(useraw=raw)]
            )

        self.waypoints = _gettype(meta.Waypoint, 'Waypoints',
                                  raw=True, pair=True)
        self.terrains = _gettype(meta.Terrain, 'Terrain',
                                 raw=True, pair=True)
        self.celltags = _gettype(meta.CellTag, 'CellTags',
                                 raw=True, pair=True)
        self.smudges = _gettype(meta.Smudge, 'Smudge')

        self.taskforces = _getreg(meta.TaskForce, 'TaskForces')
        self.scripts = _getreg(meta.Script, 'ScriptTypes')
        self.teams = _getreg(meta.Team, 'TeamTypes')
        self.aitriggers = _gettype(meta.AITrigger, 'AITriggerTypes',
                                   pair=True)

        self.triggers = _gettype(meta.Trigger, 'Triggers',
                                 pair=True, iniptr=True)
        self.tags = _gettype(meta.Tag, 'Tags', pair=True)
        self.localvars = _gettype(meta.LocalVar, 'VariableNames')

        self.houses = (
            {idx: f'<Player @ {chr(loc)}>'
             for idx, loc in zip(range(4475, 4483), range(65, 73))}
            if self.ismultiplay else
            _getreg(meta.House, 'Houses', iniptr=True)
        )
        self.countries = _getreg(meta.Country, 'Countries',
                                 iniptr=True)

        self.infantries = _gettype(meta.Infantry.loadinf, 'Infantry')
        self.units = _gettype(meta.Vehicle.loadunit, 'Units')
        self.buildings = _gettype(meta.Building.loadbuilding,
                                  'Structures')
        self.aircrafts = _gettype(meta.Aircraft.loadair, 'Aircrafts')

    def getfreeregid(self):
        while True:
            idx = '{0:0>8}-G'.format(str(uuid4()).split("-")[0]
                                     .upper())
            if not self.hassection(idx):
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

    def save(self, dst=None, encoding=None, withspace=False):
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
        def _regsync(_src, _sect: str):
            if len(_src) != len(self[_sect]):
                self[_sect] = {
                    str(_src.index(reg.section)): reg.section
                    for reg in _src
                }

        def _typesync(_src, _sect: str):
            if len(_src) != 0:
                self[_sect] = {
                    str(idx): obj.apply()
                    for idx, obj in zip(range(len(_src)), _src)
                }

        def _pairsync(_src, _sect: str):
            if len(_src) != 0:
                self[_sect] = {
                    pair.apply()[0]: pair.apply()[1]
                    for pair in _src
                }

        if not self.ismultiplay:
            _regsync(self.houses, "Houses")
            _regsync(self.countries, "Countries")
        _regsync(self.scripts, "ScriptTypes")
        _regsync(self.taskforces, "TaskForces")
        _regsync(self.teams, "TeamTypes")

        _typesync(self.localvars, "VariableNames")
        _typesync(self.smudges, "Smudge")
        _typesync(self.infantries, "Infantry")
        _typesync(self.units, "Units")
        _typesync(self.buildings, "Structures")
        _typesync(self.aircrafts, "Aircrafts")

        _pairsync(self.terrains, "Terrain")
        _pairsync(self.celltags, "CellTags")
        _pairsync(self.aitriggers, "AITriggerTypes")
        _pairsync(self.triggers, "Triggers")
        _pairsync(self.tags, "Tags")

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
