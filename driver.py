'''
A driver that loads a model and prints some info about it.

Created on Feb 8, 2017

@author: CantUseApostrophes
'''

from model import Model
       
def main():
    model = Model("sphere")
    model.setShortestEdge(4)
    print str(model)
    #print "\n"+str(model.edges[0])
    model.generateAhkScript()
    #model.plotWireframe()
    
if __name__ == "__main__":
    main()