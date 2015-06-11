# -*- coding: utf-8 -*-
'''
Created on Thu May 21 17:33:00 2015
@author: Mischa

This file contains some logic / functions which are taken out of the main file for neatness
'''

'''external modules used'''
import numpy as np

'''custom modules used'''
from sound import Sound

class Mask():
    @staticmethod
    def blocktype(blockdata):
        return (blockdata & 0b1111111100000000) >> 8
        
class Color:
    black = (0,0,0)
    white = (255,255,255)
    red = (255,0,0)
    green = (0,255,0)
    blockcolorkey = (255,255,255)
    playercolorkey = ((0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 255))
    heartscolorkey = (0, 0, 255)
    sky = (135, 206, 255)
    invslotcolor = (42,42,160)
    message = (110, 110, 110)
    
class Rendersupport: #stands for renderplus but is kept short for readability reasons
    def __init__(self, worldsize, screensize):
        self.worldsize = worldsize
        self.screensize = screensize
    
    def rar(self, sit, player):
        if player > self.screensize[sit %2] /2 and player < self.worldsize[sit %2] - (self.screensize[sit %2] /2):
            return player if sit /2 ==0 else self.screensize[sit %2] /2 if sit /2 ==2 else (self.screensize[sit %2] / 2) - (player % 1024) - 1024
        elif player <= self.screensize[sit %2] /2:
            return 0 if (sit /2 ==0 or sit/2 == 1) else player
        elif player >= self.worldsize[sit %2] - (self.screensize[sit %2] /2):
            return -1 if sit /2 ==0 else self.screensize[sit %2] - 2048 if sit /2 ==1 else player - self.worldsize[sit %2] + self.screensize[sit %2]
    
    def mouse(self, playerpos, mousepos): #(x, y) --> player from 0,0 world, mouse from 0,0 screen.
        return [(playerpos[i] + mousepos[i] - (self.screensize[i] /2))  if (playerpos[i] > self.screensize[i] /2 and playerpos[i] < self.worldsize[i] - (self.screensize[i] /2)) else mousepos[i] if (playerpos[i] <= self.screensize[i] /2) else (self.worldsize[i] - self.screensize[i] + mousepos[i]) for i in range(2)]
    
        #return mousepos from #0,0 screen

    def worldpostoscreenpos(self, playerpos, worldpos):
        #transforms the absolute position of an object in the world to the relative position on the screen
        return [(worldpos[i] - playerpos[i] + (self.screensize[i] /2))  if (playerpos[i] > self.screensize[i] /2 and playerpos[i] < self.worldsize[i] - (self.screensize[i] /2)) else worldpos[i] if (playerpos[i] <= self.screensize[i] /2) else (worldpos[i] - self.worldsize[i] + self.screensize[i]) for i in range(2)]
        
