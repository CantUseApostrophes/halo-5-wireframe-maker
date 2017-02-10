'''
Contains the position and rotation information for each of the
cables (Forge props) that make up the wireframe edges.

Created on Feb 8, 2017

@author: CantUseApostrophes
'''

import math

class Cable:
    types = [4, 8, 16, 20, 32, 36, 40, 48, 64, 96]
    
    def __init__(self, length, yaw, roll):
        self.length = length
        # The yaw and roll values here are not to be trusted.
        # The edge object containing the cable object has the
        # correct rotation values.
        self.yaw = yaw
        self.roll = roll
        self.start = []
        self.end = []
        self.position = []
        self.index = Cable.types.index(self.length)
        
    def setStart(self, start):
        self.start = start
        self.calcPosition()
        
    def reverseDirection(self):
        if self.yaw >= 0:
            self.yaw += math.pi
        else:
            self.yaw -= math.pi
        self.roll *= -1
        
    def calcPosition(self):
        self.yaw += math.radians(90)
        
        self.end = [0, 0, 0]
        height = self.length*math.cos(self.roll)
        self.end[0] = height*math.cos(self.yaw)
        self.end[1] = height*math.sin(self.yaw)
        self.end[2] = self.length*math.cos(self.roll-math.radians(90))
        
        self.position = [i/2 for i in self.end]
        
        self.end = [self.end[i]+self.start[i] for i in range(3)]
        self.position = [self.position[i]+self.start[i] for i in range(3)]
        
    def __str__(self):
        output = "(" + ", ".join([str(round(i, 1)) for i in self.position]) + ")"
        output += ", Length " + str(self.length)
        return output