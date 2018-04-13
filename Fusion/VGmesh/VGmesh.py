#Author-Chun-Yu Ke
#Description-Creates a VGmesh component.

import adsk.core, adsk.fusion, adsk.cam, traceback
import math
import time

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = 'mm'

# Command inputs
_deltaAngle = adsk.core.DropDownCommandInput.cast(None)
_outerRadius = adsk.core.ValueCommandInput.cast(None)
_innerRadius = adsk.core.ValueCommandInput.cast(None)
_numLayer = adsk.core.StringValueCommandInput.cast(None)
_memberRadius = adsk.core.ValueCommandInput.cast(None)
_meshSize = adsk.core.ValueCommandInput.cast(None)
_vesselDiameter = adsk.core.ValueCommandInput.cast(None)
_vesselHeight = adsk.core.TextBoxCommandInput.cast(None)
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('VGmeshPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('VGmeshPythonScript', 'VGmesh', 'Creates a VGmesh component', 'Resources/VGmesh') 
        
        
        # Connect to the command created event.
        onCommandCreated = VGmeshCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class VGmeshCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Verfies that a value command input has a valid expression and returns the 
# value if it does.  Otherwise it returns False.  This works around a 
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make 
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class VGmeshCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()
                
            defaultUnits = des.unitsManager.defaultLengthUnits
                
            # Determine whether to use inches or millimeters as the intial default.
            global _units
            _units = 'mm'
            
            deltaAngle = '30 deg'
            deltaAngleAttrib = des.attributes.itemByName('VGmesh', 'deltaAngle')
            if deltaAngleAttrib:
                deltaAngle = deltaAngleAttrib.value

            outerRadius = '0.0745'
            outerRadiusAttrib = des.attributes.itemByName('VGmesh', 'outerRadius')
            if outerRadiusAttrib:
                outerRadius = outerRadiusAttrib.value

            innerRadius = '0.0395'
            innerRadiusAttrib = des.attributes.itemByName('VGmesh', 'innerRadius')
            if innerRadiusAttrib:
                innerRadius = innerRadiusAttrib.value

            numLayer = '2'            
            numLayerAttrib = des.attributes.itemByName('VGmesh', 'numLayer')
            if numLayerAttrib:
                numLayer = numLayerAttrib.value

            memberRadius = '0.0025'
            memberRadiusAttrib = des.attributes.itemByName('VGmesh', 'memberRadius')
            if memberRadiusAttrib:
                memberRadius = memberRadiusAttrib.value

            meshSize = '0.0100'
            meshSizeAttrib = des.attributes.itemByName('VGmesh', 'meshSize')
            if meshSizeAttrib:
                meshSize = meshSizeAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
            global _deltaAngle, _outerRadius, _innerRadius, _numLayer, _memberRadius, _meshSize, _vesselDiameter, _vesselHeight, _errMessage #, _imgInputEnglish, _imgInputMetric

            # Define the command dialog.
            # _imgInputEnglish = inputs.addImageCommandInput('VGmeshImageEnglish', '', 'Resources/VGmeshEnglish.png')
            # _imgInputEnglish.isFullWidth = True

            # _imgInputMetric = inputs.addImageCommandInput('VGmeshImageMetric', '', 'Resources/VGmeshMetric.png')
            # _imgInputMetric.isFullWidth = True     

            _outerRadius = inputs.addValueInput('outerRadius', 'Outer Radius', _units, adsk.core.ValueInput.createByReal(float(outerRadius)))
            _innerRadius = inputs.addValueInput('innerRadius', 'Inner Radius', _units, adsk.core.ValueInput.createByReal(float(innerRadius)))

            _memberRadius = inputs.addValueInput('memberRadius', 'Member Radius', _units, adsk.core.ValueInput.createByReal(float(memberRadius)))

            _meshSize = inputs.addValueInput('meshSize', 'Mesh Size', _units, adsk.core.ValueInput.createByReal(float(meshSize)))

            
            _deltaAngle = inputs.addDropDownCommandInput('deltaAngle', 'Delta Angle', adsk.core.DropDownStyles.TextListDropDownStyle)
            if deltaAngle == '15 deg':
                _deltaAngle.listItems.add('15 deg', True)
            else:
                _deltaAngle.listItems.add('15 deg', False)

            if deltaAngle == '30 deg':
                _deltaAngle.listItems.add('30 deg', True)
            else:
                _deltaAngle.listItems.add('30 deg', False)

            if deltaAngle == '45 deg':
                _deltaAngle.listItems.add('45 deg', True)
            else:
                _deltaAngle.listItems.add('45 deg', False)
                
            _numLayer = inputs.addStringValueInput('numLayer', 'Number of Layers', numLayer)     
            _vesselDiameter = inputs.addTextBoxCommandInput('vesselDiameter', 'Vessel Diameter', '', 1, True)

            _vesselHeight = inputs.addTextBoxCommandInput('vesselHeight', 'Vessel Height', '', 1, True)
            
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True
            
            # Connect to the command related events.
            onExecute = VGmeshCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)        
            
            onInputChanged = VGmeshCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)     
            
            onValidateInputs = VGmeshCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)

            onDestroy = VGmeshCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class VGmeshCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            
            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            attribs = des.attributes
            attribs.add('VGmesh', 'outerRadius', str(_outerRadius.value))
            attribs.add('VGmesh', 'innerRadius', str(_innerRadius.value))
            attribs.add('VGmesh', 'memberRadius', str(_memberRadius.value))
            attribs.add('VGmesh', 'meshSize', str(_meshSize.value))
            attribs.add('VGmesh', 'deltaAngle', _deltaAngle.selectedItem.name)
            attribs.add('VGmesh', 'numLayer', str(_numLayer.value))

            # Get the current values.
            if _deltaAngle.selectedItem.name == '15 deg':
                deltaAngle = 15.0 * (math.pi/180)
            elif _deltaAngle.selectedItem.name == '30 deg':
                deltaAngle = 30.0 * (math.pi/180)
            elif _deltaAngle.selectedItem.name == '45 deg':
                deltaAngle = 45.0 * (math.pi/180)

            numLayer = int(_numLayer.value)
            memberRadius = _memberRadius.value
            meshSize = _meshSize.value
            outerRadius = _outerRadius.value
            innerRadius = _innerRadius.value

            # Create the gear.
            VGmeshComp = drawVGmesh(des, outerRadius, innerRadius, numLayer, meshSize, memberRadius, deltaAngle)
            
            if VGmeshComp:
                desc = 'VGmesh; Outer Radius: ' + des.unitsManager.formatInternalValue(outerRadius, _units, True) + '; '  
                desc += 'Inner Radius: ' + des.unitsManager.formatInternalValue(innerRadius, _units, True) + '; '
                desc += 'Member Radius: ' + des.unitsManager.formatInternalValue(memberRadius, _units, True) + '; '
                desc += 'Mesh Size: ' + des.unitsManager.formatInternalValue(meshSize, _units, True) + '; '
                desc += 'Delta Angle: ' + str(deltaAngle * (180/math.pi)) + '; '
                desc += 'Number Layers: ' + str(numLayer)
                VGmeshComp.description = desc
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        

        
# Event handler for the inputChanged event.
class VGmeshCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            
            global _units
                
            # Update the pitch diameter value.
            meshSize = None
            result = getCommandInputValue(_meshSize, '')
            if result[0]:
                meshSize = result[1]
            if not meshSize == None:
                if _numLayer.value.isdigit(): 
                    numLayer = int(_numLayer.value)
                    vesselHeight = numLayer * meshSize

                    # The pitch dia has been calculated in inches, but this expects cm as the input units.
                    des = adsk.fusion.Design.cast(_app.activeProduct)
                    vesselHeightText = des.unitsManager.formatInternalValue(vesselHeight, _units, True)
                    _vesselHeight.text = vesselHeightText
                else:
                    _vesselHeight.text = ''
            else:
                _vesselHeight.text = ''
            outerRadius = None
            result = getCommandInputValue(_outerRadius, '')
            if result[0]:
                outerRadius = result[1]
            if not outerRadius == None:
                vesselDiameter = outerRadius * 2
                vesselDiameterText = des.unitsManager.formatInternalValue(vesselDiameter, _units, True)
                _vesselDiameter.text = vesselDiameterText
            else:
                _vesselDiameter.text = ''

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
        
