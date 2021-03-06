# -*- coding: utf-8 -*-
# @Time: 2022/04/24 10:49
# @Author: Chloride
"""
Logical components are these following items:

- Local Variable (bool -> int)

Originally it's just a bool, to help triggers decide when it runs.

A familiar example is team-trigger association, like SAPC transports
an MCV then run back.

Now with Phobos, int variables could be a great enhancement for
map designment.

- Trigger: just an 'if' structure.

You just consider when it runs (Event) and what will do (Action),
which is just like this:

if (events.satisfied()) { actions.run_foreach() }

How about 'else'? You have to use a local variable
to reverse the condition.

- Tag: a bridge connecting type instances with trigger.

You can simply control how it affects (in trigger) and
which one shall be affected (TInstance[Inf, ...].tag).
"""
from typing import Sequence


class LocalVar:
    def __init__(self, args: str | Sequence):
        if type(args) == str:
            args = args.split(',')
        self.name = args[0]
        self.val = int(args[1])  # now var type is int (secsome)

    def apply(self):
        return ",".join([self.name, str(self.val)])

    def __repr__(self):
        return f"{self.name} = {self.val}"


class Trigger:
    class Event:
        def __init__(self):
            self.id = 0
            self.params = []

        def __str__(self):
            return "{},{}".format(self.id, ",".join(self.params))

    class Action:
        def __init__(self):
            self.id = 0
            self.params = []

        def __str__(self):
            return "{},{}".format(self.id, ",".join(self.params))

    def __init__(self, pini, args: tuple[str, str | Sequence]):
        self.id = args[0]
        tmeta = args[1].split(',') if type(args[1]) == str else args[1]
        self.owner = tmeta[0]
        self.assoc = tmeta[1]
        self.name = tmeta[2]
        self.disabled = tmeta[3] == '1'
        self.easy = tmeta[4] == '1'
        self.normal = tmeta[5] == '1'
        self.hard = tmeta[6] == '1'

        self.events = self.loadevents(pini)
        self.actions = self.loadactions(pini)

    def loadevents(self, pini):
        ret = []
        # https://github.com/FrozenFog/Ra2-Map-TriggerNetwork
        sl = pini['Events'][self.id]  # .split(',')
        num = int(sl[0])
        i = 1
        while num > 0:
            e = Trigger.Event()
            e.id = int(sl[i])
            indicator = int(sl[i + 1])
            i += 1
            if indicator == 2:
                e.params = sl[i:i + 3]
                i += 3
            else:
                e.params = sl[i:i + 2]
                i += 2
            num -= 1
            ret.append(e)

        return ret

    def loadactions(self, pini):
        ret = []
        # https://github.com/FrozenFog/Ra2-Map-TriggerNetwork
        sl = pini['Actions'][self.id]  # .split(',')
        num = int(sl[0])
        i = 1
        while num > 0:
            a = Trigger.Action()
            a.id = int(sl[i])
            i += 1
            a.params = sl[i:i + 7]
            i += 7
            num -= 1
            ret.append(a)
        return ret

    def applyevents(self):
        return (self.id,
                "{},{}".format(
                    len(self.events),
                    ",".join(map(str, self.events))
                ))

    def applyactions(self):
        return (self.id,
                "{},{}".format(
                    len(self.actions),
                    ",".join(map(str, self.actions))
                ))

    def apply(self):
        return (self.id,
                "{},{},{},{},{},{},{},0".format(
                    self.owner,
                    self.assoc,
                    self.name,
                    int(self.disabled),
                    int(self.easy),
                    int(self.normal),
                    int(self.hard)
                ))

    def __repr__(self) -> str:
        return f'Trigger {self.id}'


class Tag:
    def __init__(self, args: tuple[str, str | Sequence]):
        self.id = args[0]
        param = args[1].split(',') if type(args[1]) == str else args[1]
        self.repeat = int(param[0])
        self.name = param[1]
        self.trigger = param[2]

    def apply(self):
        return self.id, ",".join(
            map(str, [self.repeat, self.name, self.trigger])
        )

    def __repr__(self) -> str:
        return f'Tag {self.id}'
