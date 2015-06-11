# -*- coding: utf-8 -*-
"""
Created on Sun Jun 07 12:03:43 2015

@author: Mischa
This file contains all music and sound used in the game
"""
'''external modules used'''
import pygame.mixer

'''custom modules used'''
import settings

pygame.mixer.init(22050, -16, 1, 4096)
class Sound:
    music = "sounds/anamalie.ogg"
    effects = {"zombiedie": pygame.mixer.Sound("sounds/monsterdie.ogg"),
               "zombiehit": pygame.mixer.Sound("sounds/monsterhit.ogg"),
                "playerhit": pygame.mixer.Sound("sounds/playerhit.ogg"),
                "playerdie": pygame.mixer.Sound("sounds/playerdie.ogg"),
                "playerstep": pygame.mixer.Sound("sounds/playerstep.ogg"),
                "digging": pygame.mixer.Sound("sounds/digging.ogg"),
                "invent": pygame.mixer.Sound("sounds/bag.ogg"),
                "sword": pygame.mixer.Sound("sounds/sword.ogg"),
                "fall": pygame.mixer.Sound("sounds/fall.ogg"),
                "place": pygame.mixer.Sound("sounds/place.ogg")}
    
    
    
    for key, sound in effects.items():
        sound.set_volume((settings.sound["mastervol"] / 100.) * (settings.sound["gamevol"] / 100.))