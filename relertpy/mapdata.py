# -*- coding: utf-8 -*-
# @Time: 2022/04/22 0:17
# @Author: Chloride
from os import PathLike, path

from .ccini import INIClass

__all__ = ["MapClass"]


class MapClass(INIClass):
    def __init__(self, pathref: PathLike | str, encoding='ansi'):
        """Initialize a MAP instance."""

        # private props
        self.__full = path.abspath(pathref)
        self.__codec = encoding

        super().__init__()
