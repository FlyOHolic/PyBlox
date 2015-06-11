# -*- coding: utf-8 -*-
"""
Created on Sat Jun 06 12:29:34 2015

@author: Mischa
This file contains the properties of all the different tools. They can be added directly to the dictionary or as a loop below
"""

toolvars = {
256: {"speed": 15,
      "range": 4},
257: {"speed": 20,
      "range": 5},  
279: {"speed": 100,
      "range": 15,
      "damage": 35,
      "cooldown": 10,
      "knockback": 20},
280: {"damage": 20,
      "cooldown": 8,
      "knockback": 12},
281: {"damage": 25,
      "cooldown": 10,
      "knockback": 16}

}

for i in range(1000):
    if not i in toolvars:
        toolvars[i] = {}

for i in range(256):
    toolvars[i]["damage"] = 10
    toolvars[i]["cooldown"] = 5
    toolvars[i]["knockback"] = 8
for i in range(256, 279):
    toolvars[i]["damage"] = 10 + i - 255
    toolvars[i]["cooldown"] = 5
    toolvars[i]["knockback"] = 10