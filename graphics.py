# -*- coding: utf-8 -*-
'''
Created on Fri May 29 16:16:54 2015

@author: Mischa

This file is dedicated to graphics functions. This includes loading sprites.
'''

'''external modules used'''
import pygame.display

'''custom modules used'''
from gamelogic import Color
import settings


class Imagefiles:
#    pygame.display.init()
    player = {"sheetsize": (32, 1000),
          "head": "graphics_files/head.png",
          "hair": "graphics_files/hair.png",
          "legs": "graphics_files/legs.png",
          "body": "graphics_files/body.png",
          "armf": "graphics_files/armf.png",
          "armb": "graphics_files/armb.png"}
          
    enemies = {"zombie": "graphics_files/zombie.png"}
    blockanimations, blockvariations, blocksize = 16, 3, (16, 16)
    blocks = {0: "graphics_files/air.png",
              1: "graphics_files/mud.png",
              3: "graphics_files/stone.png"}
              
    hearts = "graphics_files/hearts.png"
    toolpaths = {256: "pickaxe1.png",
                 257: "pickaxe2.png",
                 279: "pickaxe23.png",
                 280: "sword1.png",
                 281: "sword2.png"}



class Graphics:
    def __init__(self, invslotcolor):
        self.blocktexturedict = self.loadblocktextures()
        self.inventoryimgs = self.loadinventimgs(self.blocktexturedict, invslotcolor)
        self.enemyimgs = self.loadenemies()
        self.hearts = self.loadhearts()
                
    def blocktexture(self, blocktype):
        #takes blocktype number, returns list of all animations of that blocktype texture
        #if the blocknumber exists in self.blocktexturedict then return the entry with the blocktype as label, else return empty surface
        if blocktype in self.blocktexturedict:
            return self.blocktexturedict[blocktype]
        else:
            return tuple([pygame.Surface((16,16)) for i in range(16)])
            
    def toolimg(self, toolnum):
        #takes toolnumber returns inventory images for that tool number
        if toolnum in self.inventoryimgs:
            return self.inventoryimgs[toolnum]
        else:
            return pygame.Surface((40, 40))
            
    def enemyimg(self, enemy):
        if enemy in self.enemyimgs:
            return self.enemyimgs[enemy]
        else:
            return pygame.Surface((48, 32))
            
    @staticmethod
    def loadhearts():
        hearts = []
        for i in range(3):
            sheet = pygame.image.load(Imagefiles.hearts)
            tempsurf = pygame.Surface((30, 24))
            tempsurf.fill(Color.heartscolorkey)
            tempsurf.blit(sheet, (0,0), (32 *i, 0, 30, 24))
            tempsurf.set_colorkey(Color.heartscolorkey)
            hearts.append(tempsurf)
        return hearts
            
    @staticmethod
    def loadenemies():
        enemyimgs = {}
        for key, path in Imagefiles.enemies.items():
            enemyimgs[key] = pygame.image.load(path)
        return enemyimgs
           
    @staticmethod
    def loadplayerimages():
        #blit all sheets for the upperbody onto the upperbodysheet
        upperbodysheet = pygame.Surface(Imagefiles.player["sheetsize"])
        upperbodysheet.fill(Color.playercolorkey[-1])
        upperbodysheet.blit(Graphics.convertplayersheet("armb", settings.playercolors["body"], settings.playercolors["skin"]), (0,0))
        upperbodysheet.blit(Graphics.convertplayersheet("body", settings.playercolors["body"]), (0,0))
        upperbodysheet.blit(Graphics.convertplayersheet("head", settings.playercolors["skin"], settings.playercolors["eye1"], settings.playercolors["eye2"]), (0,0))
        upperbodysheet.blit(Graphics.convertplayersheet("hair", settings.playercolors["hair"]), (0,0))
        upperbodysheet.blit(Graphics.convertplayersheet("armf", settings.playercolors["body"], settings.playercolors["skin"]), (0,0))
        
        #split the upperbodysheet into images, make left and right version
        upperbody = [[],[]]
        for i in range(20):
            tempsurf = pygame.Surface((32,48))
            tempsurf.blit(upperbodysheet, (0,0), (0, 50*i, 32, 48))
            tempsurf.set_colorkey(Color.playercolorkey[-1])
            upperbody[0].append(tempsurf)
            upperbody[1].append(pygame.transform.flip(tempsurf, True, False))
        upperbody = tuple([tuple(lst) for lst in upperbody])   #transform list into tuple
        
        #blit all the sheets for the lowerbody onto the lowerbodysheet
        lowerbodysheet = pygame.Surface((32, 1000))
        lowerbodysheet.fill(Color.playercolorkey[-1])
        lowerbodysheet.blit(Graphics.convertplayersheet("legs", settings.playercolors["legs"], settings.playercolors["shoes"]), (0,0))
        
        #split the lwoerbodysheet into different images, make left and right
        lowerbody = [[],[]]
        for i in range(20):
            tempsurf = pygame.Surface((32,48))
            tempsurf.blit(lowerbodysheet, (0,0), (0, 50*i, 32, 48))
            tempsurf.set_colorkey(Color.playercolorkey[-1])
            lowerbody[0].append(tempsurf)
            lowerbody[1].append(pygame.transform.flip(tempsurf, True, False))
        lowerbody = tuple([tuple(lst) for lst in lowerbody])  #transform list into tuple
        
        return upperbody, lowerbody
        
    @staticmethod
    def convertplayersheet(part, *args):
        #loads player sprite and replaces max 3 colors with colors given at *args
        sheetcolored = pygame.Surface(Imagefiles.player["sheetsize"])
        sheetcolored.fill(Color.playercolorkey[-1])
        sheetcolored.blit(pygame.image.load(Imagefiles.player[part]).convert_alpha(), (0,0))
        pixarray = pygame.PixelArray(sheetcolored)
        for num, color in enumerate(args):
            pixarray.replace(Color.playercolorkey[num], color)
        sheetcolored = pixarray.surface
        sheetcolored.set_colorkey(Color.playercolorkey[-1])
        return sheetcolored
        
    @staticmethod
    def loadblocktextures():
        #loads all block textures and returns dictionary with all block textures
        blocktexturedic = {}
        #loop over all files in the iamgefiles.block variable
        for blockid, path in Imagefiles.blocks.items():
            blocktexturedic[blockid] = Graphics.blocksheetconvert(blockid)
        return blocktexturedic
    
    @staticmethod
    def blocksheetconvert(blockid):
        #loads blocktexture and converts the sheet into seperate images, returns tuple of these images
        sheet = pygame.image.load(Imagefiles.blocks[blockid])
        sheetlist = []  #begin as list to be able to mutate it
        for animationnum in range(Imagefiles.blockanimations):
            image = pygame.Surface(Imagefiles.blocksize)
            image.fill(Color.blockcolorkey)
            
            image.blit(sheet, (0,0), (18*animationnum, 0 , 16, 16))
            sheetlist.append(image)
        return tuple(sheetlist) #return as it doesnt need to be changed
            
    @staticmethod
    def loadinventimgs(blocktextures, slotcolor = (255, 255, 255)):
        #loads the images for the inventory into a dictionary
        inventimgs = {}
        for imgnum in range(600):
            tempsurf = pygame.Surface((40,40))
            tempsurf.fill(slotcolor)
            if imgnum in Imagefiles.toolpaths:
                tempsurf.set_colorkey(Color.blockcolorkey)
                tempsurf.blit(pygame.image.load("graphics_files/" + Imagefiles.toolpaths[imgnum]), (0,0))
            elif imgnum in blocktextures:
                tempsurf.set_colorkey(Color.blockcolorkey)
                tempsurf.blit(blocktextures[imgnum][0], (12,12))
            #make slot completely transparant if no slotcolor is given
            if slotcolor == (255, 255, 255):
                tempsurf.set_colorkey(slotcolor)
            inventimgs[imgnum] = tempsurf
        return inventimgs
        
        
#One instance of Graphics is needed for the entire game. Now the Graphics class' content can still be called with Graphics.$$$
Graphics = Graphics(Color.invslotcolor)