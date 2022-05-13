# -*- coding: utf-8 -*-
# @Time: 2022/04/22 10:44
# @Author: Chloride
import _context

import relertpy.ccini as ini

config1 = ini.INIClass()
# config2 = ini.INIClass()

config1.load(".\\eg.ini")
print(config1['ExampleInherit']['IsCasheenBurnt'])
print(config1['ExampleInherit']['VoiceDoi'])

config1.save("..\\ego.ini")
