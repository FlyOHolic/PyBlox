# -*- coding: utf-8 -*-
'''
Created on Tue Apr 21 08:54:45 2015
@author: Mischa

This file contains the main parts for the Pyrraria game and is to be run when starting the game
'''

'''external modules used'''
import pygame
import numpy as np
import os.path

'''custom modules used'''
from gamelogic import Mask, Color, Rendersupport, Moving
from enemies import enemyproperties
from settings import keybinds
from graphics import Graphics
from worldgen import Worldgen
from tools import toolvars
import settings
from sound import Sound

def rungame(filename =0):
    '''function to start the game when run from the main menu
    filename can be given when a new world needs to be loaded'''
    global app
    app = Game(filename)
    app.gameloop()

class Game():
    '''Main class that handles the game, includes gameloop, initializing of other classes, etc.'''
    def __init__(self, worldfile):
        pygame.mixer.pre_init(11025, -16, 8, 2048)  #freq: 44100?
        pygame.init()
        self.screensize = settings.graphics["resolution"]
        self.fullscreen = settings.graphics["fullscreen"]
        if worldfile:
            self.savefile = worldfile
        else:
            self.checknum = 0
            self.searching = True
            for dir_, _, files in os.walk("saves"):
                while self.searching:
                    self.filename = "World_" + str(self.checknum) + ".npz"
                    if not self.filename in files:
                        self.savefile = self.filename
                        self.searching = False
                    else:
                        self.checknum += 1
                
                self.checknum +=1
                
        print "Savefile: ", self.savefile
        
        
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.screensize, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.screensize)
        
        pygame.display.set_caption("PyBlox")
#        Graphix.loadtextures()
        print worldfile
        if worldfile:
            self.savearrays = np.load("saves/" +worldfile)
            self.player = Player(self, self.savearrays["player"][()])
            self.world = World((self.savearrays["worldchunks"][()], self.savearrays["worldsize"][()], self.savearrays["yvals"][()]))
        else:
            self.player = Player(self)
            self.world = World()
            
            
        self.monsters = Enemycontainer(self, self.world, self.player)
        self.player.passinst(self.world, self.monsters)
        
        
        self.clock = pygame.time.Clock()
        
        self.rdsp = Rendersupport([i * 1024 for i in self.world.size], self.screensize)
        self.messages = []

    def close(self):
        pygame.mixer.quit()
        pygame.display.quit()
        pygame.quit()
        
    def gameloop(self):
        '''Main pygame game loop'''
        self.running = True
        pygame.mixer.music.load(Sound.music)
        pygame.mixer.music.set_volume((settings.sound["mastervol"] / 100.) * (settings.sound["musicvol"] / 100.))
        pygame.mixer.music.play(-1)
        while self.running:
            #lock maximum FPS to 30: game will be slower on underpowered computer, will not run too fast on overpowered computer.
            self.clock.tick(30)
            
            #logical updates
            self.player.update()
            self.monsters.spawn()
            for inst, enemy in self.monsters.container.items():
                enemy.update()
            
            #Background, world
            self.screen.fill(Color.sky)
            self.screen.blit(self.world.renderandreturn(self.rdsp.rar(0, self.player.x), self.rdsp.rar(1, self.player.y)), (self.rdsp.rar(2, self.player.x), self.rdsp.rar(3, self.player.y)))
            #enemies            
            for inst, enemy in self.monsters.container.items():
                self.screen.blit(enemy.image, (self.rdsp.worldpostoscreenpos((self.player.x, self.player.y), (enemy.x, enemy.y))))
            #Player            
            self.screen.blit(self.player.imagelow, (self.rdsp.rar(4, self.player.x) -4, self.rdsp.rar(5, self.player.y)))  #-4 in x dir is dur to the player image being larger than its hitbox
            self.screen.blit(self.player.imageup, (self.rdsp.rar(4, self.player.x) -4, self.rdsp.rar(5, self.player.y)))  #-4 in x dir is dur to the player image being larger than its hitbox
            
            #HUD
            self.fps = self.clock.get_fps()
            self.screen.blit(Graphix.renderhud(self.player.inventory, self.player.inventoryqty, self.player.inventoryselected, self.player.inventoryopen, self.screensize, self.fps, [self.player.health, self.player.healthmax, self.player.healthcooldowntimer]), (0,0))
            
            #messages            
            for num, msg in enumerate(self.messages):
                self.screen.blit(pygame.font.Font(None, 24).render(msg[0], 1, Color.message), self.rdsp.worldpostoscreenpos((self.player.x, self.player.y), msg[1]))
                msg[1][1] -= 4
                if msg[2] >0:
                    msg[2] -= 1
                else:
                    del self.messages[num]            
            self.update()
            
            #detection of player input
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    #movement, start
                    if event.key == keybinds["mvleft"]:
                        Moving.movex(self.player, -1)
                    if event.key == keybinds["mvright"]:
                        Moving.movex(self.player, 1)
                    if event.key == keybinds["mvjump"]:
                        Moving.jump(self.player)
                        
                    #hud, inventory toggle is not required as of this point in time, as there are less items then 1 row of inventory
                    if event.key == keybinds["invtoggle"]:
                        self.player.inventoryopen = not self.player.inventoryopen
                    if (pygame.key.name(event.key)) in [str(i) for i in range(10)]:
                        if int(pygame.key.name(event.key)) == 0:
                            self.player.inventoryselected = 9
                        else:
                            self.player.inventoryselected = int(pygame.key.name(event.key)) -1
                            
                    if event.key == pygame.K_ESCAPE:
                        self.save(self.savefile)
                        self.close()
                        self.running = False
                        break
     
                if event.type == pygame.KEYUP:
                    #movement, stop
                    if event.key == keybinds["mvleft"] and self.player.velx < 0:
                        Moving.movex(self.player, 0)
                    if event.key == keybinds["mvright"] and self.player.velx > 0:
                        Moving.movex(self.player, 0)
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #tools
                    if event.button == 1:   #LMB
                        if settings.game["debugmode"]:
                            print "Player position: ", self.player.x, self.player.y
