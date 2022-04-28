# -*- coding: utf-8 -*-
# @Time: 2022/04/27 19:58
# @Author: Chloride
import asyncio
import uuid
from datetime import datetime
from random import Random
from zlib import crc32

from relertpy.mapdata import MapClass as CCMap

__all__ = ['desc_go_hash', ]


# original way by secsome,
# simplified as Python doesn't have bitset.
def _barcode_text(ls=16):
    def getrandom(start=0, end=2 << 16):
        rand = Random(datetime.now().timestamp() % 100)
        dis = end - start
        return rand.randint(0, 0xff) % dis + start

    while True:
        val = getrandom()
        if val > (2 << 6):
            break
    ret = [""] * ls
    for i in range(0, 16):
        ret[i] = 'i' if (val & (1 << i)) != 0 else 'l'
    return "".join(ret)


_hashers = {  # if-...-else NO, switch case YES
    'crc32': lambda s: hex(crc32(bytes(s, 'utf-8')) & 0xFFFFFFFF)[2:],
    'guid': lambda s: str(uuid.uuid5(uuid.NAMESPACE_URL, s)),
    'barcode': lambda s: _barcode_text(len(s))
}


async def desc_go_hash(src: CCMap, mode: str):
    """
    encrypt those 'Name' in map elements.

    PS: needs 'await' when use!

    Examples:

    - crc32: '417c948d'
    - guid: 'b4bf2047-19db-4361-a26f-61d51c7e6236'
    - barcode: 'liliillillllllll'
    """

    def filter_pair(*e):
        element = [todo for i in e for todo in i]
        for i in element:
            i.name = _hashers.get(mode.lower(), str)(i.name)

    def filter_section(*e):
        element = [todo for i in e for todo in i]
        for i in element:
            i['Name'] = _hashers.get(mode.lower(), str)(i.name)

    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(
            None,
            filter_section,
            src.teams, src.scripts, src.taskforces),
        loop.run_in_executor(
            None,
            filter_pair,
            src.tags, src.triggers, src.localvars, src.aitriggers)
    ]

    await asyncio.wait(tasks)
    print("Done.")
