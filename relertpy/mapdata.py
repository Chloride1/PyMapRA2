# -*- coding: utf-8 -*-
# @Time: 2022/04/22 0:17
# @Author: Chloride
from os import PathLike, path
from uuid import uuid4

from .ccini import INIClass
from .structs import *

__all__ = ["MapClass"]


class MapClass(INIClass):
    def __init__(self, pathref: PathLike | str, encoding='ansi'):
        """Initialize a MAP instance."""

        # private props
        self.__full = path.abspath(pathref)
        self.__codec = encoding

        super().__init__()

    def getfreeregid(self):
        while True:
            idx = '{0:0>8}-G'.format(str(uuid4())
                                     .split("-")[0]
                                     .upper())
            if not self.hassection(idx):
                break
        return idx