#                        self.player.usetool(self.rdsp.mouse((self.player.x, self.player.y), pygame.mouse.get_pos()))
                        self.player.startusetool(self.rdsp)
                    #hud controls
                    if event.button == 4:   #scrollup (fwd), scroll though inventory
                        if self.player.inventoryselected < 9:
                            self.player.inventoryselected +=1
                        else:
                            self.player.inventoryselected = 0
                    if event.button == 5:   #scrolldown (bwd), scroll though inventory
                        if self.player.inventoryselected > 0:
                            self.player.inventoryselected -=1
                        else:
                            self.player.inventoryselected = 9
                            
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.player.stopusetool()
                        
                    #cross for quiting the game
                if event.type == pygame.QUIT:
                    self.save(self.savefile)
                    self.close()
                    self.running = False
                    break
                
    def update(self):
        pygame.display.update()
        
    def drawpix(self, color, pos):
        '''Function for drawing a single pixel on the screen'''
        self.screen.fill(color, (pos, (1,1)))
        
    def save(self, worldfile):
        '''Function that requests the data from other classes to save
        and saves it so a file when the player quits the game (red cross, or Escape key)'''
        self.worldsave = self.world.save()
        np.savez("saves/" + worldfile, player = self.player.save(), worldsize= self.worldsave[0], worldchunks = self.worldsave[1], yvals = self.worldsave[2])
        print "saving game"
        
    def message(self, msg, pos, time):
        self.messages.append([msg, pos, time])
        
        
class Calc:
    '''Some simple id / coordinate calculations'''
    @staticmethod
    def bliDxy(iD):     #Takes a block iD and returns x and y coordinates within a chunk
        return iD % Chunk.width, iD / Chunk.width
    
    @staticmethod
    def blxyiD(x, y):   #Takes a block x and y coords within a chunk and returns the iD of the block
        return x+ (Chunk.width * y)
        
    @staticmethod
    def chiDxy(iD):
        return iD % World.size[1], iD / World.size[1]
        
    @staticmethod
    def chxyiD(x, y):
        return y+ (World.size[1] * x)
        
        
class Graphix:        
    '''Old class that used to contain all the Graphics handeling, now moved to Graphics file. Only contains the HUD'''
    @staticmethod
    def renderhud(inventory, inventoryqty, inventoryselected, inventoryopen, windowsize, fps, playerhealth):    #Creates the heads up display surface
        '''Creates and returns HUD'''
        #in: list of 40xint, int 0-9 , bool, tuple of 2 int
        #out: Surface object
        invsurf = pygame.Surface(windowsize, pygame.SRCALPHA, 32)
        text = pygame.font.Font(None, 15).render("FPS:" + str(fps)[0:4], 1, (84, 101, 112))
        invsurf.blit(text, (20,10)) 
        
        slotsize = (40,40)
        slotcolor = (42,42,160)
        slotnumcolor = (220, 220, 220)
        slotnumcolorselected = (40, 200, 40)
        slotnumsize = 16
        slotalpha = 180
        slotoffset = (8,8)
        slotoffset0 = (20, 20)
        
        #inventory
        if not inventoryopen:
            for slot in range(10):
                    slotimg = pygame.Surface(slotsize)
                    slotimg.fill(slotcolor)