class Moving:
    '''Class which contains staticmethods for moving objects such as the player and enemies'''
    @staticmethod
    def gravity(self):
        '''Function to make stuff fall due to gravity'''
        if self.vely < self.fallspd - self.fallacc:
            #changes the player status var falling to True s.t. we can detect fallingdamage
            if self.vely >=0.5 and not self.falling:
                self.falling=True
                self.ystartfalling = self.y
            self.vely += self.fallacc
        elif self.vely < self.fallspd:  #makes sure player doesn't fall faster than fallspd
            self.vely = self.fallspd
            
    @staticmethod
    def blockcollision(self):
        self.x += self.velx + self.kbvelx
        self.blockhits3 = Moving.inblocks(self, 3)        #player is 3 blocks high
        self.blockhits2 = Moving.inblocks(self, 2)        #check secondary hitbox of 2 blocks high for stepping onto blocks
        
        if (self.velx + self.kbvelx < 0 or self.velx + self.kbvelx > 0) and Moving.insolid(self.blockhits3) and (not Moving.insolid(self.blockhits2)) and (not self.world.chunks[self.x / (64*16)][(self.y-16) / (64*16)].blocks[(self.x /16) %64][((self.y-16) /16) %64] &100000000) and (not self.world.chunks[self.x / (64*16)][(self.y-16) / (64*16)].blocks[((self.x +16) /16) %64][((self.y-16) /16) %64] &100000000):  #step onto block
            self.y = ((int(self.y) - 16) / 16) * 16
            self.vely = 0
        elif self.velx + self.kbvelx > 0 and Moving.insolid(self.blockhits3):    #moving right
            self.x = ~(~self.x |0b1111) +8
            #this method should works as long as yout xspd is not greater than 16
            self.velx = self.kbvelx = 0
            self.walking = False
            if not self.type == "player":
                Moving.jump(self)
        elif self.velx < 0 and Moving.insolid(self.blockhits3):    #moving left
            self.x = ~(~self.x |0b1111) + 16
            self.velx = self.kbvelx = 0
            self.walking = False
            if not self.type == "player":
                Moving.jump(self)
            
        self.y += int(self.vely)
        self.blockhits = Moving.inblocks(self, 4) #also check one block under the player
        if self.vely > 0 and Moving.insolid(self.blockhits):    #Moving down
            self.y = (self.y / 16) * 16
            self.vely = 0
            self.jumping = False
            #Dealing damage if you fall from great heights
            if self.falling and self.y - self.ystartfalling > self.fallingdamagethreshhold:       #fallingdamage threshhold
                Moving.gethit(self, ((self.y - self.ystartfalling) /32)**2)
                Sound.effects["fall"].play()
                self.startfalling = self.y
            self.falling = False
        if self.vely < 0 and Moving.insolid(self.blockhits):    #Moving up
            self.y = ~(~int(self.y) |0b1111) + 16
            self.vely = 0
    
    @staticmethod
    def worldleave(self):
        if self.y < 0:      #cannot jump out of world
            self.y = 0
            self.vely = 0
        if self.y + self.size[1] +4 > self.world.size[1] * 1024: #player may not fall out of the screen.
            self.y = self.world.size[1] * 1024 - self.size[1] -4
            self.vely = 0
        if self.x < 0:
            self.x = 0
        elif self.x + self.size[0] +8 > self.world.size[0] * 1024:
            self.x = self.world.size[0] * 1024 - self.size[0] -8
            #if player is going out of the screen
                #move player back into the screen
            
    @staticmethod
    def inblocks(self, hitboxheight): #this function will require the height of the hitbox as an input. This is 3 in all cases but stapping up a block!
        '''returns the blocks in which the player is located, for collision detection'''        
        self.bls = []
        self.blspan = [2, hitboxheight]
        if self.x & 15 > 8:     #check if player spans 2 or 3 blocks
            self.blspan[0] = 3
        for self.j in range(self.blspan[1]):
            for self.i in range(self.blspan[0]):
                self.bls.append([self.world.chunks[(self.x + 16* self.i) /1024, (self.y + 16* self.j) / 1024].blocks[int(((self.x + self.i *16) %1024) /16)][int(((self.y + self.j *16) %1024) /16)], self.i, self.j])

        return self.bls
        
        #returns 2D array of the blocks in which the player is located.
        #can be used to move the player out of these blocks (instead of sprite collision detection)
        
    @staticmethod
    def insolid(blockhits): #counts how many of the input blocks are actually solid.
        return sum([1 if not block[0] & 0b100000000 ==0 else 0 for block in blockhits])
        
    @staticmethod
    def movex(self, direction): #direction is 0,-1 0r 1
        self.velx = direction * self.walkspd
        if direction:
            self.walking = True
            self.dir = (direction+1)/2
        else:
            self.walking = False

    @staticmethod
    def jump(self):
        self.jumping = True
        self.blockhits3 = Moving.inblocks(self, 4)    #blockcheck is 4 blocks high as we also want to know the block that is directly under the player
        if Moving.insolid(self.blockhits3) or self.y + self.size[1] >= self.world.size[1] * 1024:
            self.vely -= self.jumpspd
            
    @staticmethod
    def gethit(self, hit):
        '''Function that reduces the health of the player when hit. Armor helps reducing incoming damaga. 100% armor means no damage. (Armor will probably range somewhere 5-60)'''
        self.healthcooldowntimer = self.healthcooldowntimermax        
        self.health -= ((100-self.armor) * int(hit))/100
        self.game.message(str(((100-self.armor) * int(hit))/100), [self.x, self.y], 30)
        if self.health <=0:
            self.kill()
            
    @staticmethod
    def knockback(self, knockback):
        '''Player knockback velocity is set to knockback'''
        self.knockedback = True
        Moving.jump(self)
        self.kbvelx += knockback
