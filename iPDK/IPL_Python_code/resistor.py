#******************************************************************************************
#******************************************************************************************
#**********                       SAED_PDK90 1P9M                         *****************
#******************************************************************************************
#******************************************************************************************

########################################################################
#                                                                      #
# Resistor.py                                                          #
#                                                                      #
########################################################################

from __future__ import with_statement

from cni.dlo import *
from cni.geo import *
from cni.constants import *
from resistorUnit import *
from cni.integ.common import renameParams, reverseDict
import techUtils

class Resistor(DloGen):

    metal1Layer =   ("M1",    "drawing")
    nimpLayer =     ("NIMP",      "drawing")
    pimpLayer =     ("PIMP",      "drawing")
    nwellLayer =    ("NWELL",     "drawing")
    contactLayer =  ("CO",   "drawing")
    rmarLayer =      ("RMARK",       "drawing")
    sblkLayer =     ("SBLK", "drawing")
        
    paramNames = dict(
        wf           = "wf",
        lf           = "lf",
        fr           = "fr",
        rw           = "rw",
        lcontact     = "lcontact",
        wbar         = "wbar",
        connect      = "connect",
        ruleset      = "ruleset",
        dummies      = "dummies",

        # These are not true parameters.
        resistorType = "resistorType",
        implantType  = "implantType",
        silicided    = "silicided",
    )

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs    = ParamSpecArray()

        # check to see if there are device specific minimum sizes defined
        # in the technology file; if not, then just use the minimum width
        # value defined for the layer on which the resistor is created.

        resistorType = 'poly'
        layer = ResistorUnit.getContactLayer(resistorType)

        (width, length) = ResistorUnit.getMinimumResistorSize(False, specs.tech, resistorType)
        (contactWidth, contactLength) = ResistorUnit.getMinimumContactSize(specs.tech, layer)
        barWidth = 2 * specs.tech.getPhysicalRule('minWidth', Layer(*cls.metal1Layer))
	
	#print barWidth;
	#print length;
	#print width;
	
        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameters for this resistor parameterized cell;
        # note that out-of-range parameter values will be rejected.
        # Since width and contact length parameter values will be used
        # for routing, these values must lie on even grid points.
        # Note that any route path must be on even grid points.
        gridSize = specs.tech.getGridResolution()
        mySpecs('wf', cls.default.get('wf', width), 
              'width per finger')
	      
	#mySpecs('wf', cls.default.get('wf', width), 
        #      'width per finger',
        #      StepConstraint(gridSize, width, None, action=REJECT))
        
	mySpecs('lf', cls.default.get('lf', length), 
              'length per finger')
	
	#mySpecs('lf', cls.default.get('lf', length), 
        #      'length per finger',
        #      StepConstraint(gridSize, length, None, action=REJECT))
        
	mySpecs('fr', cls.default.get('fr', 1), 
              'fingers per row',
              RangeConstraint(1, None, REJECT))
	
        mySpecs('rw', cls.default.get('rw', 1), 
              'number of rows',
              RangeConstraint(1, None, REJECT))
        mySpecs('lcontact', cls.default.get('lcontact', contactLength),
              'length of contacts',
              StepConstraint(gridSize, contactLength, None, action=REJECT))
        mySpecs('wbar', cls.default.get('wbar', barWidth), 
              'width of bars',
              StepConstraint(gridSize, barWidth, None, action=REJECT))
        mySpecs('connect', cls.default.get('connect', 'series'), 
              'Connection type (series or parallel)',
              ChoiceConstraint(['series', 'parallel']))                        
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
              'Ruleset type (construction or recommended)',
              ChoiceConstraint(['construction', 'recommended']))                        
        mySpecs('dummies', cls.default.get('dummies', False), 'Generate dummy resistor fingers')

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)


    def setupParams(self, params):

        # Parameter renaming
        self.paramNamesReversed = reverseDict( self.paramNames)
        myParams = ParamArray()
        renameParams( params, myParams, self.paramNamesReversed)

        # save parameter values using class variables
        self.resistorType = myParams['resistorType']
        self.implantType = myParams['implantType']
        self.width = myParams['wf']
        self.length = myParams['lf']
        self.fingers = myParams['fr']
        self.rows = myParams['rw']
        self.barWidth = myParams['wbar']
        self.contactLength = myParams['lcontact']
        self.connect = myParams['connect']
        self.dummies = myParams['dummies']
        self.ruleset = myParams['ruleset']
        self.silicided = myParams['silicided']
    
        # set up any device context which should be used
        self.deviceContext = self.tech.getActiveDeviceContext().name

        # set up ruleset to be used during device construction
        rulesets = ['construction', 'default']
        if self.ruleset == 'recommended':
            rulesets.insert(0, 'recommended')
        self.ruleset = techUtils.orderedRuleset(self.tech, rulesets)

        # use any specified rule set to calculate minimum values
        with RulesetManager(self.tech, self.ruleset):

            # readjust width and length, as minimum values may be different;
            # should use any device specific minimum values which may be defined.

            self.resistorLayer = ResistorUnit.getResistorLayer(self.resistorType)
            layer = ResistorUnit.getContactLayer(self.resistorType)

            (minWidth, minLength) = ResistorUnit.getMinimumResistorSize(self.silicided, self.tech, self.resistorType) 
            if self.width < 4e-4:
	    	self.width = self.width * 1e6
            if self.length < 4e-4:
	    	self.length = self.length * 1e6
            self.width = max(self.width, minWidth)
            self.length = max(self.length, minLength)

            (contactWidth, contactLength) = ResistorUnit.getMinimumContactSize(self.tech, layer)
            self.contactLength = max(self.contactLength, contactLength)

            # lookup portable layer names, and save layer values using class variables
            self.metalLayer = Layer(*self.metal1Layer)
            self.barLayer = self.metalLayer
            self.nimpLayer = Layer(*self.nimpLayer)
            self.pimpLayer = Layer(*self.pimpLayer)
            self.nwellLayer = Layer(*self.nwellLayer)
            self.rmarLayer = Layer(*self.rmarLayer)
            self.contactLayer = Layer(*self.contactLayer)
	    self.sblkLayer = Layer(*self.sblkLayer)
	    
	    
    
            # define implant layer for doping poly or diffusion resistors
            if self.implantType == 'N':
                self.implantLayer = self.nimpLayer
            elif self.implantType == 'P':
                self.implantLayer = self.pimpLayer

            # define Resist Protection Oxide layer used to block silicide formation
            
	    
	    if (not self.silicided):
                self.highResLayer = self.sblkLayer
	    	    
	    # define base name which should be used for each resistor unit
            self.baseName = "RES"



    def genLayout(self):
        # use specified rule set to construct resistor 
        with RulesetManager(self.tech, self.ruleset):
            self.construct()


    def construct(self):

        # place the individual resistor units into an array;
        # each row contains several fingers, and these rows 
        # are then stacked one row above the previous row.
        self.stackUnits()

        # create any silicide blocks needed for each row
        if (not self.silicided):
            self.createSilicideBlocks()
	
	self.createRmarkLayer()

        # create route bars for parallel connection case
        self.createBars()

        # generate required routing between resistor units
        self.createRouting()

        # create implant layer for doping polysilicon or diffusion resistors
        if self.resistorType in ['poly', 'diff']:
            self.createImplant(self.implantLayer)
	
	# create pins for this resistor
        self.createPins()



    def stackUnits(self):

        # create a single instance of the base resistor unit, 
        # which will be used for each finger; this base unit
        # will be arrayed as several fingers stacked in rows.

        # Adjust user-supplied length value for resistor unit.
        # For an unsilicided resistor unit, this length should
        # only be the length of the unsilicided region.
        # For a silicided resistor unit, this length should be
        # the distance between the contact layer geometries
        # in the top and bottom contact objects.
        if self.silicided:
            adjustLength1 = techUtils.getMinClearanceRule(self.tech, self.rmarLayer, self.contactLayer)
            adjustLength2 = techUtils.getMinSymmetricExtensionRule(self.tech, self.resistorLayer, self.contactLayer)
	    adjustLength = adjustLength1 - adjustLength2
            self.length = self.length + 2 * adjustLength
        else:
            adjustLength1 = techUtils.getMinClearanceRule(self.tech, self.highResLayer, self.contactLayer)
            adjustLength2 = techUtils.getMinSymmetricExtensionRule(self.tech, self.resistorLayer, self.contactLayer)
            adjustLength = adjustLength1 - adjustLength2
            self.length = self.length + 2 * adjustLength

        unitParams = ParamArray(resistorType = self.resistorType,
                                width = self.width,
                                length = self.length,
                                contactLength = self.contactLength,
                                silicided = self.silicided,
                                ruleset = self.ruleset,
                                deviceContext = self.deviceContext)

        # create resistor unit for each finger of this resistor
        baseUnit = Instance('ResistorUnit', 
                            unitParams, ['A', 'B'], self.baseName)
        baseUnit1 = baseUnit.clone()

        # in order to create an array of these resistor units, first 
        # obtain the DRC correct spacing in each direction; this will
        # be used to place each of the individual resistor units.

        (self.dX, self.dY) = self.calculateXYSpacing(baseUnit, baseUnit1)
	
        # now calculate spacing based upon metal routing which will be used;
        # series routing in both X and Y directions needs to be re-calculated.
        # Note that due to "wide metal" design rules, spacing changes in the
        # X-direction may affect Y-direction spacing (and vice-versa).

        while True:

            x_spacing = self.dX
            y_spacing = self.dY

            # consider routing in the X-direction
            unitParams['width'] = 2 * self.width + self.dX
            baseUnit.setParams(unitParams) 
            baseUnit1.setParams(unitParams) 
            (route_dX, route_dY) = self.calculateXYSpacing(baseUnit, baseUnit1)
            self.dX = max(self.dX, route_dX)
            self.dY = max(self.dY, route_dY)

            # consider routing in the Y-direction
            unitParams['contactLength'] = 2 * self.contactLength + self.dY
            baseUnit.setParams(unitParams) 
            baseUnit1.setParams(unitParams) 
            (route_dX, route_dY) = self.calculateXYSpacing(baseUnit, baseUnit1)
            self.dX = max(self.dX, route_dX)
            self.dY = max(self.dY, route_dY)

            # check to see if spacing calculations have made any changes;
            # if not, then X and Y spacing calculation has been completed.
            if  ((x_spacing == self.dX) and (y_spacing == self.dY)):
                break


        unitParams['contactLength'] = self.contactLength
        unitParams['width'] = self.width
        baseUnit.setParams(unitParams)


        # Adjust X and Y spacing for additional contact enclosure;
        # this is necessary, since the resistor unit contacts may
        # need additional Metal1 enclosure for "wide metal" rules.
        tempRect = Rect(self.metalLayer, baseUnit.findInstPin('A').getBBox())
        tempRect.setCoord(SOUTH, tempRect.getCoord(SOUTH) - (self.contactLength + self.dY))
        adjustEnclosure =  self.getContactAdjustEnclosure(tempRect, baseUnit.findInstPin('A'))
        tempRect.destroy()
        self.dX = self.dX + 2 * adjustEnclosure


        # now place resistor units into an array, each one next to the previous one
        xOffset = self.dX + baseUnit.getBBox().getWidth() 
        yOffset = self.dY + baseUnit.getBBox().getHeight()
        tmpGroup = baseUnit.makeArray(xOffset, yOffset, 
                                      self.rows, self.fingers, self.baseName)
        tmpGroup.ungroup()
        baseUnit.destroy()
        baseUnit1.destroy()


        # Check to see if "dummy" resistor units are needed; if so, then create
        # rectangles of the proper size on the layer which is being used for
        # the resistor units. These dummy resistors are then placed at each end 
        # of the row of resistor fingers, using peviously calculated spacing.
        if self.dummies:
            for i in range(self.rows):
                # place dummy resistor at beginning of this row
                unit = self.findInstance(i, 0)
                dummyBox = unit.getBBox(ShapeFilter(self.resistorLayer))
                dummy = Rect(self.resistorLayer, dummyBox)
                place(dummy, Direction.WEST, unit, self.dX)
                # place dummy resistor at the end of this row
                unit = self.findInstance(i, self.fingers - 1)
                dummyBox = unit.getBBox(ShapeFilter(self.resistorLayer))
                dummy = Rect(self.resistorLayer, dummyBox)
                place(dummy, Direction.EAST, unit, self.dX)




    def createSilicideBlocks(self):

        # if this is a non-silicided resistor, then we need to add 
        # Resist Protection Oxide layer enclosure rectangle; note that
        # we consider the spacing between contacts and the RPO layer.

        for i in range(self.rows):
            fingerGroup = Grouping('fingerGroup')
            for j in range(self.fingers):
                unit = self.findInstance(i, j)
                fingerGroup.add(unit)
            rpoGroup = fgAddEnclosingRects(fingerGroup, [self.highResLayer])   
            rpoRect = rpoGroup.getComps()[0]
            rpoBox = rpoRect.getBBox()
            rpoGroup.ungroup()

            # ensure that the RPO enclosure of the resistor layer will
            # satisfy any "wide RPO" design rules; this is temporary
            # code, until PR #816 for fgAddEnclosingRects() is fixed.
            # Note that adding dummy units may also create "wide RPO".
            rpoWidth = rpoBox.getWidth()
            if self.dummies:
                rpoWidth = rpoWidth + 2 * (self.width + self.dX)
            if self.tech.conditionalRuleExists('minExtension', self.highResLayer, self.resistorLayer, ['width']):
                minEnclosure = self.tech.getPhysicalRule('minExtension', self.highResLayer, self.resistorLayer, params={'width':rpoWidth})
                actualEnclosure = fingerGroup.getBBox(ShapeFilter(self.resistorLayer)).left - rpoBox.left
                if minEnclosure > actualEnclosure:
                    rpoBox.expand(minEnclosure - actualEnclosure)
	    
            # we now need to adjust this RPO rectangle, so that it does not
            # overlap the contacts for each of the different resistor units.
            spacing = techUtils.getMinClearanceRule(self.tech, self.highResLayer, self.contactLayer)
            enclosure = fingerGroup.getBBox().top - fingerGroup.getBBox(ShapeFilter(self.contactLayer)).top
            drcLength = spacing - enclosure
            fingerBox = fingerGroup.getBBox()
            adjustLength = drcLength + ((fingerBox.getHeight() - self.length)/2)
            rpoBox.top = fingerBox.top - adjustLength
            rpoBox.bottom = fingerBox.bottom + adjustLength

            # the RPO rectangle also needs to cover any dummy resistor units
            if self.dummies:
                # allow for dummies at each end of this row
                dummyAdjust = (self.width + self.dX)
                rpoBox.left = rpoBox.left - dummyAdjust
                rpoBox.right = rpoBox.right + dummyAdjust

            # also make sure that this RPO rectangle meets any minimum area rules;
            # note that this is not handled by the fgAddEnclosingRects() method.
            if self.tech.physicalRuleExists('minArea', self.highResLayer):
                minArea = self.tech.getPhysicalRule('minArea', self.highResLayer)
                grid = Grid(self.tech.getGridResolution())
                rpoBox.expandForMinArea(WEST, minArea, grid)
            if (rpoBox.top - rpoBox.bottom) > 0:
                rpoRect.setBBox(rpoBox)

            # ensure that the silicide block is properly aligned with the resistor fingers
            alignLocation(rpoRect, Location.CENTER_CENTER, fingerGroup)

            # after alignment, make sure that this RPO rectangle lies on grid points
            rpoRect = ResistorUnit.expandToGrid(self.tech, rpoRect)
                
            # also check to see if special resistor layer needs to be used
            # in conjunction with the Resist Protection Oxide (RPO) layer.
            if 'RH' in self.tech.getSantanaLayerNames():
                fingerGroup.add(rpoRect)
                rhGroup = fgAddEnclosingRects(fingerGroup, [Layer('RH')])
                rhRect = rhGroup.getComps()[0]
                rhBox = rhRect.getBBox()
                # this RH rectangle also needs to cover any dummy resistor units
                if self.dummies:
                    # allow for dummies at each end of this row
                    dummyAdjust = (self.width + self.dX)
                    rhBox.left = rhBox.left - dummyAdjust
                    rhBox.right = rhBox.right + dummyAdjust
                    rhRect.setBBox(rhBox)

            fingerGroup.ungroup()

    def createRmarkLayer(self):

        # if this is a non-silicided resistor, then we need to add 
        # Resist Protection Oxide layer enclosure rectangle; note that
        # we consider the spacing between contacts and the RPO layer.

        for i in range(self.rows):
            fingerGroup = Grouping('fingerGroup')
            for j in range(self.fingers):
                unit = self.findInstance(i, j)
                fingerGroup.add(unit)
            rpoGroup = fgAddEnclosingRects(fingerGroup, [self.rmarLayer])   
            rpoRect = rpoGroup.getComps()[0]
            rpoBox = rpoRect.getBBox()
            rpoGroup.ungroup()

            # ensure that the RPO enclosure of the resistor layer will
            # satisfy any "wide RPO" design rules; this is temporary
            # code, until PR #816 for fgAddEnclosingRects() is fixed.
            # Note that adding dummy units may also create "wide RPO".
            rpoWidth = rpoBox.getWidth()
            if self.dummies:
                rpoWidth = rpoWidth + 2 * (self.width + self.dX)
            if self.tech.conditionalRuleExists('minExtension', self.rmarLayer, self.resistorLayer, ['width']):
                minEnclosure = self.tech.getPhysicalRule('minExtension', self.rmarLayer, self.resistorLayer, params={'width':rpoWidth})
                actualEnclosure = fingerGroup.getBBox(ShapeFilter(self.resistorLayer)).left - rpoBox.left
                if minEnclosure > actualEnclosure:
                    rpoBox.expand(minEnclosure - actualEnclosure)
	    
            # we now need to adjust this RPO rectangle, so that it does not
            # overlap the contacts for each of the different resistor units.
            spacing = techUtils.getMinClearanceRule(self.tech, self.rmarLayer, self.contactLayer)
            enclosure = fingerGroup.getBBox().top - fingerGroup.getBBox(ShapeFilter(self.contactLayer)).top
            drcLength = spacing - enclosure
            fingerBox = fingerGroup.getBBox()
            adjustLength = drcLength + ((fingerBox.getHeight() - self.length)/2)
            rpoBox.top = fingerBox.top - adjustLength
            rpoBox.bottom = fingerBox.bottom + adjustLength

            # the RPO rectangle also needs to cover any dummy resistor units
            if self.dummies:
                # allow for dummies at each end of this row
                dummyAdjust = (self.width + self.dX)
                rpoBox.left = rpoBox.left - dummyAdjust
                rpoBox.right = rpoBox.right + dummyAdjust

            # also make sure that this RPO rectangle meets any minimum area rules;
            # note that this is not handled by the fgAddEnclosingRects() method.
            if self.tech.physicalRuleExists('minArea', self.rmarLayer):
                minArea = self.tech.getPhysicalRule('minArea', self.rmarLayer)
                grid = Grid(self.tech.getGridResolution())
                rpoBox.expandForMinArea(WEST, minArea, grid)
            if (rpoBox.top - rpoBox.bottom) > 0:
                rpoRect.setBBox(rpoBox)

            # ensure that the silicide block is properly aligned with the resistor fingers
            alignLocation(rpoRect, Location.CENTER_CENTER, fingerGroup)

            # after alignment, make sure that this RPO rectangle lies on grid points
            rpoRect = ResistorUnit.expandToGrid(self.tech, rpoRect)
                
            # also check to see if special resistor layer needs to be used
            # in conjunction with the Resist Protection Oxide (RPO) layer.
            if 'RH' in self.tech.getSantanaLayerNames():
                fingerGroup.add(rpoRect)
                rhGroup = fgAddEnclosingRects(fingerGroup, [Layer('RH')])
                rhRect = rhGroup.getComps()[0]
                rhBox = rhRect.getBBox()
                # this RH rectangle also needs to cover any dummy resistor units
                if self.dummies:
                    # allow for dummies at each end of this row
                    dummyAdjust = (self.width + self.dX)
                    rhBox.left = rhBox.left - dummyAdjust
                    rhBox.right = rhBox.right + dummyAdjust
                    rhRect.setBBox(rhBox)

            fingerGroup.ungroup()

    def createBars(self):

        resistorStack = self.makeGrouping('resistorStack')

        # construct bars for the resistor routing for parallel connections;
        # these bars are used to provide connection connection points for
        # the routing program when this parameterized cell is used in a design.
        # In the parallel case, these bars are placed to the left and right.

        if self.connect == "parallel":
            w = self.barWidth
            l = resistorStack.getBBox().getHeight()
            self.sourceBar = Bar(self.barLayer, NORTH_SOUTH, 'S', Point(0,0), Point(w,l))
            self.drainBar = Bar(self.barLayer, NORTH_SOUTH, 'D', Point(0,0), Point(w,l))
            fgPlace(self.sourceBar, Direction.WEST, resistorStack)
            fgPlace(self.drainBar, Direction.EAST, resistorStack)


    def createImplant(self, implantLayer):

        # also create an implant rectangle for doping polysilicon or diffusion;
        # this implant is shared by all resistor fingers and any dummy fingers.

        resistorStack = Grouping.find('resistorStack')

        # should also create enclosing Nwell layer for P+ diffusion resistors;
        # note that both implant and nwell layers need to be considered at
        # the same time, since nwell layer affects implant spacing rules.
        if self.resistorType == 'diff' and self.implantLayer == self.pimpLayer:
            fgAddEnclosingRects(resistorStack, [implantLayer, self.nwellLayer])
        else:
            fgAddEnclosingRects(resistorStack, [implantLayer])

    def createRouting(self):

        # Create straight-line route between the contacts for each resistor unit;
        # for "parallel" connection, both top and bottom contacts are connected,
        # but for "series" connection, top and bottom contacts alternate connections.
        # Note that Bars are used to provide connections between rows of resistors 
        # for "parallel" connections.

        # use length of resistor contacts for width of routing segments within rows;
        # use width of the resistor for width of routing segments between rows.

        resistorStack = Grouping.find('resistorStack')

        if self.connect == "parallel":

            # save metal routing rectangles for final Bar placement
            sourceRectList = []
            drainRectList = []

            # make the parallel connections between fingers for the bottom row
            fromUnit = self.findInstance(0, 0)
            toUnit = self.findInstance(0, self.fingers-1)
            connectBox = Box(fromUnit.findInstPin('A').getBBox().lowerLeft(),
                             toUnit.findInstPin('A').getBBox().upperRight())
            connectRect = Rect(self.metalLayer, connectBox)
            sourceRectList.append(connectRect)
            # check for additional Metal1 enclosure for resistor unit contact
            self.adjustRouteEnclosure(connectRect, toUnit.findInstPin('A'))

            # make the parallel connections between fingers for the top row
            fromUnit = self.findInstance(self.rows-1, 0)
            toUnit = self.findInstance(self.rows-1, self.fingers-1)
            connectBox = Box(fromUnit.findInstPin('B').getBBox().lowerLeft(),
                             toUnit.findInstPin('B').getBBox().upperRight())
            connectRect = Rect(self.metalLayer, connectBox)
            if (self.rows % 2 == 0):
                sourceRectList.append(connectRect)
            else:
                drainRectList.append(connectRect)
             # check for additional Metal1 enclosure for resistor unit contact
            self.adjustRouteEnclosure(connectRect, toUnit.findInstPin('B'))

            # now make the parallel connections between rows;
            # these are simply large rectangles between each row.
            for i in range(self.rows-1):
                fromUnit = self.findInstance(i, 0)
                toUnit = self.findInstance(i+1, self.fingers-1)
                connectBox = Box(fromUnit.findInstPin('B').getBBox().lowerLeft(),
                                 toUnit.findInstPin('A').getBBox().upperRight())
                connectRect = Rect(self.metalLayer, connectBox)
                if (i % 2 == 0):
                    drainRectList.append(connectRect)
                else:
                    sourceRectList.append(connectRect)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustRouteEnclosure(connectRect, toUnit.findInstPin('A'))

            # Now that routing has completed, place the source and drain Bars again.
            # This is done to account for any "wide metal" created during routing.
            # After Bars are placed, and the route rectangles have been extended
            # to meet these route Bars, "wide metal" may be introduced. Thus, it
            # may be necessary to call fgPlace() multiple times. 
            while True:
                # extend route rectangles to meet the route Bars
                for rect in sourceRectList:
                    connectBox = rect.getBBox()
                    connectBox.setLeft(self.sourceBar.getRect().getBBox().getLeft())
                    rect.setBBox(connectBox)
                for rect in drainRectList:
                    connectBox = rect.getBBox()
                    connectBox.setRight(self.drainBar.getRect().getBBox().getRight())
                    rect.setBBox(connectBox)
                spacing1 = self.sourceBar.getSpacing(WEST, resistorStack)
                spacing2 = self.drainBar.getSpacing(EAST, resistorStack)
                # Now use fgPlace() to place Bars, using route rectangles.
                # Note that the drain route rectangles are used as reference
                # to place the Source bar, while the source route rectangles
                # are used as a reference to place the Drain Bar.
                for rect in drainRectList:
                    resistorStack.add(rect)
                fgPlace(self.sourceBar, WEST, resistorStack)
                for rect in drainRectList:
                    resistorStack.remove(rect)
                for rect in sourceRectList:
                    resistorStack.add(rect)
                fgPlace(self.drainBar, EAST, resistorStack)
                for rect in sourceRectList:
                    resistorStack.remove(rect)
                # also align these Bars to the overall resistor layout
                self.sourceBar.alignEdge(Direction.SOUTH, resistorStack)
                self.drainBar.alignEdge(Direction.NORTH, resistorStack)
                # check to see if this placement resulted in any changes;
                # if not, then the placement of Bars has been completed.
                if ((spacing1 == self.sourceBar.getSpacing(WEST, resistorStack)) and
                    (spacing2 == self.drainBar.getSpacing(EAST, resistorStack))):
                    break

            # also check that the length of resistor body is long enough so that no
            # "wide metal" spacing errors were introduced between route rectangles.
            if len(sourceRectList) > 0 and len(drainRectList) > 0:
                # find largest source and drain routing rectangles
                sourceRectList.sort(key=lambda x : x.getBBox().getArea(), reverse=True)
                drainRectList.sort(key=lambda x : x.getBBox().getArea(), reverse=True)
                # now measure spacing between these two route rectangles
                spacing = fgMinSpacing(sourceRectList[0], NORTH, drainRectList[0])
                if spacing > self.length:
                    raise ValueError, "Length of resistor finger (%s) must be at least %s to satisfy metal1 spacing rules" % \
                                      (str(self.length), str(spacing))

        elif self.connect == "series":

            # make the series connections between fingers for the top and bottom rows
            for j in range(self.fingers - 1):
                if (j % 2 == 0):
                    fromUnit = self.findInstance(self.rows-1, j)
                    toUnit = self.findInstance(self.rows-1, j+1)
                    RoutePath.StraightLine(fromUnit.findInstPin('B'), 
                                           toUnit.findInstPin('B'), 
                                           self.metalLayer, self.contactLength)  
                    # check for additional Metal1 enclosure for resistor unit contact
                    self.adjustSeriesRouteEnclosure([fromUnit.findInstPin('B'), toUnit.findInstPin('B')], toUnit.findInstPin('B'))
                else:
                    fromUnit = self.findInstance(0, j)
                    toUnit = self.findInstance(0, j+1)
                    RoutePath.StraightLine(fromUnit.findInstPin('A'), 
                                           toUnit.findInstPin('A'), 
                                           self.metalLayer, self.contactLength)  
                    # check for additional Metal1 enclosure for resistor unit contact
                    self.adjustSeriesRouteEnclosure([fromUnit.findInstPin('A'), toUnit.findInstPin('A')], toUnit.findInstPin('A'))

            # make the series connections between rows
            for i in range(self.rows - 1):
                for j in range(self.fingers):
                    fromUnit = self.findInstance(i, j)
                    toUnit = self.findInstance(i + 1, j)
                    RoutePath.StraightLine(fromUnit.findInstPin('B'), 
                                           toUnit.findInstPin('A'), 
                                           self.metalLayer, self.width)  
                    # check for additional Metal1 enclosure for resistor unit contact
                    self.adjustSeriesRouteEnclosure([fromUnit.findInstPin('B'), toUnit.findInstPin('A')], toUnit.findInstPin('A'))


            # also check that the length of resistor body is long enough so that no
            # "wide metal" spacing errors were introduced routing between contacts.
            w = self.width
            l = self.contactLength
            if self.fingers > 1:
                w = 2 * self.width + self.dX
            tempRect1 = Rect(self.metalLayer, Box(Point(0,0), Point(w,l)))
            w = self.width
            l = self.contactLength
            if self.rows > 1:
                l = 2 * self.contactLength + self.dY
            tempRect2 = Rect(self.metalLayer, Box(Point(0,0), Point(w,l)))
            spacing = fgMinSpacing(tempRect2, NORTH, tempRect1)
            tempRect1.destroy()
            tempRect2.destroy()
            if spacing > self.length:
                raise ValueError, "Length of resistor finger (%s) must be at least %s to satisfy metal1 spacing rules" % \
                                  (str(self.length), str(spacing))



    def createPins(self):

        # Create the device pins for this resistor, based upon the connection type.
        # If the connection type is "series", then use instance pins on the beginning
        # and ending resistor units; if "parallel", then use the two route bars.

        if self.connect == "series":
            # use the beginning and ending resistor units to create pins;
            # note that the ending unit depends on the number of fingers.
            self.addPin('PLUS', 'PLUS', 
                        self.findInstance(0,0).findInstPin('A').getBBox(), 
                        self.metalLayer)
            if self.fingers % 2 == 0:
                self.addPin('MINUS', 'MINUS', 
                            self.findInstance(0, self.fingers-1).findInstPin('A').getBBox(), 
                            self.metalLayer)
            else:
                self.addPin('MINUS', 'MINUS', 
                            self.findInstance(self.rows-1, self.fingers-1).findInstPin('B').getBBox(), 
                            self.metalLayer)

        elif self.connect == "parallel":
            # use the bars created for parallel routing to create pins
            self.addPin('PLUS', 'PLUS', self.sourceBar.getBBox(), self.barLayer)
            self.addPin('MINUS', 'MINUS', self.drainBar.getBBox(), self.barLayer)

        # Remove extra nets which were only used during device construction;
        # the 'A' and 'B' instance terminals for resistor units are required
        # to access the contacts for connection of individual resistor units.
        for netName in ['A', 'B']:
            if Net.find(netName):
                Net.find(netName).destroy()


    def findInstance(self, i, j):
        # create instance name from base name
        name = self.baseName + '_' + str(i) + '_' + str(j)
        # find this instance in the array of resistor units
        return(Instance.find(name))


    def calculateXYSpacing(self, baseUnit, baseUnit1):
        # Calculate the DRC correct spacing in both X and Y directions.
        # Note that this spacing depends upon the existence of the Resist
        # Protection Oxide layer rectangle used for non-silicided resistors.
        # Thus, we need to create a temporary RPO enclosure rectangle.
        if (not self.silicided):
            tmpGroup = fgAddEnclosingRects(baseUnit, [self.highResLayer])
            #dX = fgMinSpacing(baseUnit, Direction.EAST,
            #                  baseUnit1, env = tmpGroup.getComps()[0])
            dX = 0.3
	    dY = fgMinSpacing(baseUnit, Direction.NORTH, 
                              baseUnit1, env = tmpGroup.getComps()[0])
            tmpGroup.destroy()
        else:
            tmpGroup = fgAddEnclosingRects(baseUnit, [self.rmarLayer])
            dX = fgMinSpacing(baseUnit, Direction.EAST,
                              baseUnit1, env = tmpGroup.getComps()[0])
            dY = fgMinSpacing(baseUnit, Direction.NORTH, 
                              baseUnit1, env = tmpGroup.getComps()[0])
            tmpGroup.destroy()
        return(dX, dY)
        
	
    def getContactAdjustEnclosure(self, routeRect, contactInstPin):
        # Check to see if the metal1 enclosure of contact needs to be adjusted
        # for the presence of "wide metal" routing rectangles for the individual
        # resistor unit contacts. Note that when these resistor unit contacts are
        # created, they are not aware of the possible existence of "wide metal".

        # first determine the actual metal1 enclosure value
        top1 = routeRect.top
        bottom1 = routeRect.bottom
        right1 = routeRect.right
        left1 = routeRect.left
        for comp in contactInstPin.getInst().getCompRefs():
            if isinstance(comp, InstanceRef):
                if comp.getBBox(ShapeFilter(self.metalLayer)) == contactInstPin.getBBox():
                   contactBox = comp.getBBox(ShapeFilter(self.contactLayer))
                   top2 = contactBox.top 
                   bottom2 = contactBox.bottom 
                   right2 = contactBox.right 
                   left2 = contactBox.left 
                   actualEnclosure = min(top1 - top2, right1 - right2, bottom2-bottom1, left2-left1)
        
        # now determine the expected minimum enclosure value
        minEnclosure = techUtils.getMinExtensionRule(self.tech, self.metalLayer, self.contactLayer, width=routeRect.getHeight())

        adjustEnclosure = 0
        if minEnclosure > actualEnclosure:
            adjustEnclosure = minEnclosure - actualEnclosure
          
        return(adjustEnclosure)



    def adjustRouteEnclosure(self, routeRect, contactInstPin, adjustDirectionList=[]):
        # Check to see if the metal1 enclosure of contact needs to be adjusted
        # for the presence of "wide metal" routing rectangles for the individual
        # resistor unit contacts. Note that when these resistor unit contacts are
        # created, they are not aware of the possible existence of "wide metal".

        adjustEnclosure = self.getContactAdjustEnclosure(routeRect, contactInstPin)

        # now adjust the routing rectangle as needed
        if adjustEnclosure > 0:
            routeRect.setBBox(routeRect.getBBox().expand(adjustEnclosure))
          

    def adjustSeriesRouteEnclosure(self, connectComps, contactInstPin):
        # Create a routing rectangle between the two connection components;
        # this will be used to check for possible adjustment of the metal1
        # enclosure for the resistor unit contact. If no enclosure adjustment
        # is required, then this routing rectangle will then be deleted.

        connectBox = Box(connectComps[0].getBBox().lowerLeft(),
                         connectComps[1].getBBox().upperRight())
        connectRect = Rect(self.metalLayer, connectBox)

        # if no enclosure adjustment is needed, then delete routing rectangle
        adjustEnclosure = self.getContactAdjustEnclosure(connectRect, contactInstPin)
        if adjustEnclosure > 0:
            self.adjustRouteEnclosure(connectRect, contactInstPin)
        else:
            connectRect.destroy()


class rnpoly(Resistor):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'N'
        params['silicided'] = True
        # call method on base Resistor class
        Resistor.setupParams(self, params)


class rppoly(Resistor):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'P'
        params['silicided'] = True
        # call method on base Resistor class
        Resistor.setupParams(self, params)


class rndiff(Resistor):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'diff'
        params['implantType'] = 'N'
        params['silicided'] = True
        # call method on base Resistor class
        Resistor.setupParams(self, params)


class rpdiff(Resistor):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'diff'
        params['implantType'] = 'P'
        params['silicided'] = True
        # call method on base Resistor class
        Resistor.setupParams(self, params)


class rnpoly_wos(Resistor):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'N'
        params['silicided'] = False
        # call method on base Resistor class
        Resistor.setupParams(self, params)


class rppoly_wos(Resistor):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'P'
        params['silicided'] = False
        # call method on base Resistor class
        Resistor.setupParams(self, params)