#                    if inventory[slot] < 256:
                    slotimg.blit(Graphics.toolimg(inventory[slot]), (0,0))
                    slotimg.set_alpha(slotalpha)
                    slotimg.blit(pygame.font.Font(None, slotnumsize).render(str((slot +1)if slot < 9 else 0), 1, slotnumcolor if not slot == inventoryselected else slotnumcolorselected), (2,2))
                    slotimg.blit(pygame.font.Font(None, slotnumsize).render(str(inventoryqty[slot]), 1, slotnumcolor if not slot == inventoryselected else slotnumcolorselected), (2,28))
                    invsurf.blit(slotimg, (slot * (slotsize[0] + slotoffset[0]) + slotoffset0[0], slotoffset0[1]))

        elif inventoryopen:
            for row in range(4):
                for slot in range(10):
                    slotimg = pygame.Surface(slotsize)
                    slotimg.fill(slotcolor)
                    slotimg.blit(Graphics.toolimg(inventory[slot + 10*row]), (0,0))
                    slotimg.set_alpha(slotalpha)
                    if row ==0:
                        slotimg.blit(pygame.font.Font(None, slotnumsize).render(str(slot +1), 1, slotnumcolor if not slot == inventoryselected else slotnumcolorselected), (2,2))
                    slotimg.blit(pygame.font.Font(None, slotnumsize).render(str(inventoryqty[slot +10*row]), 1, slotnumcolor if not slot == inventoryselected else slotnumcolorselected), (2,28))
                    invsurf.blit(slotimg, (slot * (slotsize[0] + slotoffset[0]) + slotoffset0[0], row * (slotsize[1] + slotoffset[1]) + slotoffset0[1]))
        
        #health hearts
        for i in range(playerhealth[1] / 20):
            if playerhealth[0] / 20:
                playerhealth[0] -=20
                invsurf.blit(Graphics.hearts[0], (windowsize[0] - 46, 20 + 32 *i))
            elif playerhealth[0] / 10:
                playerhealth[0] -=10
                invsurf.blit(Graphics.hearts[1], (windowsize[0] - 46, 20 + 32 *i))
            else:
                invsurf.blit(Graphics.hearts[2], (windowsize[0] - 46, 20 + 32 *i))
                
        return invsurf
        
        
class Player:
    '''Class for the player, handles updates, requests block detection, handles damage etc.'''
    def __init__(self, game= 0, playersave= 0):
        self.type  = "player"
        self.game = game
