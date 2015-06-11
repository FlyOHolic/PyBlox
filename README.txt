The following files included with the game can be run:
	-runme.py (menu.py in older versions)--> starts the main menu, would be the normal way of launching the game
	-game.py --> directly starts the game with a new world created
	-settings.py --> resets the settings set by the user
	-worldgen.py --> shows results of parts of the world generation algorithm	
	
	
	
***INSTALLATION***
The following python modules are required to run PyBlox:
	-pygame
	-numpy
	-Tkinter (as Tkinter, with capital T)
	-tkMessageBox
	-os
	
The only installation required is to extract the zip file. After that the game can simply be started by running runme.py in python.

This game is build for x64 python 2.7 installation on Windows 8. 
It should also work on different system with python 2.7, however, the performance might be considerable less and the game is likely to run not quite as good.
Performance can be significantly increased by reducing the resolution in the main menu. The frame rate is locked at a maximum of 30FPS. With a lower frame rate the entire game will be slower.
Making the world larger will mainly influence memory usage and loading times of the game, however it does generally not have a large impact on CPU performance.
Please make the world no smaller than 2x2 chunks.

The least recommended resolution is 550x350 px (fullscreen)


***CREDITS***
This game is made by Mischa Griffioen (4377745) as assignment for '2015 Python Programming Competition AE1205'.
Everything included with this game, except for the audio is made by Mischa Griffioen.

The audio is made by:
Music: Kevin MacLeod (Anamalie)

Sound effects from opengameart.org -->
	http://opengameart.org/content/3-melee-sounds
	http://opengameart.org/content/footsteps-leather-cloth-armor
	http://opengameart.org/content/11-male-human-paindeath-sounds
	http://opengameart.org/content/items-door-fire-weapon-hits


Special thanks to the crew behind the game 'Terraria' for a lot of inspiration.