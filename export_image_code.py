#importing libraries
from PyQt5 import QtGui
from PyQt5 import QtCore, QtGui, QtWidgets
from qgis.utils import iface
import time
from qgis.core import QgsProject

#defining directory to the output folder
#change according to users file path
directory = 'D:/Git_repo/Project-GP-Network-Analysis/output/'

def reorder_layers(layer, node):
    root = QgsProject.instance().layerTreeRoot()
    mylayer = root.findLayer(layer.id()) #find layer by id
    myClone = mylayer.clone() # clone the mylayer QgsLayerTreeLayer object
    parent = mylayer.parent() # get the parent. If None (layer is not in group) returns ''
    parent.insertChildNode(node, myClone) # move the cloned layer to the top (0)
    parent.removeChildNode(mylayer) # remove the original mylayer

def exportMap(filename):
    iface.mapCanvas().saveAsImage( directory + filename + ".png" ) #using saveasimage function to export current map canvas

def printImage(user_input): 
    layers = QgsProject.instance().mapLayers().values() #mapLayers().values() returns the names of all loaded layers
    for i in layers: #using a loop on all the loaded layers, reordering the layers basis user preference
        if i.name() == "Selected Safety Point":
            reorder_layers(i, 0)
        if i.name() == "Shortest Path":
            reorder_layers(i, 1)
        if i.name() == "All Safety Points":
            reorder_layers(i, 2)
        if i.name() == "Addresses nearest to the selected safety point":
            reorder_layers(i, 3)
        if i.name() == "Address points in hazard location":
            reorder_layers(i, 4)
        if i.name() == "Road Network":
            reorder_layers(i, 5)
        if i.name() == "Buffered Flood Area":
            reorder_layers(i, 5)
        if i.name() == "Study Area":
            reorder_layers(i, 5)
        else:
            pass
    #user input defines whether the image that needs to be downloaded is for the final path area or the study area
    if user_input == 1:
        layers = QgsProject.instance().mapLayersByName('Study Area') #creating a list of layers by the given name
        iface.setActiveLayer(layers[0]) #activating the first layer from the list
        iface.zoomToActiveLayer() #zooming to the full bounds of the activated layer
        iface.mapCanvas().refresh() #refreshing the map canvas to follow through with the symbological changes
        fileName = 'Study Area View' #defining the name of the output image
    
    elif user_input == 0:
        layers = QgsProject.instance().mapLayersByName('Shortest Path') #creating a list of layers by the given name
        iface.setActiveLayer(layers[0]) #activating the first layer from the list
        iface.zoomToActiveLayer() #zooming to the full bounds of the activated layer
        iface.mapCanvas().refresh() #refreshing the map canvas to follow through with the symbological changes
        layers = QgsProject.instance().mapLayersByName('Selected Safety Point') #creating a list of layers by the given name
        iface.setActiveLayer(layers[0]) #activating the first layer from the list
        lyr = iface.activeLayer()
        features = lyr.getFeatures() 
        for feat in features:
            attrs = feat.attributes() #getting all the column values from the layer
            fileName = attrs[9] #defining the name of the output image basis the NAME column from the selected safety point layer
    return fileName


print('1. For the output road image: 0\n 2. For entire study area: 1')
user_input = 0
f = printImage(user_input)
exportMap(f) #calling the exportmap function