#        self.chunkno = 0
#        self.spawn = (240,260)    #spawn coordinates
        self.velx, self.vely, self.kbvelx, self.kbvely = 0, 0, 0, 0
        self.size = (24,48)        #size of the player sprite, used for hitbox logic etc. This cannot be changed without changing the logic in the hitbox functions!
        self.screensize = (32,48)

        self.upperbody = Graphics.loadplayerimages()[0]
        self.lowerbody = Graphics.loadplayerimages()[1]
        self.playervarsa()
        if not playersave:
            self.playervarsb_make()
            self.spawn = False
        else:
            self.playervarsb_load(playersave)
        
        #playerstatus variables
        self.walking, self.working, self.jumping, self.falling, self.knockedback = False, False, False, False, False
        self.walksound, self.worksound = False, False
        self.rect = pygame.Rect((0, 0), (40, 48))
        self.attrect = pygame.Rect((-100, -100), self.size)
        self.walkanimation = False
        self.workanimation = True
        self.dir = 0
        
    def passinst(self, world, enemies):
        '''Passes the world and enemies instances from inside the game function, is needed as player is made before world and enemies'''
        self.world = world
        self.enemies = enemies
        
        self.spx = 30
        while not self.spawn:
            if self.world.worldgen.yvals[self.spx] > (self.size[1] / 16) +3:
                if self.world.worldgen.yvals[self.spx] > self.world.worldgen.yvals[self.spx +1]:
                    self.spawn = (self.spx *16, int(self.world.worldgen.yvals[self.spx] - (self.size[1] /16)) *16)
                else:
                    self.spawn = (self.spx *16, int(self.world.worldgen.yvals[self.spx] - (self.size[1] /16) +1) *16)
            else:
                self.spx +=1
        self.x, self.y = self.spawn
        
    def playervarsa(self):
        '''Sets not saved variables'''
        self.walkspd = 4        #horizontal walk speed (pix/update)
        self.fallspd = 10.      #terminal velocity (pix/update)
        self.fallacc = 1.        #gravitational acceleration (pix/update)
        self.jumpspd = 11       #speed with which the player jumps (pix/update)
        self.fallingdamagethreshhold = 120
        self.attractdistance = 100
        self.collectdistance = 10
        self.healthmax = 100
        self.healthcooldowntimermax = self.healthcooldowntimer = 180
        self.attackcooldownmax = self.attackcooldown = 100
        self.hitsomething = False
        self.armor = 0
        self.blockprogressmax = self.blockprogress = 100
        self.blockprogressblock = [0, 0]
        self.placerange = 4 if not settings.game["debugmode"] else 15
        
        self.inventoryselected = 0               #which inventoryslot is currently selected
        self.inventoryopen = False              #to see if inventory is open or closed
    
    def playervarsb_make(self):
        '''Create variables which can also be loaded'''
        self.health = self.healthmax
        self.inventory = [0 for i in range(40)] #tools 0-255 are all different blocks, tools 256 - 4095 are all non-placeable items. last 4 numbers are quantity. give form 0b#### tttt bbbb     
        self.inventoryqty = [0 for i in range(40)]  #amount of each tool
        self.invadd(256 if not settings.game["debugmode"] else 279, 0)
        
    def playervarsb_load(self, playersave):
        '''Load variables which can be loaded'''
        self.health = playersave["health"]
        self.x = playersave["x"]
        self.y = playersave["y"]
        self.spawn = playersave["spawn"]
        self.inventory = playersave["inventory"]
        self.inventoryqty = playersave["inventoryqty"]
        
    def update(self):
        '''Updates player status, includes: movement, enemy damaging player, player damaging enemy, animations, falling, etc. '''
        Moving.gravity(self)
