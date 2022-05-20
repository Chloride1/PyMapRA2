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
    def __init__(self, section, *, source=None):
        if source is None:
            source = _team_default.copy()

        super().__init__(section, **source)
        # simplify bools.
        for i in _team_def_no:
            if self.tryparse(i, self.get(i)) is False:
                del self[i]
        if self.tryparse(_team_def_yes, self.get(_team_def_yes)):
            del self[_team_def_yes]

    def __repr__(self) -> str:
        return f'Team {self.section}'

    def __getitem__(self, item):
        if item in ('Waypoint', 'TransportWaypoint'):
            return Waypoint.toint(self.get(item))
        else:
            return self.tryparse(item, self.get(item))

    def __setitem__(self, key, value):
        if value is None:
            return super().__setitem__(key, "<none>")
        elif type(value) == int:
            if key in ('Waypoint', 'TransportWaypoint'):
                return super().__setitem__(key, Waypoint.tostring(value))
            elif (key == 'VeteranLevel') and (int(value) not in range(1, 4)):
                raise ValueError("Expect level in 1-3.")
            elif (key == 'MindControlDecision') and (int(value) not in range(6)):
                raise ValueError("Expect MC decision in 0-5.")
        return super().__setitem__(key, value)


class Script(INISectionClass):
    def __init__(self, section, *, source=None):
        if source is None:
            source = {'Name': 'New Script'}
        super().__init__(section, **source)

    def __getitem__(self, item):
        return super().__getitem__(str(item))

    def __setitem__(self, key, value):
        return super().__setitem__(str(key), value)

    def __repr__(self):
        return f'Script {self.section}'


class TaskForce(INISectionClass):
    def __init__(self, section, *, source=None):
        if source is None:
            source = {"Name": "New Taskforce"}
        super().__init__(section, **source)

    def __getitem__(self, item):
        return super().__getitem__(str(item))

    def __setitem__(self, key, value):
        return super().__setitem__(str(key), value)

    def __repr__(self):
        return f'TaskForce {self.section}'


class AITrigger(Array):
    # this guy doesn't work well in singleplay,
    # so I don't want to declare clearly.
    def __init__(self, pair: tuple[str, str | Array]) -> None:
        self.id = pair[0]
        args = pair[1].split(",") if type(pair[1]) == str else pair[1]
        self.name = args[0]  # according to aimd.ini
        super().__init__(args[1:])
        for i in range(len(self)):
            self[i] = self[i].strip()

    def apply(self):
        return self.id, "%s,%s" % (self.name, ",".join(self))

    def __repr__(self) -> str:
        return f'AITrigger {self.id}'