# Event handler for the validateInputs event.
class VGmeshCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            
            _errMessage.text = ''

            # Verify that at lesat 4 teath are specified.
            if not _numLayer.value.isdigit():
                _errMessage.text = 'The number of layers must be a whole number.'
                eventArgs.areInputsValid = False
                return
            else:    
                numLayer = int(_numLayer.value)

            if _outerRadius.value <= _innerRadius.value:
                _errMessage.text = 'Outer Radius must be greater than Inner Radius.'
                eventArgs.areInputsValid = False
                return
            else:
                outerRadius = float(_outerRadius.value)

                    
            if _deltaAngle.selectedItem.name == '15 deg':
                deltaAngle = 15.0 * (math.pi/180)
            elif _deltaAngle.selectedItem.name == '30 deg':
                deltaAngle = 20.0 * (math.pi/180)
            elif _deltaAngle.selectedItem.name == '45 deg':
                deltaAngle = 25.0 * (math.pi/180)

            des = adsk.fusion.Design.cast(_app.activeProduct)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Calculate points along an involute curve.
def involutePoint(baseCircleRadius, distFromCenterToInvolutePoint):
    try:
        # Calculate the other side of the right-angle triangle defined by the base circle and the current distance radius.
        # This is also the length of the involute chord as it comes off of the base circle.
        triangleSide = math.sqrt(math.pow(distFromCenterToInvolutePoint,2) - math.pow(baseCircleRadius,2)) 
        
        # Calculate the angle of the involute.
        alpha = triangleSide / baseCircleRadius

        # Calculate the angle where the current involute point is.
        theta = alpha - math.acos(baseCircleRadius / distFromCenterToInvolutePoint)

        # Calculate the coordinates of the involute point.    
        x = distFromCenterToInvolutePoint * math.cos(theta)
        y = distFromCenterToInvolutePoint * math.sin(theta)

        # Create a point to return.        
        return adsk.core.Point3D.create(x, y, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Builds a VGmesh.
def drawVGmesh(design, outerRadius, innerRadius, numLayer, meshSize, memberRadius, deltaAngle):
    try:        
        t_begin = time.time()
        # Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)
        newComp = adsk.fusion.Component.cast(newOcc.component)
        rootComp = design.rootComponent
        
        # Create a new sketch.
        sketches = newComp.sketches
        xzPlane = newComp.xZConstructionPlane
        baseSketch = sketches.add(xzPlane)
        origin = adsk.core.Point3D.create(0,0,0)

        # Create one unit component
        nr = math.floor((outerRadius - innerRadius) / meshSize) + 1
        nt = round(2 * math.pi / deltaAngle)
        nz = numLayer        
        t = deltaAngle / 2
        z = 0
        plate_unit_angle = adsk.core.ObjectCollection.create()
        support_unit_angle = adsk.core.ObjectCollection.create()
        for ir in range(0, nr):
            r1 = innerRadius + meshSize * ir
            if (ir % 2 == 0):
                y1 = r1 * math.tan(t)
                p1 = adsk.core.Point3D.create(r1, y1, z)
                p2 = adsk.core.Point3D.create(r1, -y1, z)
                create_bond(newComp, baseSketch, plate_unit_angle, p1, p2, memberRadius)
                if ir > 0:
                    p0 = adsk.core.Point3D.create(r1 - meshSize, 0, z)
                    create_bond(newComp, baseSketch, plate_unit_angle, p0, p1, memberRadius)
                    create_bond(newComp, baseSketch, plate_unit_angle, p0, p2, memberRadius)
                p3 = adsk.core.Point3D.create(r1 / math.cos(t), 0, z + meshSize)
                create_bond(newComp, baseSketch, support_unit_angle, p1, p3, memberRadius)
                create_bond(newComp, baseSketch, support_unit_angle, p2, p3, memberRadius)
                if ir < nr - 1:
                    r2 = r1 + meshSize
                    p4 = adsk.core.Point3D.create(r2 * math.cos(t), r2 * math.sin(t), z + meshSize)
                    create_bond(newComp, baseSketch, support_unit_angle, p1, p4, memberRadius)
                if ir > 0:
                    r0 = r1 - meshSize
                    p4 = adsk.core.Point3D.create(r0 * math.cos(t), r0 * math.sin(t), z + meshSize)
                    create_bond(newComp, baseSketch, support_unit_angle, p1, p4, memberRadius)
            else:
                p1 = adsk.core.Point3D.create(r1, 0, z)
                r0 = r1 - meshSize
                y0 = r0 * math.tan(t)
                p2 = adsk.core.Point3D.create(r0, y0, z)
                p3 = adsk.core.Point3D.create(r0, -y0, z)
                p4 = adsk.core.Point3D.create(r1 * math.cos(2*t), r1 * math.sin(2*t), z)
                create_bond(newComp, baseSketch, plate_unit_angle, p1, p2, memberRadius)
                create_bond(newComp, baseSketch, plate_unit_angle, p1, p3, memberRadius)
                create_bond(newComp, baseSketch, plate_unit_angle, p1, p4, memberRadius)
                x2 = r1 * math.cos(t)
                y2 = r1 * math.sin(t)
                p5 = adsk.core.Point3D.create(x2, y2, z + meshSize)
                p6 = adsk.core.Point3D.create(x2, -y2, z + meshSize)
                create_bond(newComp, baseSketch, support_unit_angle, p1, p5, memberRadius)
                create_bond(newComp, baseSketch, support_unit_angle, p1, p6, memberRadius)
                if ir < nr - 1:
                    r2 = r1 + meshSize
                    p7 = adsk.core.Point3D.create(r2 / math.cos(t), 0, z + meshSize)
                    create_bond(newComp, baseSketch, support_unit_angle, p1, p7, memberRadius)
                if ir > 0:
                    p7 = adsk.core.Point3D.create(r0 / math.cos(t), 0, z + meshSize)
                    create_bond(newComp, baseSketch, support_unit_angle, p1, p7, memberRadius)
        plate_b = plate_unit_angle.item(0)
        plate_unit_angle.removeByIndex(0)
        support_b = support_unit_angle.item(0)
        support_unit_angle.removeByIndex(0)
        combineFeats = newComp.features.combineFeatures
        combineInput = combineFeats.createInput(plate_b, plate_unit_angle)
        combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeats.add(combineInput)
        combineInput = combineFeats.createInput(support_b, support_unit_angle)
        combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeats.add(combineInput)
        plate_b = newComp.bRepBodies.item(0)
        support_b = newComp.bRepBodies.item(1)
        # Copy and paste in theta
        plate = adsk.core.ObjectCollection.create()
        support = adsk.core.ObjectCollection.create()
        plate.add(plate_b)
        support.add(support_b)
        normal = baseSketch.xDirection.crossProduct(baseSketch.yDirection)
        normal.transformBy(baseSketch.transform)
        for it in range(1, nt):
            theta = deltaAngle * it
            transform = adsk.core.Matrix3D.create()
            transform.setToRotation(theta, normal, baseSketch.origin)
            new_plate = adsk.core.ObjectCollection.create()
            new_support = adsk.core.ObjectCollection.create()
            new_plate.add(plate_b.copyToComponent(newOcc));
            new_support.add(support_b.copyToComponent(newOcc));
            moveInput = newComp.features.moveFeatures.createInput(new_plate, transform);
            newComp.features.moveFeatures.add(moveInput);
            moveInput = newComp.features.moveFeatures.createInput(new_support, transform);
            newComp.features.moveFeatures.add(moveInput);
            for entity in new_plate:
                plate.add(entity)
            for entity in new_support:
                support.add(entity)
        plate_b = plate.item(0)
        plate.removeByIndex(0)
        support_b = support.item(0)
        support.removeByIndex(0)
        combineFeats = newComp.features.combineFeatures
        combineInput = combineFeats.createInput(plate_b, plate)
        combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeats.add(combineInput)
        combineInput = combineFeats.createInput(support_b, support)
        combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeats.add(combineInput)

        plate_b = newComp.bRepBodies.item(0)
        support_b = newComp.bRepBodies.item(1)

        # Copy and paste in z
        rot = adsk.core.Matrix3D.create()
        rot.setToRotation(deltaAngle / 2, normal, baseSketch.origin)
        bodies = adsk.core.ObjectCollection.create()
        bodies.add(plate_b)
        bodies.add(support_b)
        for iz in range(1, nz):
            transform = adsk.core.Matrix3D.create()
            transform.translation = adsk.core.Vector3D.create(0, 0, meshSize * iz)
            new_plate = adsk.core.ObjectCollection.create()
            new_plate.add(plate_b.copyToComponent(newOcc));
            moveInput = newComp.features.moveFeatures.createInput(new_plate, transform);
            newComp.features.moveFeatures.add(moveInput);
            bodies.add(newComp.bRepBodies.item(newComp.bRepBodies.count - 1))
            if iz % 2 == 1:
                moveInput = newComp.features.moveFeatures.createInput(new_plate, rot);
                newComp.features.moveFeatures.add(moveInput);
            if iz < nz - 1:
                new_support = adsk.core.ObjectCollection.create()
                new_support.add(support_b.copyToComponent(newOcc));
                moveInput = newComp.features.moveFeatures.createInput(new_support, transform);
                newComp.features.moveFeatures.add(moveInput);
                if iz % 2 == 1:
                    moveInput = newComp.features.moveFeatures.createInput(new_support, rot);
                    newComp.features.moveFeatures.add(moveInput)
                bodies.add(newComp.bRepBodies.item(newComp.bRepBodies.count - 1))
        
        # for i in range(0, bodies.count - 1):
        #     combineFeats = newComp.features.combineFeatures
        #     that = adsk.core.ObjectCollection.create()
        #     that.add(bodies.item(i + 1))
        #     combineInput = combineFeats.createInput(bodies.item(i), that)
        #     combineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        #     combineFeats.add(combineInput)


        # Group everything used to create the gear in the timeline.
        timelineGroups = design.timeline.timelineGroups
        newOccIndex = newOcc.timelineObject.index
        baseSketchIndex = baseSketch.timelineObject.index
        timelineGroup = timelineGroups.add(newOccIndex, baseSketchIndex)
        timelineGroup.name = 'VGmesh'

        VGmeshValues = {}
        VGmeshValues['outerRadius'] = str(outerRadius)
        VGmeshValues['innerRadius'] = str(innerRadius)
        VGmeshValues['memberRadius'] = str(memberRadius)
        VGmeshValues['meshSize'] = str(meshSize)
        VGmeshValues['deltaAngle'] = str(deltaAngle)
        VGmeshValues['numLayer'] = str(numLayer)
        attrib = newComp.attributes.add('VGmesh', 'Values',str(VGmeshValues))
        
        newComp.name = 'VGmesh'
        t_end = time.time()
        _ui.messageBox('Elapsed time: %s' % str(t_end - t_begin))
        return newComp
    except Exception as error:
        _ui.messageBox("drawVGmesh Failed : " + str(error)) 
        return None

def create_bond(rootComp, rootSketch, container, start, end, r):
    planes = rootComp.constructionPlanes
    planeInput = planes.createInput()
    line_sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)
    lines = line_sketch.sketchCurves.sketchLines
    line = lines.addByTwoPoints(start, end)
    path = rootComp.features.createPath(line)
    planeInput = rootComp.constructionPlanes.createInput() 
    planeInput.setByDistanceOnPath(path, adsk.core.ValueInput.createByReal(0))
    plane1 = rootComp.constructionPlanes.add(planeInput)
    sketch1 = rootComp.sketches.add(plane1)
    circles = sketch1.sketchCurves.sketchCircles
    circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), r)
    profile0 = sketch1.profiles.item(0)
    extrudes = rootComp.features.extrudeFeatures
    dist = adsk.core.ValueInput.createByReal(start.distanceTo(end))
    extrude1 = extrudes.addSimple(profile0, dist, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    container.add(rootComp.bRepBodies.item(rootComp.bRepBodies.count - 1))
    line_sketch.deleteMe()
    sketch1.deleteMe()