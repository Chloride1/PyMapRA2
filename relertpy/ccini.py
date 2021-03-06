# -*- coding: utf-8 -*-
# @Time: 2022/04/20 0:00
# @Author: Chloride
import re
from os import PathLike
from typing import MutableMapping

from .types import Array, Bool

__all__ = ["INIClass", "INISectionClass",
           ]


class INISectionClass(MutableMapping):
    def __init__(self, section: str, _super=None, **kwargs):
        self.section = section
        self.parent = _super
        self._map = {}
        if kwargs:
            self.update(kwargs)

    def __setitem__(self, k, v):
        self._map[k] = (Bool.tostring(v)  # to be consistent with FA2.
                        if type(v) == bool
                        else str(v))

    def __delitem__(self, v):
        del self._map[v]

    def __getitem__(self, k):
        if k in self._map:
            return self.tryparse(k, self._map[k])
        elif (isinstance(self.parent, INISectionClass)
              and k in self.parent):
            return self.parent.tryparse(k, self.parent.get(k))
        else:
            raise KeyError(k)

    def __contains__(self, item):
        return item in self._map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self):
        return iter(self._map)

    def __repr__(self):
        return f"Section {self.section}"

    def __str__(self):
        return self.section

    def tostring(self):
        _info = "[%s]" % self.section
        if self.parent:
            _info += ":[%s]" % self.parent
        return _info

    def get(self, key, default=None):
        if key in self._map:
            return self._map[key]
        elif (isinstance(self.parent, INISectionClass)
              and key in self.parent):
            return self.parent.get(key, default)
        else:
            return default

    def values(self, *, useraw=False):
        return self._map.values() if useraw else super().values()

    def items(self, *, useraw=False):
        return self._map.items() if useraw else super().items()

    def sortkeys(self, cond_expr=None):
        _items = sorted(self._map.keys(), key=cond_expr)
        _o_sect = {k: self._map[k] for k in _items}
        self._map = _o_sect

    def tryparse(self, option, fallback):
        try:
            value: str = self._map[option]
        except KeyError:
            return fallback

        if value.isdecimal():  # int
            return int(value)
        elif re.match(r"^-?\d+\.?\d+$", value):  # float
            return float(value)
        elif value.lower() in Bool.bool_like:  # bool
            return Bool.parse(value)
        elif value.lower() in ('none', '<none>'):  # NoneType
            return None
        elif re.findall(",+", value):  # Array
            return Array(i.strip() for i in re.split(",+", value))
        else:  # str itself
            return value


class INIClass:
    """C&C INI handler.

    Support the following features Ares implemented:

    - section inheritance: '[A]:[B]'
    - fast append: '+= C'
    - include sub inis: '[#include]' (NOT directly)

    """

    def __init__(self):
        """Initialize an empty INI structure."""
        self._raw: dict[str, INISectionClass] = {}

    def __getitem__(self, item):
        return self._raw[item]

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("Section name should always be str.")
        if isinstance(value, INISectionClass):
            self._raw[key] = value
        else:
            self._raw[key] = INISectionClass(key, **value)

    def __delitem__(self, key):
        del self._raw[key]

    def __len__(self):
        return len(self._raw)

    def __iter__(self):
        return iter(self._raw)

    @property
    def sections(self):
        return list(self._raw.values())

    def hassection(self, section):
        return section in self._raw

    def hasoption(self, section, option):
        if not self.hassection(section):
            return False
        else:
            return option in self[section]

    def add(self, section):
        if not self.hassection(section):
            self._raw[section] = INISectionClass(section)

    def remove(self, section):
        if not self.hassection(section):
            return
        del self._raw[section]

    def rename(self, _old, _new):
        self[_new] = INISectionClass(_new,
                                     self[_old].parent,
                                     **self[_old])
        self.remove(_old)

    def getsection(self, section):
        return self._raw.get(section,
                             INISectionClass(section))

    def getvalue(self, section, key, fallback=None):
        try:
            sect = self._raw[section]
            return fallback if not sect.get(key) else sect[key]
        except KeyError:
            return fallback

    def gettypelist(self, section, fallback=Array()):
        if not self.hassection(section):
            return fallback
        return list(self._raw[section].values(useraw=True))

    def setvalue(self, section, key, value):
        if not self.hassection(section):
            self.add(section)
        self._raw[section][key] = value

    def clear(self):
        return self._raw.clear()

    def sort(self, cond_expr=None, *, reverse=False):
        _sects = sorted(self._raw.keys(), key=cond_expr, reverse=reverse)
        _o_raw = {k: self._raw[k] for k in _sects}
        self._raw = _o_raw

    def load(self, ccinis, encoding='utf-8'):
        """
        Load C&C ini(s).

        Basically we recommend the recursive way to support [#include],
        instead of just 'os.walk' or blabla files collection.

        :param ccinis: INI file path(s), make sure the order of them.
        :param encoding: text encoding.
        """
        if isinstance(ccinis, (str, bytes)):
            ccinis = [ccinis]
        read_ok = []
        for ref in ccinis:
            try:
                with open(ref, 'r', encoding=encoding) as fp:
                    self.__fread(fp)
            except OSError:
                continue
            read_ok.append(ref)
        return read_ok

    def save(self, dst: PathLike | str, encoding='utf-8', withspace=False):
        """
        Save as a C&C ini.

        :param dst: target ini path.
        :param encoding: text encoding.
        :param withspace: shall we use spaces around '='?
        """
        _eq = ' = ' if withspace else '='

        with open(dst, 'w', encoding=encoding) as fs:
            for i in self.sections:
                fs.write(f"{i.tostring()}\n")
                for key, value in i.items(useraw=True):
                    fs.write(f"{key}{_eq}{value}\n")
                fs.write("\n")

    def __fread(self, stream):
        if not self._raw:
            sections, options = [], []
            curopt = maxopt = -1
        else:
            sections = list(self._raw.keys())
            options = list(self._raw.values())
            curopt = maxopt = len(options) - 1

        # since we just read A map when called,
        # instead of processing multiple inis
        diff = 0

        while True:
            i = stream.readline()
            if len(i) == 0:
                break
            if i[0] == '[':
                cursect = [j.strip()[1:-1] for j in i.split(':')]
                if cursect[0] in sections:
                    curopt = sections.index(cursect[0])
                else:
                    sections.append(cursect[0])
                    options.append(INISectionClass(cursect[0]))
                    maxopt += 1
                    curopt = maxopt
                # ares struct: [a]:[b]
                if len(cursect) > 1:
                    options[curopt].parent = (
                        options[sections.index(cursect[1])]
                        if cursect[1] in sections else cursect[1]
                    )
            elif '=' in i:
                j = i.split('=', 1)
                if ';' not in j[0]:
                    j[0] = j[0].strip()
                    j[1] = j[1].split(";")[0].strip()
                    # ares struct: += a
                    if j[0] == '+':
                        j[0] = f"+{diff}"
                        diff += 1
                    options[curopt].update([j])

        self._raw = dict(zip(sections, options))
        return len(sections), len(options)
