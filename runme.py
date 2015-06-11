# -*- coding: utf-8 -*-
'''
Created on Mon May 25 15:26:30 2015

@author: Mischa

This file contains the horrible hardcoded menu before the game starts
'''

'''external modules used'''
import Tkinter as tk
import tkMessageBox as tkmb
import os.path
import pygame

'''custom modules used'''
from game import rungame, Player
from menulogic import tkpygameconvert
import settings


#small about message showing in the about screen in the menu
about = "\n Welcome to PyBlox! \n\
This game is a game about digging, building and surviving. \n\
However, for now only 2 different blocks and 4 different tools can be obtained. \n\
More might be added in future updates.\n\n\
The keyboard controls can be found under settings --> keybinds \n\
By clicking with the left mouse button you can use a tool. \n\
Using the scroll wheel or number keys you can select a slot in the inventory. \n\
"


class Mainmenu():
    def __init__(self):
        #setting some overall menu properties
        self.menu = tk.Tk()
        self.menu.protocol("WM_DELETE_WINDOW", self.quitme)
        self.menu.geometry('{}x{}'.format(600, 400))
        self.menu.resizable(width=False, height=False)
        self.menu.wm_title("PyBlox")
        
        
        self.menunum = 0
        self.settabs = ["Player", "Graphics", "Controls", "Sound", "Game"]
        self.settab = "Graphics"
        
        self.frames = []
        self.titleframes = []
        self.importsettingsvars()
        self.runtabs()
        self.tabframes= [self.framegra, self.frameplayer, self.framectr, self.framesnd, self.framegam]
        
        self.update()   #first update
        self.menuloop() #starts loop that keeps the menu updating
        
    def update(self):
        #all menu items are removed from the screen
        for frame in self.frames + self.titleframes + self.tabframes:
            frame.pack_forget()
        #the list containing the items is reset
        self.frames = []
        
        #depending on the menu number the right menu gets displayed
        self.menu.rowconfigure(0, minsize = 100)
        self.menu.columnconfigure(8, minsize = 600)
        if self.menunum == 0:
            self.rendmain()
        elif self.menunum == 1:
            self.rendworldselect()
        elif self.menunum == 2:
            self.rendset()
        elif self.menunum == 3:
            self.renderabout()
            
    def rendmain(self):
        #Main menu frames and variables to hold the items
        self.frames.append(tk.Frame(self.menu, bd= 1, w= 600, height= 100))
        self.titleitems = []
        self.frames.append(tk.Frame(self.menu, w= 400,height=4, bd=1, relief= tk.SUNKEN))
        self.frames.append(tk.Frame(self.menu, w= 600, height= 300))
        self.buttonitems = []
        
        #Main menu items
        self.titleitems.append(tk.Label(self.frames[0], text= "PyBlox Game.", font= ("Helvetica", 24), width= 20))
        self.buttonitems.append(tk.Button(self.frames[2], text= "Play Game", width= 15, height= 2, command= lambda: self.changemenunum(1)))
        self.buttonitems.append(tk.Button(self.frames[2], text= "Settings", width= 15, height= 2, command= lambda: self.changemenunum(2)))
        self.buttonitems.append(tk.Button(self.frames[2], text= "About", width= 15, height= 2, command= lambda: self.changemenunum(3)))
        self.buttonitems.append(tk.Button(self.frames[2], text= "Exit", width= 15, height= 2, command= lambda: self.quitme()))
            
        #Drawing all items inside Frames and the Frames
        [thing.place(relx = .5, rely = .5, anchor = tk.CENTER) \
        for thing in self.titleitems]
            
        [thing.place(anchor = tk.CENTER, relx = .5, rely=.15 * count + 0.2) \
        for count, thing in enumerate(self.buttonitems)]
            
        [frame.pack(side= tk.TOP) for frame in self.frames]
        
    def rendertitle(self, title):
        #renders title for world selection, settings and about
        self.titleframes = []
        self.titleitems= []
        self.titleframes.append(tk.Frame(self.menu, bd= 1, w= 600, height= 100))
        self.titleframes.append(tk.Frame(self.menu, w= 400, height=4, bd=1, relief= tk.SUNKEN))
        self.titleitems = []
        
        self.titleitems.append(tk.Label(self.titleframes[0], text= title, font= ("Helvetica", 20), width= 20))
        self.titleitems.append(tk.Button(self.titleframes[0], text= "<-- Return", width= 15, command= lambda: self.changemenunum(0)))
        if self.menunum == 2:
            self.titleitems.append(tk.Button(self.titleframes[0], text= "Save", width= 10, command= lambda: self.savesettings()))
            self.titleitems.append(tk.Button(self.titleframes[0], text= "Reset", width= 10, command= lambda: self.resetsettings()))
            self.titleitems[2].place(x=115, rely= .7)
            self.titleitems[3].place(x=195, rely= .7)   
            
        self.titleitems[0].place(relx= .5, rely= .35, anchor= tk.CENTER)
        self.titleitems[1].place(x= 0, rely= .7)
        [frame.pack(side= tk.TOP) for frame in self.titleframes]
        
    def rendworldselect(self):
        self.rendertitle("World selection")
        self.frames.append(tk.Frame(self.menu, w= 600, height= 45))
        self.frames.append(tk.Frame(self.menu, w= 600, height= 400))
        self.buttonnewworld = tk.Button(self.frames[0], text= "New world", width= 45, height= 2, command= self.startgame)
        self.buttonnewworld.place(relx= .5, rely= .5, anchor= tk.CENTER)
        
        self.worlditems = []
        if not os.path.exists("saves"):
            os.makedirs("saves")
        
        for dir_, _, files in os.walk("saves"):
            for num, filename in enumerate(files):
                self.worlditems.append([])
                self.worlditems[num].append(tk.Label(self.frames[1], text="World " + filename[6:8], width= 10, height= 1))
                self.worlditems[num].append(tk.Button(self.frames[1], text= "Load World", width= 10, height= 1, command= lambda filename=filename: self.startgame(filename)))
                self.worlditems[num].append(tk.Button(self.frames[1], text= "Delete World", width= 10, height= 1, command= lambda filename=filename: self.deleteworld(filename)))
                if settings.game["debugmode"]:                
                    print "World " + filename[6:8]
        
        for rownum, row in enumerate(self.worlditems):
            for colnum, item in enumerate(row):
                item.place(x=80 + 80* colnum, y=35*rownum +5)
        
        [frame.pack(side= tk.TOP) for frame in self.frames]
        
    def renderabout(self):
        #renders the 'about' screen
        self.rendertitle("About")    #takes self.frames 0 and 1
        
        self.frames.append(tk.Frame(self.menu, width= 600, height = 300))
        self.about = tk.Label(self.frames[0], text= about , width= 95, height= 12, justify= "left")
        
        self.about.place(relx = .5, y= 110, anchor= tk.CENTER)
        [frame.pack(side= tk.TOP) for frame in self.frames]
        
    def rendertabs(self):
        #creates the tabs for the settings menu and makes the right on a Label insteaf of a button
        self.frames.append(tk.Frame(self.menu, width= 600, height= 50))
        self.tabitems = []
        
        for num, tab  in enumerate(self.settabs):
            if not self.settab == tab:
                self.tabitems.append(tk.Button(self.menu, text= self.settabs[num], width= 10, height= 1, command= lambda num=num: self.changetab(self.settabs[num])))
            else:
                self.tabitems.append(tk.Label(self.menu, text= self.settabs[num], width= 10, height= 1))

        [item.place(x = num*80, y=110) for num, item in enumerate(self.tabitems)]
        
        
    def rendset(self):
        #Creates settings frame and calls the right function for the open tab
        self.rendertitle("Settings")
        self.rendertabs()
        [frame.pack(side= tk.TOP) for frame in self.frames]
        
        
        if self.settab == "Graphics":
            self.framegra.pack(side= tk.TOP)
        if self.settab == "Player":
            self.frameplayer.pack(side= tk.TOP)
        if self.settab == "Controls":
            self.framectr.pack(side = tk.TOP)
        if self.settab == "Sound":
            self.framesnd.pack(side = tk.TOP)
        if self.settab == "Game":
            self.framegam.pack(side = tk.TOP)
            
    def runtabs(self):
        #executes all tabs on startup such that they are initialized
        self.tabgra()
        self.tabplayer()
        self.tabcontrols()
        self.tabsound()
        self.tabgameset()
        
    def tabgra(self):
        #Creates the content for Graphics tab in the Settings menu
        self.framegra = tk.Frame(self.menu, width= 600, height = 300)
        self.graitems = [[],[]]
        
        #Creates the labels, buttons and checkboxes and sets their values
        self.graitems[0].append(tk.Label(self.framegra, text = "Resolution: ", width = 16))
        self.graitems[0].append(tk.Entry(self.framegra, width = 12))
        self.graitems[0].append(tk.Entry(self.framegra, width = 12))
        self.graitems[1].append(tk.Label(self.framegra, text = "Fullscreen: ", width = 16))
        self.fullscreeninp = tk.IntVar()
        self.fullscreeninp.set(self.graphics["fullscreen"])
        self.graitems[1].append(tk.Checkbutton(self.framegra, variable = self.fullscreeninp))
        self.graitems[0][1].insert(0, str(self.graphics["resolution"][0]))
        self.graitems[0][2].insert(0, str(self.graphics["resolution"][1]))
        
        #places all the items inside the Frame
        for rownum, row in enumerate(self.graitems):
            for colnum, item in enumerate(row):
                item.place(x= (20 + 120* colnum) if not colnum == 2 else 220 , y= 20*rownum +5)
        
        
    def tabplayer(self):
        #Creates the content for Player tab in the Settings menu
        #Creation of main player frame and 2 sub-frames
        self.frameplayer = tk.Frame(self.menu, width= 600, height= 300)
        
        self.frameplayer1 = tk.Frame(self.frameplayer, width= 450, height= 300)
        self.frameplayer2 = tk.Frame(self.frameplayer, width= 100, height= 300)
        
        if embedpygame == True:
            #This line causes pygame to embed in the self.frampleyer2 tkinter Frame, such that you can see the player when settings it's colros
            #This also causes the main game not to open a new window when starting the game, so for now it is not used
            os.environ["SDL_WINDOWID"] = str(self.frameplayer2.winfo_id())
        
        self.menu.update()
        self.screen = pygame.display.set_mode((64,96))
        
        #for each color (excep eyecolor) a label and RGB sliders are created
        self.sliders= []
        for num1, tag in enumerate(("hair", "skin", "body", "legs", "shoes")):
            self.sliders.append([])
            self.sliders[num1].append(tk.Label(self.frameplayer1, text = tag[0].upper() + tag[1:] + ":", width = 10))
            self.sliders[num1].append(tk.Scale(self.frameplayer1, troughcolor= "red", length = 90,from_= 0, to= 254, orient= tk.HORIZONTAL))
            self.sliders[num1].append(tk.Scale(self.frameplayer1, troughcolor= "green", length = 90,from_= 0, to= 254, orient= tk.HORIZONTAL))
            self.sliders[num1].append(tk.Scale(self.frameplayer1, troughcolor= "blue", length = 90, from_= 0, to= 254, orient= tk.HORIZONTAL))
            
            #Set the start value for the slider
            for i in range(1, 4):
                self.sliders[num1][i].set(self.playercolors[tag][i-1])            
            
            #Places the sliders inside the frame
            for num2, item in enumerate(self.sliders[num1]):
                item.place(x= 20+ 100*num2, y= 40*num1)
        
        #Places the 2 frames inside the main fram.
        self.frameplayer1.place(x=0, y=0)
        self.frameplayer2.place(x=462, y=42)
        
    def tabcontrols(self):
        #Creates the content for the controls tab under settings
        self.framectr = tk.Frame(self.menu, width= 600, height= 300)
        self.framectr.bind("<Key>", self.recordkey)
        self.keybinds
        self.controlitems = []
        
        #A label and button will be created for each variable in self.keybinds (=settings.keybinds)
        for num, key in enumerate(self.keybinds):
            self.controlitems.append(tk.Label(self.framectr, text= settings.keybindnames[key][0].upper() + settings.keybindnames[key][1:], width= 15))
            self.controlitems.append(tk.Button(self.framectr, text= pygame.key.name(settings.keybinds[key]), width= 10, command= lambda num=num: self.recordbutton(num))) #clicking button runs self.recordbutton
            
        for num, item in enumerate(self.controlitems):
            item.place(x= 20+ 120* (num%4), y= 30*(num/4))  #make 4 columng: label-button-albel-button, untill all labels and buttons are palced
        
    def recordbutton(self, num):
        #when clicking one of the keybind buttons self.recordingnum is set to which button and the keyboard focus is set to framectr
        self.recordingnum = num
        self.framectr.focus_set()
        
    def recordkey(self, event):
        #This function gets called by pressing a button on the keyboard after pressing a keybind button. It removes the keyboard focus from framectr and sets the text of the button to the key pressed
        self.controlitems[self.recordingnum *2 +1].config(text= pygame.key.name(tkpygameconvert(event.keycode)))
        self.frames[0].focus_set()
        
    def tabsound(self):
        #Creates the content for the sound tab under settings
        self.framesnd = tk.Frame(self.menu, width= 600, height = 300)
        self.soundsliders = []
        #make a label and slider for each setting in settings.sound
        for num, key in enumerate(settings.sound):
            self.soundsliders.append(tk.Label(self.framesnd, text= key[0].upper() + key[1:] + "ume", width = 15))
            self.soundsliders.append(tk.Scale(self.framesnd, length = 100, from_= 0, to= 100, orient= tk.HORIZONTAL))
            self.soundsliders[num*2+1].set(settings.sound[key])

        for num, item in enumerate(self.soundsliders):
            item.place(x = 20 + 120*(num%2), y= 40*(num/2))
        
    def tabgameset(self):
        #Creates the content fo
        self.framegam = tk.Frame(self.menu, width= 600, height = 300)
        self.gamesetitems = [[], []]
        
        #Creates the labels, buttons and checkboxes and sets their values
        self.gamesetitems[0].append(tk.Label(self.framegam, text = "World size:", width = 16))
        self.gamesetitems[0].append(tk.Entry(self.framegam, width = 12))
        self.gamesetitems[0].append(tk.Entry(self.framegam, width = 12))
        self.gamesetitems[1].append(tk.Label(self.framegam, text = "Debugmode: ", width = 16))
        self.debugmode = tk.IntVar()
        self.debugmode.set(self.game["debugmode"])
        
        self.gamesetitems[1].append(tk.Checkbutton(self.framegam, variable= self.debugmode))
        self.gamesetitems[0][1].insert(0, str(self.game["worldsize"][0]))
        self.gamesetitems[0][2].insert(0, str(self.game["worldsize"][1]))
        
        #places all the items inside the Frame
        for rownum, row in enumerate(self.gamesetitems):
            for colnum, item in enumerate(row):
                item.place(x= (20 + 120* colnum) if not colnum == 2 else 220 , y= 20*rownum +5)
        
    def savelocal(self):
        #Saves the input values to variables in the instance, such that they can easilly be saved.
        if self.settab == "Graphics":
            self.graphics["resolution"] = (int(self.graitems[0][1].get()), int(self.graitems[0][2].get()))
            self.graphics["fullscreen"] = bool(self.fullscreeninp.get())
            
        if self.settab == "Player":
            for num, tag in enumerate(("hair", "skin", "body", "legs", "shoes")):
                self.playercolors[tag] = tuple([int(self.sliders[num][i].get()) for i in range(1, 4)])
                
        if self.settab == "Sound":
            for num, key in enumerate(settings.sound):
                self.sound[key] = self.soundsliders[num *2 +1].get()
                
        if self.settab == "Controls":
            for num, key in enumerate(settings.keybinds):
                self.keybinds[key] = eval("pygame.K_" + (self.controlitems[num *2 +1]["text"] if self.controlitems[num *2 +1]["text"] in list("abcdefghijklmnopqrstuvwxyz") else self.controlitems[num *2 +1]["text"].upper()))
                
        if self.settab == "Game":
            self.game["worldsize"] = (int(self.gamesetitems[0][1].get()), int(self.gamesetitems[0][2].get()))
            self.game["debugmode"] = bool(self.debugmode.get())
                
    def importsettingsvars(self):
        #sets the settings variables in the instance to the same values as the settings file
        self.playercolors = settings.playercolors
        self.graphics = settings.graphics
        self.keybinds = settings.keybinds
        self.sound = settings.sound
        self.game = settings.game
        
    def resetsettings(self):
        #Sets the imput values in the tab which as active in the settings menu back to its default values
        if self.settab == "Player":
            settings.playercolors = settings.Default.playercolors
            
            for num, tag in enumerate(("hair", "skin", "body", "legs", "shoes")):
                for i in range(1, 4):
                    self.sliders[num][i].set(settings.playercolors[tag][i-1])
                    
        elif self.settab == "Graphics":
            settings.graphics = settings.Default.graphics
            self.graitems[0][1].delete(0, tk.END)
            self.graitems[0][1].insert(0, str(settings.graphics["resolution"][0]))
            self.graitems[0][2].delete(0, tk.END)
            self.graitems[0][2].insert(0, str(settings.graphics["resolution"][1]))
            self.fullscreeninp.set(settings.graphics["fullscreen"])
            
        elif self.settab == "Controls":
            settings.keybinds = settings.Default.keybinds
            
            for num, key in enumerate(self.keybinds):
                self.controlitems[num *2 +1].config(text= str(pygame.key.name(settings.keybinds[key])))
            
        elif self.settab == "Sound":
            settings.sound = settings.Default.sound
            for num, key in enumerate(settings.sound):
                self.soundsliders[num *2 +1].set(settings.sound[key])
            
            
            for num, key in enumerate(settings.sound):
                self.soundsliders[num *2 +1].set(settings.sound[key])
            
        elif self.settab == "Game":
            settings.graphics = settings.Default.graphics
            self.gamesetitems[0][1].delete(0, tk.END)
            self.gamesetitems[0][1].insert(0, str(settings.graphics["resolution"][0]))
            self.gamesetitems[0][2].delete(0, tk.END)
            self.gamesetitems[0][2].insert(0, str(settings.graphics["resolution"][1]))
            self.debugmode.set(settings.graphics["fullscreen"])

        self.update()
            
    def savesettings(self):
        #Saves the settings in a file using the save function to settings.py
        self.savelocal()
        
        settings.playercolors = self.playercolors
        settings.graphics = self.graphics
        settings.keybinds = self.keybinds
        settings.sound = self.sound
        settings.game = self.game
        
        settings.save()
        
        tkmb.showinfo("Save", "Restarting menu to save settings.")
        self.running = False
        self.menu.destroy()
    
    def changetab(self, tab):
        #Changes the tab by clicking on a tab in the settings menu
        self.savelocal()
        self.settab = tab
        self.update()
        
    def changemenunum(self, num):
        #changes the menu number to go to another part of the menu
        self.menunum = num
        self.tab = "Player"
        self.update()
        
    def startgame(self, filename= 0):
        #runs the pygame game

        #moves the embedding of the pygame window into the tkinter, such that a new pygame as stand-alone frame can be launched
        if "SDL_WINDOWID" in os.environ:
            del os.environ["SDL_WINDOWID"]
            pygame.quit()
        self.running = False
        self.menu.destroy()
        rungame(filename)
        
    def deleteworld(self, filename):
        os.remove("saves/" + filename)
        self.update()

    def menuloop(self):
        #loop to keep the menu updating, without using the tkinter mainloop (as this will interfere with the pygame screen in the settings->player menu)
        self.running = True
        self.clock = pygame.time.Clock()
        self.menuplayer = Player()
        
        #Main loop for keeping the menu window updates, pygame style loop is used instead of tk.mainloop() because of the embedded pygame window
        while self.running:
            self.clock.tick(30)
            
            #Updating only while Player tab is active is not possible as this will crash the pygame window and thus the tkinter window
            for num, tag in enumerate(("hair", "skin", "body", "legs", "shoes")):
                self.playercolors[tag] = tuple([int(self.sliders[num][i].get()) for i in range(1, 4)])
            self.menuplayer = Player()
            
            self.screen.fill((240, 240, 240))
            self.screen.blit(pygame.transform.scale2x(self.menuplayer.lowerbody[0][0]), (0, 0))
            self.screen.blit(pygame.transform.scale2x(self.menuplayer.upperbody[0][0]), (0, 0))
            self.menu.update()
                
            if pygame.display.get_init():
                pygame.display.flip()
        
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        self.running = False
                        self.quitme()
            
    def quitme(self):
        #completely quits the game and pygame window
        global menu
        menu = False
        self.running = False
        pygame.quit()
        self.menu.destroy()
        
        
if __name__=="__main__":
    embedpygame = True  #This toggles if the player is embedded in the settings menu or seperate window, may prevent the main window from opening
                        #True--> embedded, False --> Seperate window
            
    menu = True         #Sets the variable for reopening the menu after closing the game
    root = Mainmenu()   #opens the menu for the first time
    while menu == True:
        #this loop causes te menu to reopen when the game is closed, only exit button or the cross in the menu will completely close the game
        root = Mainmenu()