#        self.rect.left = self.x
#        self.rect.top = self.y
        
        '''Damage player if player is in an enemy '''
        self.inany = False
        for inst, enemy in self.enemies.container.items():
            if self.rect.colliderect(enemy.rect):
                self.inany = True
                if enemy.attackcooldown <=0:
                    Sound.effects["playerhit"].play()
                    Moving.gethit(self, enemy.damage)
                    enemy.attackcooldown = enemy.attackcooldownmax
                    if enemy.x < self.x:
                        Moving.knockback(self, enemy.knockback)
                    elif enemy.x > self.x:
                        Moving.knockback(self, -enemy.knockback)
                
        if not self.inany:
            if self.kbvelx > 0:
                self.kbvelx -=1
            elif self.kbvelx < 0:
                self.kbvelx +=1
            self.knockedback = False
            
        if self.attackcooldown > 0:
            self.attackcooldown -=5            
        
        '''Damage enemy if player attacks and hits'''
        for inst, enemy in self.enemies.container.items():
            if self.attrect.colliderect(enemy.rect) and not self.attackcooldown >0:
                Sound.effects["zombiehit"].play()
                Moving.gethit(enemy, toolvars[self.inventory[self.inventoryselected]]["damage"])
                if enemy.x < self.x:
                    Moving.knockback(enemy, -toolvars[self.inventory[self.inventoryselected]]["knockback"])
                elif enemy.x > self.x:
                    Moving.knockback(enemy, toolvars[self.inventory[self.inventoryselected]]["knockback"])
                self.hitsomething = True
                
        if self.hitsomething:
            self.attackcooldown = self.attackcooldownmax
            self.hitsomething = False
            
        self.animation()
        if self.healthcooldowntimer >0:
            self.healthcooldowntimer -= 1
        elif self.health < self.healthmax:
            self.health +=1
            self.healthcooldowntimer +=8

        Moving.blockcollision(self)
        Moving.worldleave(self)
        
        #sounds
        if self.walking and not self.walksound:
            self.walksound = True
            Sound.effects["playerstep"].play(-1)
        elif self.walksound and not self.walking:
            self.walksound = False
            Sound.effects["playerstep"].stop()
            
        #toggle through walk animation if the player is walking
        if self.walking:
            self.walkanimation = ((self.walkanimation + 1) if 5 < self.walkanimation < 19 else 6)
        else:
            self.walkanimation = 0
        
        if self.working:
            self.attrect.right = (self.x if not self.dir else self.x + 2*self.size[0] + 8)
            self.attrect.y = self.y
            self.workanimation = self.workanimation + 0.35 if 0 < self.workanimation < 4 else 0.35  #update animation
            self.mouseblockpos = self.rdsp.mouse((self.x, self.y), pygame.mouse.get_pos())
            self.mouseblockpos[0], self.mouseblockpos[1] = self.mouseblockpos[0] / 16, self.mouseblockpos[1] / 16            
            
            if 0< self.inventory[self.inventoryselected] < 256 and abs((self.x + self.size[0]/2) - self.mouseblockpos[0] * 16) < 4 * 16 and abs((self.y + self.size[1]/2) - self.mouseblockpos[1] * 16) < 4 * 16:    #place block
                if self.world.placeblock(self.mouseblockpos[0] / 64, self.mouseblockpos[1] / 64, self.mouseblockpos[0]%64, self.mouseblockpos[1]%64, self.inventory[self.inventoryselected]):
                    Sound.effects["place"].play()                    
                    self.inventoryqty[self.inventoryselected] -=1
                    self.inventory[self.inventoryselected] = self.inventory[self.inventoryselected] if self.inventoryqty[self.inventoryselected] else 0
            elif self.inventory[self.inventoryselected] < 256:
                pass        #do nothing if trying to place block out of range
                
            elif self.inventory[self.inventoryselected] < 280:  #block remove tools
                if not self.mouseblockpos == self.blockprogressblock:
                    self.blockprogressblock = self.mouseblockpos
                    self.blockprogress = self.blockprogressmax
                elif self.blockprogress > 0 and abs(((self.x + self.size[0]/2) / 16) - self.mouseblockpos[0]) < toolvars[self.inventory[self.inventoryselected]]["range"] and abs(((self.y + self.size[1]/2) / 16) - self.mouseblockpos[1]) < toolvars[self.inventory[self.inventoryselected]]["range"]:
                    self.blockprogress -= toolvars[self.inventory[self.inventoryselected]]["speed"]
                    Sound.effects["digging"].play()
                elif self.blockprogress <= 0:
                    self.invadd(self.world.removeblock(self.mouseblockpos[0] / 64, self.mouseblockpos[1] / 64, self.mouseblockpos[0]%64, self.mouseblockpos[1]%64))
                    self.blockprogress = self.blockprogressmax
            elif self.inventory[self.inventoryselected] < 300:
                Sound.effects["sword"].play()
        else:
            self.attrect.x = -100
            self.attrect.y = -100
            self.workanimation = self.workanimation + 0.35 if 0 < self.workanimation < 4 else 0 #update animation
        
        self.rect.x = self.x
        self.rect.y = self.y
                    
    def animation(self):
        '''determines which upper and lower body images to use in a frame'''
        self.imageup = self.upperbody[self.dir][int(self.workanimation) if self.workanimation > 0 else 5 if self.jumping else self.walkanimation if self.walking else 0]        
        self.imagelow = self.lowerbody[self.dir][5 if self.jumping else self.walkanimation if self.walking else 0]
            
    def invadd(self, tool, sound=1):
        '''adds given tool to the inventory to player'''
        if tool:
            if tool in self.inventory:      #see if tool already in inventory
                self.inventoryqty[self.inventory.index(tool)] +=1       #add 1 to quantity
            elif 0 in self.inventory:
                self.inventoryqty[self.inventory.index(0)] +=1          #add 1 to quantity of empty slot
                self.inventory[self.inventory.index(0)] = tool          #set slot to the added tool
        if tool and sound:
            Sound.effects["invent"].play()
            
    def startusetool(self, rdsp):
        '''sets working to true, used to determine of LMB is down'''
        self.working = True
        self.rdsp = rdsp
        
    def stopusetool(self):
        '''LMB is released, player no longer placing / removing blocks'''
        self.working = False
        
    def kill(self):
        '''Player is reset to spawn position, health is set to 100'''
        #kills ans respawns the player when dead
        print "You died!"
        Sound.effects["playerdie"].play()
        self.x = self.spawn[0]
        self.y = self.spawn[1]
        self.health = 100

    def save(self):
        '''Stores important player information in a dictionary and returns it'''
        self.playerdatadict = {
        "x": self.x,
        "y": self.y,
        "spawn": self.spawn,
        "inventory": self.inventory,
        "inventoryqty": self.inventoryqty,
        "health": self.health        
        }
        return self.playerdatadict
        

