from qgis.core import QgsProcessing, QgsRasterLayer, QgsProject
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFile
import processing


urlWithParams = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0&crs=EPSG3857'
rlayer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')  

if rlayer.isValid():
    QgsProject.instance().addMapLayer(rlayer)

class Module(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('AddressPoints', 'Address Points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterString('CoordinateforSafetyPoint', 'Coordinate for Safety Point', multiLine=False, defaultValue='144.2340860050, -36.7876829996'))
        self.addParameter(QgsProcessingParameterVectorLayer('FloodArea', 'Flood Area', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('FloodBufferZonem', 'Flood Buffer Zone (m)', type=QgsProcessingParameterNumber.Double, minValue=0, defaultValue=100))
        self.addParameter(QgsProcessingParameterVectorLayer('Roadnetwork', 'Road network', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterString('SafetyPointSelectorbyName', 'Safety Point Selector by Name', multiLine=False, defaultValue='KANGAROO FLAT PRIMARY SCHOOL'))
        self.addParameter(QgsProcessingParameterVectorLayer('SafetyPoints', 'Safety Points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('StudyArea', 'Study Area', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologyFloodArea', 'Symbology - Flood Area', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologyPath', 'Symbology - Final Path', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologyRoadNetwork', 'Symbology - Road Network', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologyStudyArea', 'Symbology - Study Area', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologySafetyPoint', 'Symbology - Safety Point', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologyAlladdresses', 'Symbology - All addresses', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologyNearestAddresses', 'Symbology - Nearest Addresses', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('SymbologySelectedPoint', 'Symbology - Selected Point', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(26, model_feedback)
        results = {}
        outputs = {}

        # Fix geometries
        alg_params = {
            'INPUT': parameters['StudyArea'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract by attribute - safety point
        alg_params = {
            'FIELD': 'NAME',
            'INPUT': parameters['SafetyPoints'],
            'OPERATOR': 0,  # =
            'VALUE': parameters['SafetyPointSelectorbyName'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeSafetyPoint'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Add X/Y fields to layer
        alg_params = {
            'CRS': 'ProjectCrs',
            'INPUT': outputs['ExtractByAttributeSafetyPoint']['OUTPUT'],
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddXyFieldsToLayer'] = processing.run('native:addxyfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Load layer into project - Study Area
        alg_params = {
            'INPUT': parameters['StudyArea'],
            'NAME': 'Study Area'
        }
        outputs['LoadLayerIntoProjectStudyArea'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['FloodBufferZonem'],
            'END_CAP_STYLE': 0,  # Round
            'INPUT': parameters['FloodArea'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Load layer into project - Safety Points
        alg_params = {
            'INPUT': parameters['SafetyPoints'],
            'NAME': 'All Safety Points'
        }
        outputs['LoadLayerIntoProjectSafetyPoints'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Clip - Flood Area
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OVERLAY': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipFloodArea'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Load layer into project - Selected Safety Point
        alg_params = {
            'INPUT': outputs['AddXyFieldsToLayer']['OUTPUT'],
            'NAME': 'Selected Safety Point'
        }
        outputs['LoadLayerIntoProjectSelectedSafetyPoint'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Clip - Road
        alg_params = {
            'INPUT': parameters['Roadnetwork'],
            'OVERLAY': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipRoad'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectStudyArea']['OUTPUT'],
            'STYLE': parameters['SymbologyStudyArea']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Load layer into project - Flood Area
        alg_params = {
            'INPUT': outputs['ClipFloodArea']['OUTPUT'],
            'NAME': 'Buffered Flood Area'
        }
        outputs['LoadLayerIntoProjectFloodArea'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectSelectedSafetyPoint']['OUTPUT'],
            'STYLE': parameters['SymbologySelectedPoint']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectSafetyPoints']['OUTPUT'],
            'STYLE': parameters['SymbologySafetyPoint']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Load layer into project - Road Network
        alg_params = {
            'INPUT': outputs['ClipRoad']['OUTPUT'],
            'NAME': 'Road Network'
        }
        outputs['LoadLayerIntoProjectRoadNetwork'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Clip - Address Points
        alg_params = {
            'INPUT': parameters['AddressPoints'],
            'OVERLAY': outputs['ClipFloodArea']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ClipAddressPoints'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Distance to nearest hub (points)
        alg_params = {
            'FIELD': 'NAME',
            'HUBS': parameters['SafetyPoints'],
            'INPUT': outputs['ClipAddressPoints']['OUTPUT'],
            'UNIT': 3,  # Kilometers
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestHubPoints'] = processing.run('qgis:distancetonearesthubpoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectFloodArea']['OUTPUT'],
            'STYLE': parameters['SymbologyFloodArea']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Extract by attribute - Selected addresses for input safety hub
        alg_params = {
            'FIELD': 'HubName',
            'INPUT': outputs['DistanceToNearestHubPoints']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': parameters['SafetyPointSelectorbyName'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByAttributeSelectedAddressesForInputSafetyHub'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectRoadNetwork']['OUTPUT'],
            'STYLE': parameters['SymbologyRoadNetwork']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Load layer into project - Addresses nearest to Safety Point
        alg_params = {
            'INPUT': outputs['ExtractByAttributeSelectedAddressesForInputSafetyHub']['OUTPUT'],
            'NAME': 'Addresses nearest to the selected safety point'
        }
        outputs['LoadLayerIntoProjectAddressesNearestToSafetyPoint'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Shortest path (layer to point)
        alg_params = {
            'DEFAULT_DIRECTION': 2,  # Both directions
            'DEFAULT_SPEED': 50,
            'DIRECTION_FIELD': '',
            'END_POINT': parameters['CoordinateforSafetyPoint'],
            'INPUT': outputs['ClipRoad']['OUTPUT'],
            'SPEED_FIELD': '',
            'START_POINTS': outputs['ExtractByAttributeSelectedAddressesForInputSafetyHub']['OUTPUT'],
            'STRATEGY': 1,  # Fastest
            'TOLERANCE': 0,
            'VALUE_BACKWARD': '',
            'VALUE_BOTH': '',
            'VALUE_FORWARD': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ShortestPathLayerToPoint'] = processing.run('native:shortestpathlayertopoint', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Load layer into project - All addresses
        alg_params = {
            'INPUT': outputs['DistanceToNearestHubPoints']['OUTPUT'],
            'NAME': 'Address points in hazard location'
        }
        outputs['LoadLayerIntoProjectAllAddresses'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Load layer into project - Path
        alg_params = {
            'INPUT': outputs['ShortestPathLayerToPoint']['OUTPUT'],
            'NAME': 'Shortest Path'
        }
        outputs['LoadLayerIntoProjectPath'] = processing.run('native:loadlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectAllAddresses']['OUTPUT'],
            'STYLE': parameters['SymbologyAlladdresses']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectAddressesNearestToSafetyPoint']['OUTPUT'],
            'STYLE': parameters['SymbologyNearestAddresses']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Set layer style
        alg_params = {
            'INPUT': outputs['LoadLayerIntoProjectPath']['OUTPUT'],
            'STYLE': parameters['SymbologyPath']
        }
        outputs['SetLayerStyle'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)    
        return results

    def name(self):
        return 'Module'

    def displayName(self):
        return 'Network Analysis: Safety Point Identification'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Module()
