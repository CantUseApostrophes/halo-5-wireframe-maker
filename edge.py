'''
Contains position and direction information for each edge,
as well as the cables needed to form that edge.

Created on Feb 8, 2017

@author: CantUseApostrophes
'''

import math
from cable import Cable

class Edge:
    def __init__(self, start_coords, end_coords):
        self.start = start_coords
        self.end = end_coords
        self.length = 0
        self.yaw = 0
        self.roll = 0
        self.cables = []
        self.omitted = False
        
        self.calcLength()
        self.calcAngles()
        self.getCableLengths()
        self.getCablePositions()
        
    def calcLength(self):
        self.length = math.sqrt(sum([(self.end[i]-self.start[i])**2 for i in range(3)]))
        
    def calcAngles(self):
        x, y, z = (self.end[i] - self.start[i] for i in range(3))
        
        self.yaw = math.atan2(y, x)
        if self.yaw < 0:
            self.yaw += 3*math.pi/2
        else:
            self.yaw -= math.pi/2
            
        self.roll = math.atan2(z, math.sqrt(x**2 + y**2))
        
        if self.yaw > math.pi:
            self.yaw -= math.pi*2
        elif self.yaw < -math.pi:
            self.yaw += math.pi*2
        if self.roll > math.pi:
            self.roll -= math.pi*2
        elif self.roll < -math.pi:
            self.roll += math.pi*2
            
    def getCablePositions(self):
        if len(self.cables) != 0:
            cable_start = list(self.start)
            for i in range(len(self.cables)):
                if i == len(self.cables)-1:
                    self.cables[i].reverseDirection()
                    self.cables[i].setStart(self.end)
                else:
                    self.cables[i].setStart(cable_start)
                    cable_start = self.cables[i].end
                    
    def getCableLengths(self):
        length = self.length
        cable_types = [96, 64, 48, 40, 36, 32, 20, 16, 8, 4, 0]
        threshold = 0.1
        if length <= 4-threshold:
            self.omitted = True
            return []
        while length > threshold:
            for i in range(len(cable_types)):
                if self.approxEqual(length-cable_types[i], 0, threshold):
                    length -= cable_types[i]
                    self.cables.append(Cable(cable_types[i], self.yaw, self.roll))
                    break
                elif length > cable_types[i]-threshold:
                    if len(self.cables) == 0:
                        length -= cable_types[i]
                        self.cables.append(Cable(cable_types[i], self.yaw, self.roll))
                    elif i == 0:
                        length -= cable_types[0]
                        self.cables.append(Cable(cable_types[0], self.yaw, self.roll))
                    else:
                        length -= cable_types[i-1]
                        self.cables.append(Cable(cable_types[i-1], self.yaw, self.roll))
                    break
    
    def approxEqual(self, float1, float2, threshold):
        if math.fabs(float1-float2) < threshold:
            return True
        else:
            return False
        
    def __str__(self):
        output = "Edge:"
        output += "\n- Start: (" + ", ".join([str(round(i, 1)) for i in self.start]) + ")"
        output += "\n- End: (" + ", ".join([str(round(i, 1)) for i in self.end]) + ")"
        output += "\n- Length: " + str(round(self.length, 1))
        output += "\n- Yaw: " + str(round(math.degrees(self.yaw), 2))
        output += "\n- Roll: " + str(round(math.degrees(self.roll), 2))
        output += "\n- " + str(len(self.cables)) + " cables:"
        for cable in self.cables:
            output += "\n  > " + str(cable)
        return output