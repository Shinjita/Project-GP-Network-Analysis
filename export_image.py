from PyQt5 import QtGui
from PyQt5 import QtCore, QtGui, QtWidgets
from qgis.utils import iface
import time
from qgis.core import QgsProject

directory = 'D:/Git_repo/Project-GP-Network-Analysis/output/'
root = QgsProject.instance().layerTreeRoot()

def reorder_layers(layer, node):
    myalayer = root.findLayer(layer.id())
    myClone = myalayer.clone()
    parent = myalayer.parent()
    parent.insertChildNode(node, myClone)
    parent.removeChildNode(myalayer)

def exportMap(filename):
    iface.mapCanvas().saveAsImage( directory + filename + ".png" )

def printImage(user_input): 

    layers = QgsProject.instance().mapLayers().values()
    for i in layers:
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
    
    if user_input == 1:
        layers = QgsProject.instance().mapLayersByName('Study Area')
        iface.setActiveLayer(layers[0])
        iface.zoomToActiveLayer()
        iface.mapCanvas().refresh()  
        fileName = 'Study Area View'
    
    elif user_input == 0:
        layers = QgsProject.instance().mapLayersByName('Shortest Path')
        iface.setActiveLayer(layers[0])
        iface.zoomToActiveLayer()
        iface.mapCanvas().refresh()
        layers = QgsProject.instance().mapLayersByName('Selected Safety Point')
        iface.setActiveLayer(layers[0])
        lyr = iface.activeLayer()
        features = lyr.getFeatures()
        for feat in features:
            attrs = feat.attributes()
            fileName = attrs[9]
    return fileName


print('1. For the output road image: 0\n 2. For entire study area: 1')
user_input = 0
f = printImage(user_input)
exportMap(f)
