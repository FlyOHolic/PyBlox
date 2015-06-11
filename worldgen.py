# -*- coding: utf-8 -*-
'''
Created on Sun May 24 12:25:51 2015
@author: Mischa

This file contains the required functions and classes for generating a new world.
(terrain generation, ore generation, etc.)
'''

'''external modules used'''
import numpy as np

class Worldgen:
    def __init__(self, width, yvals=0):
        if not np.any(yvals)==0:
            self.yvals = yvals
        else:
            self.yvals = self.polygen(width)
        
    def landscapematrix(self, chpos):
        self.arr = np.zeros((64, 64))

        for colnum, col in enumerate(self.arr):
            for rownum, bl in enumerate(col):
                self.arr[colnum, rownum] = (1 if self.yvals[colnum + chpos[0] * 64] < rownum + chpos[1] * 64 else 0)
        return self.arr
                
    @staticmethod
    def polygen(width):
        x = np.arange(0 - 200, width + 200, 4)  #make boundary larger for a nicer curve near the edges of the screen
        y = np.random.random_integers(64, size= len(x))
        y -= 8      #make the landscape a nicer fit
        xused = np.arange(0, width * 64, 1)  #all actual x values present
        coeff = np.polyfit(x, y, 20)    #I have to admit, stole this from the reader, page:95
        poly = np.poly1d(coeff)         #I have to admit, stole this from the reader, page:95
        return np.polyval(poly, xused)
    
    @staticmethod
    def reversemask(array, mask):
        '''Takes a bitmask and changes the blocks around accordingly (1: Up, 2:Right, 4: Bottom, 8: Left'''
        poslist = ((0,-1),(1, 0),(0,1),(-1,0))
        index = np.where(array)
        newarray = np.zeros(array.shape, int)
        for tilenum in range(len(index[0])):
            
            mask = np.random.randint(0b0000, 0b1111)    #generates new mask for each block. Comment this line out to keep the same mask
                                                        #new masks give a 'messier' result, same mask gives simpler outlines
            for i in range(4):
                if mask & 2**i:
                    newarray[index[0][tilenum] + poslist[i][0], index[1][tilenum] + poslist[i][1]] = 1
        return newarray
    
    @staticmethod
    def oregen(size, start,  passes):
        '''Creates a numpy array of size 0, which contains 1s for where ore should be, other 0s
        start is more ore less the center
        passes is the size of the ore chunk, this should not be higher than the distance of start from the sides'''
        mapfin = np.zeros(size, int)
        mapfin[start] = 1
        mapupd = mapfin
        for i in range(passes):
            if mapupd.any():
                mapupd = Worldgen.reversemask(mapupd, np.random.randint(0b0000, 0b1111))
                mapfin = np.logical_or(mapfin, mapupd) *1
                
        return mapfin
    
    @staticmethod
    def maskoffset(mask, offset):   #input one chunk mask, output 4 for the chunk itself, right, bottom , bottomright
        '''Changes 2d array into 4 2d array of the same size, combined containing the original array, but offset with '''
        xsplit = mask.shape[0] - offset[0]
        ysplit = mask.shape[1] - offset[0]
        
        mask0 = mask[:xsplit, :ysplit]
        mask1 = mask[xsplit:, :ysplit]
        mask2 = mask[:xsplit, ysplit:]
        mask3 = mask[xsplit:, ysplit:]
        
        mask0 = np.insert(mask0, 0, np.zeros((mask.shape[0]-mask0.shape[0], mask0.shape[1])), 0)
        mask0 = np.insert(mask0, 0, np.zeros((mask.shape[1] - mask0.shape[1], mask0.shape[0])), 1)
        mask2 = np.insert(mask2, 0, np.zeros((mask.shape[0]-mask2.shape[0], mask2.shape[1])), 0)
        mask2 = np.append(mask2, np.zeros((mask2.shape[0], mask.shape[1] - mask2.shape[1])), 1)
        
        mask1 = np.append(mask1, np.zeros((mask.shape[0] - mask1.shape[0], mask1.shape[1])), 0)
        mask1 = np.insert(mask1, 0, np.zeros((mask.shape[1] - mask1.shape[1], mask1.shape[0])), 1)
        mask3 = np.append(mask3, np.zeros((mask.shape[0] - mask3.shape[0], mask3.shape[1])), 0)
        mask3 = np.append(mask3, np.zeros((mask3.shape[0], mask.shape[1] - mask3.shape[1])), 1)
        
        return mask0, mask1, mask2, mask3, mask0.shape, mask1.shape, mask2.shape, mask3.shape

if __name__ == "__main__":
    '''Demonstrator of the ore generation when this file is started'''
    running = True
    while running:
        command = raw_input("What demonstrator do you want to use (ore or terrain)? (o/t) (press Enter to quit)")
        if command == "o":
            print Worldgen.oregen((19,19), (9,9), 10)
        elif command == "t":
            import matplotlib.pyplot as plt
            width = 3
            wg = Worldgen(width)
            plt.plot(np.arange(0, width * 64, 1),wg.yvals, 'g')
            plt.axis((0, width * 64, 128, 0))
            plt.show()
            wg.landscapematrix((0,0))
        else:
            running = False