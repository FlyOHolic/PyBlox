# -*- coding: utf-8 -*-
'''
Created on Sun May 31 13:10:00 2015
@author: Mischa

This file contains a converter for tkinter keynumbers to pygame keynumbers
'''


tkpgkeydict = {\
192:96, 20:203, 16:304, 17:306, 18:308, 91:311, 220:92, 221:93, 219:91, 186:59, \
222:39, 188:44, 190:46, 191:47, 187:61, 189:45,\
45:277, 36:278, 33:280, 46:127, 35:279, 34:281,\
144:300, 111:267, 106:268, 109:269, 107:270, 110:266,\
37:276, 38:273, 39:275, 40:274\
}

def tkpygameconvert(tkkey):
    #Converts tkinter keynumber into pygame keynumber
    if tkkey >=65 and tkkey <=90:       #a-z keys
        return tkkey +32
    elif tkkey >= 112 and tkkey <=123:  #F-* keys
        return tkkey +170
    elif tkkey >= 96 and tkkey <=105:   #numlock keys
        return tkkey +169
    elif tkkey in tkpgkeydict:          #keys from tkphkeydict dictionary 
        return tkpgkeydict[tkkey]
    else:                               #all other keys are assumed to have equal numbers
        return tkkey