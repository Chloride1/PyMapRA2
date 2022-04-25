# -*- coding: utf-8 -*-
# @Time: 2022/04/22 13:23
# @Author: Chloride
"""
In YR, AI consists of these following components:

- TaskForce: which & how many guys would there be
- Script: what they act
- Team: to gather both of above, to use in anywhere.
- AI triggers: to control how do AI produce teams.
"""
from .celldata import Waypoint
from ..ccini import INISectionClass
from ..types import Array

_team_default = {
    'Max': '5',
    'Name': 'New Teamtype',
    'Group': '-1',
    'House': '<none>',
    'Script': '<none>',
    'TaskForce': '<none>',
    'Priority': '5',
    'Waypoint': 'A',
    'TechLevel': '0',
    'VeteranLevel': '1',
    'MindControlDecision': '0'
}
_team_def_no = ("Full", "Whiner", "Droppod", "Suicide", "Loadable",
                "Prebuild", "Annoyance", "IonImmune", "Recruiter",
                "Reinforce", "Aggressive", "Autocreate", "GuardSlower",
                "OnTransOnly", "AvoidThreats", "LooseRecruit",
                "IsBaseDefense", "UseTransportOrigin",
                "OnlyTargetHouseEnemy", "TransportsReturnOnUnload")
_team_def_yes = "AreTeamMembersRecruitable"


class Team(INISectionClass):
    def __init__(self, pini, index):
        super().__init__(index, src=pini[index])
        # simplify bools.
        for i in _team_def_no:
            if not self.tryparse(self.get(i), 'no'):
                self.pop(i, None)
        if self.tryparse(self.get(_team_def_yes), 'yes'):
            self.pop(_team_def_yes, None)

    def __repr__(self) -> str:
        return f'Team {self.section}'

    def __getitem__(self, item):
        if item == 'Waypoint':
            return Waypoint.toint(self.get(item))
        else:
            return self.tryparse(item, self.get(item))

    def __setitem__(self, key, value):
        if value is None:
            return super().__setitem__(key, "<none>")
        elif type(value) == int:
            if key == 'Waypoint':
                return super().__setitem__(key, Waypoint.tostring(value))
            elif (key == 'VeteranLevel') and (int(value) not in range(1, 4)):
                raise ValueError("Expect level in 1-3.")
            elif (key == 'MindControlDecision') and (int(value) not in range(6)):
                raise ValueError("Expect MC decision in 0-5.")
        return super().__setitem__(key, value)

    @classmethod
    # constructor overload
    def create(cls, pini):
        idx = pini.getfreeregid()
        pini.add(idx)
        pini[idx].update(_team_default)
        return cls(pini, idx)


class Script(INISectionClass):
    def __init__(self, pini, index):
        super().__init__(index, src=pini[index])

    def __getitem__(self, item):
        return super().__getitem__(str(item))

    def __setitem__(self, key, value):
        return super().__setitem__(str(key), value)

    def __repr__(self):
        return f'Script {self.section}'

    @classmethod
    # constructor overload
    def create(cls, pini):
        idx = pini.getfreeregid()
        pini[idx] = {"Name": "New Script"}
        return cls(pini, idx)


class TaskForce(INISectionClass):
    def __init__(self, pini, index):
        super().__init__(index, src=pini[index])

    def __getitem__(self, item):
        return super().__getitem__(str(item))

    def __setitem__(self, key, value):
        return super().__setitem__(str(key), value)

    def __repr__(self):
        return f'TaskForce {self.section}'

    @classmethod
    # constructor overload
    def create(cls, pini):
        idx = pini.getfreeregid()
        pini[idx] = {"Name": "New Taskforce"}
        return cls(pini, idx)


class AITrigger(Array):
    # this guy doesn't work well in singleplay,
    # so I don't want to declare clearly.
    def __init__(self, pair: tuple[str, str]) -> None:
        self.id = pair[0]
        self.name = pair[1].split(',')[0]  # according to aimd.ini
        super().__init__(pair[1].split(',')[1:])
        for i in range(len(self)):
            self[i] = self[i].strip()

    def apply(self):
        return self.id, (f"{self.name}," + ",".join(self))

    def __repr__(self) -> str:
        return f'AITrigger {self.id}'
