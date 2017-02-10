'''
Loads a .obj file, parses the mesh info, and calculates edge info.

Created on Feb 8, 2017

@author: CantUseApostrophes
'''

from edge import Edge
import math
try:
    import matplotlib.pyplot as pyplot
    from mpl_toolkits.mplot3d import Axes3D  # @UnusedImport
except: pass

class Model:
    root_path = "models/"
    
    def __init__(self, filename):
        self.filename = filename
        self.vertices = []
        self.faces = []
        self.min_coords = []
        self.max_coords = []
        self.edge_indices = []
        self.edges = []
        self.numSharedEdges = 0
        self.scale_factor = 1
        
        self.parseModel()
        self.getBoundingBox()
        self.centerAtOrigin()
        self.getEdgeCoords()
        
    def parseModel(self):
        self.vertices = []
        self.faces = []
        with open(Model.root_path+self.filename+".obj") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].split()
            if len(lines[i]) > 0:
                if lines[i][0] == "f":
                    for j in range(1, len(lines[i])):
                        if lines[i][j].find("/") != -1:
                            lines[i][j] = lines[i][j][:lines[i][j].find("/")]
                    self.faces.append([int(j)-1 for j in lines[i][1:]])
                elif lines[i][0] == "v":
                    self.vertices.append([float(j) for j in [lines[i][k] for k in [1,3,2]]])
                    
    def getNumTrisAndPolys(self):
        numTris = 0
        numPolys = 0
        for face in self.faces:
            if len(face) == 3:
                numTris += 1
            elif len(face) > 3:
                numPolys += 1
        return numTris, numPolys
                    
    def getEdgeIndices(self):
        self.edge_indices = []
        self.numSharedEdges = 0
        for face in self.faces:
            for i in range(len(face)):
                segment = sorted([face[i], face[(i+1)%len(face)]])
                if not self.edgeIsShared(segment) and segment[0] != segment[1]:
                    self.edge_indices.append(segment)
                    
    def getEdgeCoords(self):
        self.getEdgeIndices()
        self.edges = []
        for indices in self.edge_indices:
            self.edges.append(Edge(self.vertices[indices[0]], self.vertices[indices[1]]))
                    
    def edgeIsShared(self, segment):
        for edge in self.edge_indices:
            if segment == edge:
                self.numSharedEdges += 1
                return True
        return False
    
    def getBoundingBox(self):
        self.min_coords = list(self.vertices[0])
        self.max_coords = list(self.vertices[0])
        for vertex in self.vertices:
            for i in range(3):
                if vertex[i] > self.max_coords[i]:
                    self.max_coords[i] = vertex[i]
                if vertex[i] < self.min_coords[i]:
                    self.min_coords[i] = vertex[i]
    
    def centerAtOrigin(self):
        for i in range(len(self.vertices)):
            self.vertices[i] = [self.vertices[i][j] - (self.max_coords[j]+self.min_coords[j])/2 for j in range(3)]
        self.getBoundingBox()
        
    def setShortestEdge(self, length):
        self.scale(length/self.getShortestEdge())
        
    def getShortestEdge(self):
        return min([edge.length for edge in self.edges])
    
    def getLongestEdge(self):
        return max([edge.length for edge in self.edges])
        
    def scale(self, scale):
        for i in range(len(self.vertices)):
            self.vertices[i] = [scale*self.vertices[i][j] for j in range(3)]
        self.scale_factor *= scale
        self.getBoundingBox()
        self.getEdgeCoords()
            
    def deleteShortEdges(self, threshold):
        edges_trimmed = []
        for edge in self.edges:
            if not edge.length < threshold:
                edges_trimmed.append(edge)
        self.edges = edges_trimmed
        
    def getNumCables(self):
        numCables = 0
        for edge in self.edges:
            numCables += len(edge.cables)
        return numCables
    
    def getNumEdgesOmitted(self):
        numOmitted = 0
        for edge in self.edges:
            numOmitted += edge.omitted
        return numOmitted
    
    def plotWireframe(self):
        try:
            fig = pyplot.figure()
            ax = fig.add_subplot(111, projection="3d")
            ax.axis("equal")
            for edge in self.edges:
                ax.plot([edge.start[0], edge.end[0]], [edge.start[1], edge.end[1]], [edge.start[2], edge.end[2]], ["black", "red"][edge.omitted])
            pyplot.show()
        except: pass
        
    def generateAhkScript(self):
        with open ("ahk_functions", "r") as funcs:
            output = funcs.read()
        for edge in self.edges:
            for cable in edge.cables:
                output += "clickPlus()\n"
                output += "checkPlusMenu()\n"
                output += "clickSpawnCable("+str(cable.index)+")\n"
                output += "clickProperties()\n"
                output += "clickPosition()\n"
                output += "clickField1(0)\n"
                output += "input("+str(round(cable.position[0], 1))+")\n"
                output += "clickField2(0)\n"
                output += "input("+str(round(cable.position[1], 1))+")\n"
                output += "clickField3(0)\n"
                output += "input("+str(round(cable.position[2], 1))+")\n"
                output += "clickArrowToRotation()\n"
                output += "clickField1(1)\n"
                output += "input("+str(round(math.degrees(edge.yaw), 2))+")\n"
                output += "clickField3(1)\n"
                output += "input("+str(round(math.degrees(edge.roll), 2))+")\n"
                output += "if (pause_var1 = 1) {\n\tBlockInput MouseMoveOff\n\tPause On\n}\n"
                output += "Sleep 500\n"
        output += "BlockInput MouseMoveOff\n"
        output += "time_elapsed := FormatSeconds((A_TickCount-StartTime)/1000)\n"
        output += "MsgBox Build time:`n%time_elapsed%\n"
        output += "ExitApp\n"
        # Sets F1 to terminate script
        output += "F1::\nBlockInput MouseMoveOff\nExitApp\nreturn\n"
        # Sets F2 to pause script when finished with current object
        output += "F2::\nPause Off\nBlockInput MouseMove\nif (pause_var1 = 0)\n\tpause_var1 := 1\nelse\n\tpause_var1 := 0\nreturn\n"
        # Sets F3 to pause script immediately
        output += "F3::\nPause Off\nBlockInput MouseMove\nif (pause_var2 = 0) {\n\tpause_var2 := 1\n\tBlockInput MouseMoveOff\n\tPause On\n}\nelse\n\tpause_var2 := 0\nreturn\n"
        f = open("ahk_scripts/build_"+self.filename+"_wireframe.ahk","w")
        f.write(output)
        f.close()
        print "\nAHK script build_"+self.filename+"_wireframe.ahk generated."
    
    def __str__(self):
        numTris, numPolys = self.getNumTrisAndPolys()
        output = "model " + self.filename + ".obj:"
        output += "\n- Vertices: " + str(len(self.vertices))
        output += "\n- Faces: " + str(len(self.faces))
        output += "\n  > Triangles: " + str(numTris)
        output += "\n  > Polygons: " + str(numPolys)
        output += "\n- Edges: " + str(len(self.edges)) + " ("+ str(self.numSharedEdges) + " shared)"
        output += "\n  > Shortest edge: " + str(round(self.getShortestEdge(), 1))
        output += "\n  > Longest edge: " + str(round(self.getLongestEdge(), 1))
        output += "\n- Cables: " + str(self.getNumCables()) +" (" + str(self.getNumEdgesOmitted()) + " edges omitted)"
        output += "\n- Dimensions:"
        output += "\n  > Width (x): " + str(round(self.max_coords[0] - self.min_coords[0], 1))
        output += "\n  > Length (y): " + str(round(self.max_coords[1] - self.min_coords[1], 1))
        output += "\n  > Height (z): " + str(round(self.max_coords[2] - self.min_coords[2], 1))
        output += "\n- Scale factor: " + str(round(self.scale_factor, 3))
        return output