class Enemycontainer:
    '''Class which contains all enemies and updates them'''
    def __init__(self, game, world, player):
        self.game = game
        self.world = world
        self.player = player
        self.container = {}

    def spawn(self):
        if not np.random.randint(0, 80 + 20*len(self.container)):   #1/120 change of spawning enemy, chance decreases when more zombies are on the map
            self.spawnx = np.random.randint(0, self.world.size[0] * 16)
            if abs(self.spawnx *16 - self.player.x) >20 *16:
                self.spawnpos = False
                while not self.spawnpos:
                    if self.spawnx > self.world.size[0] * 64 -1:
                        breaK
                    self.newid = 0
                    while self.newid in self.container:
                        self.newid +=1
                    if self.world.worldgen.yvals[self.spawnx] > 4:
                        if self.world.worldgen.yvals[self.spawnx] < self.world.worldgen.yvals[self.spawnx+1]:
                            self.spawnpos = (self.spawnx *16, (self.world.worldgen.yvals[self.spawnx +1] *16)-48)
                            self.newid = 0
                            while self.newid in self.container:
                                self.newid +=1
                            self.container[self.newid] = Enemy("zombie", self.spawnpos, self.newid, self.kill, self.world, self.player, self.game)
                            
                        else: #self.world.worldgen.yvals[self.spawnx] > self.world.worldgen.yvals[self.spawnx]:
                            self.spawnpos = (self.spawnx *16, (self.world.worldgen.yvals[self.spawnx] *16)-48)
                            self.newid = 0
                            while self.newid in self.container:
                                self.newid +=1
                            self.container[self.newid] = Enemy("zombie", self.spawnpos, self.newid, self.kill, self.world, self.player, self.game)
                    else:
                        self.spawnx +=1

    def kill(self, inst):
        '''removes killed enemy from container and gives drop to player'''
        Sound.effects["zombiedie"].play()
        self.player.invadd(self.container[inst].drop)
        del self.container[inst]
            
        
class Enemy:
    '''One instance of this class contains one enemy and its functions / values'''
    def __init__(self, typ, pos, inst, kill, world, player, game):
        self.type = typ
        self.game = game
        self.world = world
        self.player = player
        self.x, self.y = pos[0], pos[1]
        self.velx, self.vely, self.kbvelx, self.kbvely = 0, 0, 0, 0
        self.walking, self.working, self.jumping, self.falling = False, False, False, False
        self.instance = inst
        
        self.kill = lambda: kill(self.instance) #define self.kill as lamda that runs the kill frunction of parent and passes self.instance to see which enemy to remove
        
        self.dir = 0
        self.sprite = Graphics.enemyimg("zombie")
        self.sprite = (self.sprite, pygame.transform.flip(self.sprite, True, False))
        self.size = (24,48)
        self.rect = pygame.Rect((self.x, self.y), self.size)
        self.initvars()
        
    def initvars(self):
        #Most values requested from the enemyproperties dictionary, such that multiple enemytypes are possible
        self.drop = np.random.choice(enemyproperties[self.type]["droptable"])
        self.damage = enemyproperties[self.type]["damage"]
        self.knockback = enemyproperties[self.type]["knockback"]
        self.attackcooldownmax = enemyproperties[self.type]["attackcooldown"]
        self.attackcooldown = self.attackcooldownmax
        self.walkspd = enemyproperties[self.type]["walkspeed"]        #horizontal walk speed (pix/update)
        self.fallspd = 10.      #terminal velocity (pix/update)
        self.fallacc = 1.        #gravitational acceleration (pix/update)
        self.jumpspd = enemyproperties[self.type]["jumpspeed"]       #speed with which the player jumps (pix/update)
        
        self.fallingdamagethreshhold = 120
        self.healthmax = enemyproperties[self.type]["health"]
        self.health = self.healthmax
        self.healthcooldowntimermax = enemyproperties[self.type]["regencooldown"]
        self.healthcooldowntimer = self.healthcooldowntimermax
        self.armor = enemyproperties[self.type]["armor"]
        
        
    def update(self):
        self.image = self.sprite[self.dir]
        
        if self.kbvelx > 0:
            self.kbvelx -=1
        elif self.kbvelx < 0:
            self.kbvelx +=1
        
        if self.attackcooldown >0:
            self.attackcooldown -= 1
            
        #walk towards the palyer
        if self.x < self.player.x:
            Moving.movex(self, 1)
        elif self.x > self.player.x:
            Moving.movex(self, -1)
            
        Moving.gravity(self)
        
        Moving.blockcollision(self)
        Moving.worldleave(self)
        
        self.rect.x = self.x
        self.rect.y = self.y

        
