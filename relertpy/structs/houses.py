# -*- coding: utf-8 -*-
# @Time: 2022/04/26 21:10
# @Author: Chloride
"""
CAUTION: The following statements are JUST MY OPINION,
NOT THE TRUTH.

In RA2 (and YR, within mods), there are 'Countries',
'Houses' and 'Sides' which form a system to control
gaming process.

- 'Side':
Specifies settings of a group of countries,
like UI, EVA, etc, which is abstract.

However, it's unable to configure a side in map file,
so we just skip it.

- 'Country':
An abstract type templating how it shows, like
those buff (VeteranXX, YYMultiplier) in game.

It's NOT the one we really operate and fight.

- 'House':
An instance of 'Country'.

With houses in multiplays, it's possible to handle
several players who all choose a same country, which
is of course NOT RECOMMENDED in singleplay map development.
"""
from ..ccini import INISectionClass


class House(INISectionClass):
    def __init__(self, pini, h_name):
        super().__init__(h_name, **pini[h_name])

    def __repr__(self):
        return self.section

    @classmethod
    def create(cls, pini, h_name):
        if pini.ismultiplay:
            return None
        pini[f"{h_name} House"] = {
            'IQ': '0',
            'Edge': 'West',
            'Color': 'Gold',
            'Allies': f'{h_name} House',
            'Country': h_name,
            'Credits': '0',
            'NodeCount': '0',
            'TechLevel': '10',
            'PercentBuilt': '100',
            'PlayerControl': 'no'
        }
        return cls(pini, h_name)


class Country(INISectionClass):
    def __init__(self, pini, c_name):
        super().__init__(c_name, **pini[c_name])

    def __repr__(self):
        return self.section

    @classmethod
    # without global rules everything is difficult to get= =
    def create(cls, pini, name, parent, side):
        if pini.ismultiplay:
            return None
        pini[name] = {
            'Name': name,
            'Side': side,
            'Color': 'Gold',
            'Prefix': 'G' if side == 'GDI' else 'B',
            'Suffix': 'Allied' if side == 'GDI' else 'Soviet',
            'SmartAI': 'yes',
            'CostUnitsMult': '1',
            'ParentCountry': parent
        }
        return cls(pini, name)
