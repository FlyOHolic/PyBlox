# -*- coding: utf-8 -*-
'''
Created on Sat May 23 0:29:00 2015
@author: Mischa

This file contains the settings for the game
'''

'''external modules used'''
import pygame
import numpy as np
import os.path

#Path to the file where the settings are saved
settingsfile = "settings.npz"

def load():
    '''Loads settings'''
    settingsarrays = np.load(settingsfile)
    global keybinds
    global graphics
    global sound
    global game
    global playercolors
    
    keybinds = settingsarrays["keybinds"][()]
    graphics = settingsarrays["graphics"][()]
    sound = settingsarrays["sound"][()]
    game = settingsarrays["game"][()]
    playercolors = settingsarrays["playercolors"][()]

def save():
    '''Saves settings '''
    np.savez(settingsfile, keybinds = keybinds, graphics = graphics, sound = sound, game = game, playercolors = playercolors)
    print "Settings saved."

class Default:
    '''This class is a collection of Default settings to which are loaded when no settings are found or when reset is pressed'''
    keybinds =  {"mvleft": pygame.K_a, 
             "mvright": pygame.K_d,
             "mvjump": pygame.K_SPACE, 
             "invtoggle": pygame.K_TAB
             }
            
    graphics =  {"resolution": (600, 400),
                 "fullscreen": False,
                 }
                
    sound =     {"mastervol": 100,
                 "gamevol": 50,
                 "musicvol": 50
                 }
    
    game =      {"worldsize": (4, 3),
                 "debugmode": False
                }
                
    playercolors =      {"hair":    (177, 181, 140),
                         "skin":    (213, 164, 139),
                         "body":    (111, 130, 141),
                         "legs":    (44, 32, 133),
                         "shoes":   (129, 116, 89),
                         "eye1":   (47, 115, 90),
                         "eye2":   (205, 230, 221)}
      
#The displayed titles for the key binds as seen in the settings menu. (this should not be under Default!)   
keybindnames = {"mvleft": "Move left",
                    "mvright": "Move right",
                    "mvjump": "Jump",
                    "invtoggle": "Toggle inventory"}

defaultoverride = False 
 
if __name__=="__main__":
    '''When this file is main, all settings are reset to default'''
    defaultoverride = True 
    
    
#Not something I would usually do, but there are some 'global' variables in this file. This is because these are always needed, even when in game
if os.path.isfile("settings.npz") and not defaultoverride:
    load()
    print "File:settings.npz loaded"
    
else:
    print "File: settings.npz not found, using default settings"
    keybinds = Default.keybinds
    graphics = Default.graphics
    sound = Default.sound
    game = Default.game
    playercolors = Default.playercolors
    print graphics
    
if __name__=="__main__":
    '''When this file is main, all settings are reset to default'''
    save()