class World:
    '''Class which handles the world'''
    size = settings.game["worldsize"]
    def __init__(self, worldsave= 0):
        self.worldgen = Worldgen(self.size[0])
        if worldsave ==0:
            self.create()
        else:
            self.worldgen = Worldgen(self.size[0], worldsave[2])
            self.load(worldsave)
        
        self.surface = pygame.Surface((3072, 3072))
        [[chunk.calcnexttosamechunk() for chunk in row] for row in self.chunks]
        
    def renderandreturn(self, playerx, playery):    #grabs proper chunk surfaces and combines them into one Surface
        for x in range(2 if (playerx ==0 or playerx == -1 or playerx >= (World.size[0]-1) *1024) else 3):
            for y in range(2 if (playery ==0 or playerx == -1 or playery >= (World.size[1] -1) *1024) else 3):
                self.surface.blit(self.chunks[x + (playerx / 1024) -(0 if playerx ==0 else 1),y + (playery / 1024) -(0 if playery ==0 else 1)].surface, (x * 1024, y * 1024))
        self.surface.set_colorkey(Color.blockcolorkey)
        return self.surface

    def placeblock(self, chunkx, chunky, x, y, newtype):
        if not Mask.blocktype(self.chunks[chunkx, chunky].blocks[x][y]):
            if settings.game["debugmode"]:
                print "placement approved"
            self.chunks[chunkx, chunky].blocks[x][y] = (self.chunks[chunkx, chunky].blocks[x][y] & 0b111111110000000000000000) + (newtype << 8)
            self.chunks[chunkx, chunky].calcnexttosamearound(x, y)
            self.chunks[chunkx, chunky].updateblockgraphix(x, y)
            return True
        else:
            return False
        if settings.game["debugmode"]:
            print [item.pos for item in self.itembag.items]
            
    def removeblock(self, chunkx, chunky, x, y):
        if Mask.blocktype(self.chunks[chunkx, chunky].blocks[x][y]):
            self.removing = Mask.blocktype(self.chunks[chunkx, chunky].blocks[x][y])
            self.chunks[chunkx, chunky].blocks[x][y] = (self.chunks[chunkx, chunky].blocks[x][y] & 0b111111110000000011111111)
            self.chunks[chunkx, chunky].calcnexttosamearound(x, y)
            self.chunks[chunkx, chunky].updateblockgraphix(x, y)
            if settings.game["debugmode"]:
                print "remove approved; removing: ", self.removing
            return self.removing
        else:
            if settings.game["debugmode"]:
                print "remove denied"
            return 0
        
    def create(self):
        self.chunks = np.array([[Chunk(x, y, self, worldgen = self.worldgen) for y in range(World.size[1])]for x in range(World.size[0])])
    
    def load(self, worldsave):
        World.size = worldsave[1]
        self.chunksarray = worldsave[0]
        
        self.chunks = np.array([[Chunk(x, y, self, blocksarray = self.chunksarray[y * World.size[0] + x]) for y in range(World.size[1])] for x in range(World.size[0])])
        
    def save(self):
        self.size = np.array(World.size)
        self.chunkstosave = np.array([self.chunks[x, y].blocks for y in range(World.size[1]) for x in range(World.size[0])])
        
        return self.size, self.chunkstosave, self.worldgen.yvals
        
        
class Chunk:
    '''Class which handles one 64x64 blocks part of the world, such that we can always talk to small pieces of the world '''
    width = 64
    height = 64
    def __init__(self, x, y, world, worldgen=0, blocksarray= 0):
        self.world = world
        self.worldgen = worldgen
        print "Initializing chunk: %s out of %s" % (Calc.chxyiD(x, y)+1, self.world.size[0]*self.world.size[1])
        self.chpos = (x, y)
        self.surface = pygame.Surface((self.width * 16, self.height * 16))   #surface creation
        
        if np.any(blocksarray):
            self.load(blocksarray)
            self.calcchunkgraphics()
            print "Loading chunk data"
        else:
            self.create()
        
    def updateblockgraphix(self, blx, bly):     #updates graphics when a block changes
        self.newtex = Graphics.blocktexture((self.blocks[blx][bly] & 65280) >>8)[(self.blocks[blx][bly] & 240) >> 4]
#        self.surface.blit(self.newtex if not self.blocks[blx][bly] & 0b11110000 == 0b11110000 else pygame.transform.flip(self.newtex, np.random.randint(0, 1), np.random.randint(0, 1)), (blx * 16, bly * 16))
#        self.surface.blit(pygame.transform.flip(self.newtex, np.random.randint(0, 2), np.random.randint(0, 2)) if self.blocks[blx][bly] & 0b11110000 == 0b11110000 else self.newtex, (blx * 16, bly * 16))          #flips
        self.surface.blit(pygame.transform.flip(pygame.transform.rotate(self.newtex, np.random.randint(0, 4) *90), np.random.randint(0, 2), np.random.randint(0, 2))  if self.blocks[blx][bly] & 0b11110000 == 0b11110000 else self.newtex, (blx * 16, bly * 16))          #flips
        if settings.game["debugmode"]:        
            pygame.draw.line(self.surface, Color.red, (0,0), (0,1024))
            pygame.draw.line(self.surface, Color.red, (0,0), (1024,0))
                    
    def create(self):   #creates a block for each block location in the chunk.
        self.blocks = np.zeros((64, 64), dtype=np.int)   #zero = air
        self.blocks[self.worldgen.landscapematrix(self.chpos) == 1] = 0b000000000000000100000000    #mud
              
        for i in range(np.random.randint(1, 6)):    #min1, max6 'ore' things per chunk
            self.blocks[Worldgen.oregen((64,64),(np.random.randint(10,50), np.random.randint(30,50)), 8) == 1] = 768

    def calcchunkgraphics(self):
        for rownum, row in enumerate(self.blocks):
            for colnum, block in enumerate(row):
                self.updateblockgraphix(rownum, colnum)
           
    def calcnexttosamechunk(self):  #loops calcnexttosame over entire chunk
        '''calculates all block animations inside an entire chunk'''
        print "Calculating block animations chunk: %s out of %s" % (Calc.chxyiD(self.chpos[0], self.chpos[1])+1, self.world.size[0]*self.world.size[1])
        [self.calcnexttosame(blx, bly) for blx, col in enumerate(self.blocks) for bly, dat in enumerate(col)]
                
    def calcnexttosamearound(self, blx, bly):   #loops calcnexttosame over one block and directly touching blocks
        '''recalculates the block animations of the given block and the blocks around it, for when removing / placing blocks'''
        self.aroundlist = ((0,0), (0, -1), (1, 0), (0, 1), (-1, 0))
        [self.world.chunks[self.chpos[0] + ((blx + relpos[0]) /64) if self.chpos[0] + ((blx + relpos[0]) /64)< World.size[0] else World.size[0] -1, self.chpos[1] + ((bly + relpos[1]) /64) if self.chpos[1] + ((bly + relpos[1]) /64) < World.size[1] else World.size[1] -1].calcnexttosame((blx + relpos[0]) %64, (bly + relpos[1]) %64) for relpos in self.aroundlist]
            
    def calcnexttosame(self, blx, bly): #updates the animation of a block
        self.change = False
        for i in range(4):
            if (Mask.blocktype(self.blocks[blx, bly]) == Mask.blocktype(self.blockrelative(blx, bly, i))) != bool(self.blocks[blx, bly] & 2 ** (i+4)):
                self.blocks[blx, bly] = self.blocks[blx, bly] ^ 2 ** (i+4)
                self.updateblockgraphix(blx, bly)
        return True
            
    def blockrelative(self, blx, bly, checknum):    #supporting function for calcnexttosame
        self.nexttolist = ((0, -1), (1, 0), (0, 1), (-1, 0)) #dx, dy
        if (0 <= blx + (64 * self.chpos[0]) + self.nexttolist[checknum][0] < World.size[0] * 64) and (0 <= bly + (64 * self.chpos[1]) + self.nexttolist[checknum][1] < World.size[1] * 64):
            return self.world.chunks[self.chpos[0] + ((blx + self.nexttolist[checknum][0]) / 64)][self.chpos[1] + ((bly + self.nexttolist[checknum][1]) /64)].blocks[(blx + self.nexttolist[checknum][0]) %64][(bly + self.nexttolist[checknum][1]) %64]
        else:
            return 0
            
    def load(self, blocksfromfile):
        self.blocks = blocksfromfile

            
if __name__ == "__main__":
    '''Creates new world and starts game when run as main file'''
    rungame()
