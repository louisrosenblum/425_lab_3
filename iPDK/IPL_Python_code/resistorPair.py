########################################################################
# Copyright (c) 2001-2008 by Ciranova, Inc. All rights reserved.       #
#                                                                      #
# Permission is hereby granted, free of charge, to any person          #
# obtaining a copy of this software and associated documentation       #
# ("Ciranova Open Code"), to use the Ciranova Open Code without        #
# restriction, including without limitation the right to use, copy,    #
# modify, merge, publish, distribute, sublicense, and sell copies of   #
# the Ciranova Open Code, and to permit persons to whom the Ciranova   #
# Open Code is furnished to do so, subject to the following            #
# conditions:                                                          #
#                                                                      #
# The above copyright notice and this permission notice must be        #
# included in all copies and all distribution, redistribution, and     #
# sublicensing of the Ciranova Open Code. THE CIRANOVA OPEN CODE IS    #
# PROVIDED "AS IS" AND WITHOUT WARRANTY OF ANY KIND, EXPRESS, IMPLIED  #
# OR STATUTORY INCLUDING WITHOUT LIMITATION ANY WARRANTY OF            #
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND         #
# NONINFRINGEMENT. IN NO EVENT SHALL CIRANOVA, INC. BE LIABLE FOR ANY  #
# INDIRECT, PUNITIVE, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES     #
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE CIRANOVA OPEN CODE    #
# OR ANY USE OF THE CIRANOVA OPEN CODE, OR BE LIABLE FOR ANY CLAIM,    #
# DAMAGES OR OTHER LIABILITY, HOWEVER IT ARISES AND ON ANY THEORY OF   #
# LIABILITY, WHETHER IN AN ACTION FOR CONTRACT, STRICT LIABILITY OR    #
# TORT (INCLUDING NEGLIGENCE), OR OTHERWISE, ARISING FROM, OUT OF OR   #
# IN CONNECTION WITH THE CIRANOVA OPEN CODE OR ANY USE OF THE          #
# CIRANOVA OPEN CODE. The Ciranova Open Code is subject to U.S.        #
# export control laws and may be subject to export or import           #
# regulations in other countries, and all use of the Ciranova Open     #
# Code must be in compliance with such laws and regulations.  If any   #
# license for the Ciranova Open Code is obtained pursuant to a         #
# government contract, all use, distribution and/or copying by the     #
# U.S. government shall be subject to this permission notice and any   #
# applicable FAR provisions.                                           #
########################################################################

########################################################################
#                                                                      #
# resistorPair.py                                                      #
#                                                                      #
########################################################################

from __future__ import with_statement

from cni.dlo import *
from cni.geo import *
from cni.constants import *
from resistorUnit import *
from cni.integ.common import renameParams, reverseDict
import techUtils


class ResistorPair(DloGen):

    # Portable layer names
    metal1Layer =   ("M1",    "drawing")
    metal2Layer =   ("M2",    "drawing")
    nimpLayer =     ("NIMP",      "drawing")
    pimpLayer =     ("PIMP",      "drawing")
    nwellLayer =    ("NWELL",     "drawing")
    contactLayer =  ("CO",   "drawing")
    rpoLayer =      ("RMARK",       "drawing")

    paramNames = dict(
        wf           = "wf",
        lf           = "lf",
        fr           = "fr",
        rw           = "rw",
        lcontact     = "lcontact",
        wbar         = "wbar",
        connect      = "connect",
        dummies      = "dummies",
        ruleset      = "ruleset",

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

        # also determine minimum contact sizes; note that resistor pairs with
        # "parallel" connection use Metal2 routing, so two contacts are needed.
        (contactWidth, contactLength) = ResistorUnit.getMinimumContactSize(specs.tech, layer)
        (mWidth, mLength) = ResistorUnit.getMetalContactSize(specs.tech, Layer(*cls.metal2Layer), Layer(*cls.metal1Layer))
        contactWidth = max(contactWidth, mWidth)
        contactLength = max(contactLength, mLength)
        barWidth = 2 * specs.tech.getPhysicalRule('minWidth', Layer(*cls.metal1Layer))

        # make sure that resistor body is long enough to allow for 
        # CShape routes used to connect fingers of the resistor pair.
        minSpacing = specs.tech.getPhysicalRule('minSpacing', Layer(*cls.metal1Layer))
        length = max(length, (3*minSpacing + 2*contactLength)) 

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameters for this resistor parameterized cell;
        # note that out-of-range parameter values will be rejected.
        # Since width and length parameter values will be used
        # for routing, these values must lie on even grid points.
        # Note that any route path must be on even grid points.
        gridSize = specs.tech.getGridResolution()
        mySpecs('wf', cls.default.get('wf', width), 
              'width per finger', 
              StepConstraint(2*gridSize, width, None, action=REJECT))
        mySpecs('lf', cls.default.get('lf', length), 
              'length per finger', 
              StepConstraint(2*gridSize, length, None, action=REJECT))
        mySpecs('fr', cls.default.get('fr', 1), 
              'fingers per row',
              RangeConstraint(1, None, REJECT))
        mySpecs('rw', cls.default.get('rw', 1), 
              'number of rows',
              RangeConstraint(1, None, REJECT))
        mySpecs('lcontact', cls.default.get('lcontact', contactLength),
              'length of contacts',
              StepConstraint(2*gridSize, contactLength, None, action=REJECT))
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
            self.width = max(self.width, minWidth)
            self.length = max(self.length, minLength)

            (contactWidth, contactLength) = ResistorUnit.getMinimumContactSize(self.tech, layer)
            self.contactLength = max(self.contactLength, contactLength)

            # lookup portable layer names, and save layer values using class variables
            self.metalLayer = Layer(*self.metal1Layer)
            self.barLayer = self.metalLayer
            self.routeLayer = Layer(*self.metal2Layer)
            self.nimpLayer = Layer(*self.nimpLayer)
            self.pimpLayer = Layer(*self.pimpLayer)
            self.nwellLayer = Layer(*self.nwellLayer)
            self.contactLayer = Layer(*self.contactLayer)

            # define implant layer for doping poly resistors
            if self.implantType == 'N':
                self.implantLayer = self.nimpLayer
            elif self.implantType == 'P':
                self.implantLayer = self.pimpLayer

            # define Resist Protection Oxide layer used to block silicide formation
            if (not self.silicided):
                self.highResLayer = Layer(*self.rpoLayer)

            # define base name which should be used for each resistor unit
            self.baseName = "RES"

            # define number of columns including fingers for both resistors in the pair
            self.columns = 2 * self.fingers



    def genLayout(self):
        # use specified rule set to construct resistor pair
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

        # create bars and required routing
        self.createBars()
        self.createRouting()

        # create implant layer for doping polysilicon or diffusion resistors
        if self.resistorType in ['poly', 'diff']:
            self.createImplant(self.implantLayer)

        # create the device pins for this resistor pair
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
            adjustLength = techUtils.getMinSymmetricExtensionRule(self.tech, self.resistorLayer, self.contactLayer)
            self.length = self.length - 2 * adjustLength
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

        # create resistor unit for this each finger of this resistor pair
        baseUnit = Instance('ResistorUnit', 
                            unitParams, ['A', 'B'], self.baseName)
        baseUnit1 = baseUnit.clone()

        # in order to create an array of these resistor units, first 
        # obtain the DRC correct spacing in each direction; this will
        # be used to place each of the individual resistor units.

        (self.dX, self.dY) = self.calculateXYSpacing(baseUnit, baseUnit1)

        # allow room in the Y-direction for C-Shape routes used for parallel case
        minWidth = min(self.width, self.contactLength)
        if self.connect == "parallel":
            w = (self.width * (self.columns - 1)) + (self.dX * self.columns)
            routeBox = Box(Point(0,0), Point(w, minWidth))
            routeRect = Rect(self.metalLayer, routeBox)
            minSpacing = fgMinSpacing(baseUnit, NORTH, routeRect)
            routeRect.destroy()
            self.dY = self.dY + minWidth + 2 * minSpacing

        # consider routing in the Y-direction.
        # Note that series and parallel connections use different routing.
        if self.connect == "parallel":
            unitParams['contactLength'] = 2 * minWidth + self.dY
        elif self.connect == "series":
            minSpacing = self.tech.getPhysicalRule('minSpacing', self.metalLayer)
            unitParams['contactLength'] = 4 * minWidth + self.barWidth + minSpacing + self.dY
        baseUnit.setParams(unitParams) 
        baseUnit1.setParams(unitParams) 

        (route_dX, route_dY) = self.calculateXYSpacing(baseUnit, baseUnit1)

        self.dX = max(self.dX, route_dX)
        self.dY = max(self.dY, route_dY)

        # consider routing in the X-direction.
        # Note that there are two pairs of Bars involved, 
        # one for metal1 routing and one for metal2 routing.
        if self.dummies:
            unitParams['width'] = 2 * (self.width + self.dX) + 2 * self.barWidth
        else:
            unitParams['width'] = (self.width + self.dX) + 2 * self.barWidth
        baseUnit.setParams(unitParams) 
        baseUnit1.setParams(unitParams) 

        (route_dX, route_dY) = self.calculateXYSpacing(baseUnit, baseUnit1)

        self.dX = max(self.dX, route_dX)
        self.dY = max(self.dY, route_dY)

        unitParams['width'] = self.width
        unitParams['contactLength'] = self.contactLength
        baseUnit.setParams(unitParams)

        # For parallel connection, measure distance between metal2 routing rectangles;
        # this is necessary, since metal1 and metal2 spacing rules may be different.
        if self.connect == "parallel":
            routeWidth = (self.width + self.dX) * self.columns + 2 * self.barWidth
            if self.dummies:
                routeWidth = routeWidth + (self.width + self.dX)
            routeLength = 2 * self.contactLength + self.dY
            routeBox = Box(Point(0,0), Point(routeWidth, routeLength))
            routeRect = Rect(self.routeLayer, routeBox)

            (route_dX, route_dY) = self.calculateXYSpacing(routeRect, routeRect)

            self.dX = max(self.dX, route_dX)
            self.dY = max(self.dY, route_dY)
            routeRect.destroy()


        # since dX and dY values will be used for routing, snap to an even grid point
        grid = Grid(2 * self.tech.getGridResolution())
        self.dX = grid.snap(self.dX, SnapType.ROUND)
        self.dY = grid.snap(self.dY, SnapType.ROUND) 

        # Also calculate required spacing for CShapes and merged CShapes used for routing.
        # For the series case, this is a single CShape between fingers, while for the
        # parallel case, it is a set of merged CShapes between fingers on the same row.
        if self.connect == "series":
            w = 3 * self.width + 2 * self.dX
            routeBox1 = Box(Point(0,0), Point(w, minWidth))
            w = 2 * self.contactLength + self.dY
            routeBox2 = Box(Point(0,0), Point(w, minWidth))
            routeRect1 = Rect(self.metalLayer, routeBox1)
            routeRect2 = Rect(self.metalLayer, routeBox2)
            self.CShapeSpacing = fgMinSpacing(routeRect1, NORTH, routeRect2)
            routeRect1.destroy()
            routeRect2.destroy()
        elif self.connect == "parallel":
            w = (self.width * (self.columns - 1)) + (self.dX * (self.columns - 2))
            routeBox = Box(Point(0,0), Point(w, minWidth))
            routeRect = Rect(self.metalLayer, routeBox)
            self.CShapeSpacing = fgMinSpacing(routeRect, NORTH, routeRect)
            routeRect.destroy()


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
                                      self.rows, self.columns, self.baseName)

        tmpGroup.ungroup()
        baseUnit.destroy()
        baseUnit1.destroy()


        # Check to see if "dummy" resistor units are needed; if so, then create rectangles
        # of the proper size on the layer which is being used to create the resistor units.
        # These dummy resistors are placed at each end of the row of resistor fingers,
        # using the previously calculated spacing value.
        if self.dummies:
            for i in range(self.rows):
                # place dummy resistor at beginning of this row
                unit = self.findInstance(i, 0)
                dummyBox = unit.getBBox(ShapeFilter(self.resistorLayer))
                dummy = Rect(self.resistorLayer, dummyBox)
                place(dummy, Direction.WEST, unit, self.dX)
                # place dummy resistor at the end of this row
                unit = self.findInstance(i, self.columns - 1)
                dummyBox = unit.getBBox(ShapeFilter(self.resistorLayer))
                dummy = Rect(self.resistorLayer, dummyBox)
                place(dummy, Direction.EAST, unit, self.dX)



    def createSilicideBlocks(self):

        # if this is a non-silicided resistor, then we need to add 
        # Resist Protection Oxide layer enclosure rectangle; note that
        # we consider the spacing between contacts and the RPO layer.

        for i in range(self.rows):
            fingerGroup = Grouping('fingerGroup')
            for j in range(self.columns):
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



    def createBars(self):

        resistorStack = self.makeGrouping('resistorStack')

        # construct bars for the resistor routing; these bars are used
        # to simplify routing for both series and parallel connections.
        # In the parallel case, these bars are placed to the left and right,
        # while for the series case, they are placed at the top and bottom.
        # Note that for the series case, these Bars will be removed, after
        # routing has been completed; this avoids routing issues with Bars.

        # note that it is necessary to allow room for the route bars used by
        # C-Shapes for connecting fingers of each of the individual resistors.

        # use length of resistor contacts for width of all routing segments;
        # this route width can not be larger than the width of the resistor.

        minWidth = min(self.width, self.contactLength)

        if self.connect == "parallel":
            w = self.barWidth
            l = resistorStack.getBBox().getHeight()
            self.sourceBar = Bar(self.barLayer, NORTH_SOUTH, 'S', Point(0,0), Point(w,l))
            self.drainBar = Bar(self.barLayer, NORTH_SOUTH, 'D', Point(0,0), Point(w,l))
            fgPlace(self.sourceBar, Direction.WEST, resistorStack)
            fgPlace(self.drainBar, Direction.EAST, resistorStack)
            # also create bars for second metal layer routing
            self.sourceBar2 = Bar(self.routeLayer, NORTH_SOUTH, 'S2', Point(0,0), Point(w,l))
            self.drainBar2 = Bar(self.routeLayer, NORTH_SOUTH, 'D2', Point(0,0), Point(w,l))
            fgPlace(self.sourceBar2, Direction.WEST, self.sourceBar)
            fgPlace(self.drainBar2, Direction.EAST, self.drainBar)
        elif self.connect == "series":
            w = self.barWidth
            l = resistorStack.getBBox().getWidth()
            # also add additional length for LShape and CShape routes to Bar
            l = l +  2 * self.width
            self.sourceBar = Bar(self.barLayer, EAST_WEST, 'S', Point(0,0), Point(l,w))
            self.drainBar = Bar(self.barLayer, EAST_WEST, 'D', Point(0,0), Point(l,w))
            fgPlace(self.sourceBar, Direction.SOUTH, resistorStack)
            fgPlace(self.drainBar, Direction.NORTH, resistorStack)
            # adjust location of these bars to allow for C-Shape routes
            self.sourceBar.moveBy(0, -(self.barWidth + minWidth))
            self.drainBar.moveBy(0, (self.barWidth + minWidth))


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

        # create straight-line route between the contacts for each resistor unit;
        # for "parallel" connection, both top and bottom contacts are connected,
        # but for "series" connection, top and bottom contacts alternate connections.
        # Note that Bars are used to provide connections between rows of resistors
        # for "parallel" connections. Also note that "CShape" routes are used to connect
        # fingers of each resistor in the resistor pair.

        # use length of resistor contacts for width of all routing segments;
        # this route width can not be larger than the width of the resistor.

        minWidth = min(self.width, self.contactLength)

        routeRects = Grouping('routeRects')
        routeCShapes = Grouping('routeCShapes')

        # now connect the appropriate contacts to the Bars
        if self.connect == "parallel":

            # note for odd-numbered rows, the resistor units are flipped,
            # so that the top contact is on the bottom and vice-versa.
            for i in range(self.rows):
                if i % 2 == 1:
                    for j in range(0, self.columns):
                        unit = self.findInstance(i, j)
                        yCoord = unit.getBBox().getCenterY()
                        unit.mirrorX(yCoord)

            # save metal routing rectangles for final Bar placement
            sourceRectList = []
            drainRectList = []
            contactRectList = []
            sourceRectList2 = []
            drainRectList2 = []
        
            # make parallel connections between the outside columns;
            # these are simply metal rectangles between each column.
            # connect top contacts of outside column resistors on top row to Bar
            if (self.rows % 2 == 1):
                fromUnit = self.findInstance(self.rows-1, 0)
                connectBox = Box(fromUnit.findInstPin('B').getBBox().lowerLeft(),
                                 fromUnit.findInstPin('B').getBBox().upperRight())
                # also extend this contact to meet the route Bar
                connectBox.setLeft(self.sourceBar.getRect().getBBox().getLeft())
                connectRect = Rect(self.metalLayer, connectBox)
                # add this route rectangle to the route rectangle group
                routeRects.add(connectRect)
                sourceRectList.append(connectRect)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustRouteEnclosure(connectRect, fromUnit.findInstPin('B'))

                fromUnit = self.findInstance(self.rows-1, self.columns - 1)
                connectBox = Box(fromUnit.findInstPin('B').getBBox().lowerLeft(),
                                 fromUnit.findInstPin('B').getBBox().upperRight())
                # also extend this contact to meet the route Bar
                connectBox.setRight(self.drainBar.getRect().getBBox().getRight())
                connectRect = Rect(self.metalLayer, connectBox)
                # add this route rectangle to the route rectangle group
                routeRects.add(connectRect)
                drainRectList.append(connectRect)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustRouteEnclosure(connectRect, fromUnit.findInstPin('B'))

            # generate metal2 contacts at bottom of all even numbered rows
            # on outside column resistors, and then connect to metal2 Bar.
            for i in range(self.rows-1):
                if (i % 2 == 1):
                    fromUnit = self.findInstance(i, 0)
                    toUnit = self.findInstance(i+1, 0)
                    connectBox = Box(fromUnit.findInstPin('A').getBBox().lowerLeft(),
                                     toUnit.findInstPin('A').getBBox().upperRight())
                    connectContact = Contact(self.metalLayer, self.routeLayer)
                    connectContact.stretch(connectBox)
                    connectRect = Rect(self.routeLayer, connectBox)
                    # add this route rectangle to the Metal2 source route rectangle list
                    sourceRectList2.append(connectRect)

                    fromUnit = self.findInstance(i, self.columns-1)
                    toUnit = self.findInstance(i+1, self.columns-1)
                    connectBox = Box(fromUnit.findInstPin('A').getBBox().lowerLeft(),
                                     toUnit.findInstPin('A').getBBox().upperRight())
                    connectContact = Contact(self.metalLayer, self.routeLayer)
                    connectContact.stretch(connectBox)
                    connectRect = Rect(self.routeLayer, connectBox)
                    # add this route rectangle to the Metal2 drain route rectangle group
                    drainRectList2.append(connectRect)


            # Connect bottom contacts of outside column resistors on bottom row to Bar;
            # note this requires creating metal2 contacts below bottom resistor unit contact.
            # Ensure that metal2 contact can be re-sized to match size of metal1 contact;
            # specify route directions, so that minimum area rules will not be enforced.
            # Note that metal2 minimum area rules will be satisfied after routing.
            unit = self.findInstance(0, 0)
            contactBox = Box(unit.findInstPin('A').getBBox().lowerLeft(),
                             unit.findInstPin('A').getBBox().upperRight())
            # create metal2 contact, using routing directions
            connectContact = Contact(self.metalLayer, self.routeLayer, routeDir1=EAST_WEST, routeDir2=EAST_WEST)
            connectContact.stretch(contactBox)
            connectRect1 = Rect(self.metalLayer, connectContact.getBBox(ShapeFilter(self.metalLayer)))
            connectRect2 = Rect(self.routeLayer, connectContact.getBBox(ShapeFilter(self.routeLayer)))
            # add this route rectangle to the route rectangle group
            routeRects.add(connectRect1)
            # add this route rectangle to the Metal2 source route rectangle list
            sourceRectList2.append(connectRect2)

            unit = self.findInstance(0, self.columns - 1)
            contactBox = Box(unit.findInstPin('A').getBBox().lowerLeft(),
                             unit.findInstPin('A').getBBox().upperRight())
            # create metal2 contact, using routing directions
            connectContact = Contact(self.metalLayer, self.routeLayer, routeDir1=EAST_WEST, routeDir2=EAST_WEST)
            connectContact.stretch(contactBox)
            connectRect1 = Rect(self.metalLayer, connectContact.getBBox(ShapeFilter(self.metalLayer)))
            connectRect2 = Rect(self.routeLayer, connectContact.getBBox(ShapeFilter(self.routeLayer)))
            # add this route rectangle to the route rectangle group
            routeRects.add(connectRect1)
            # add this route rectangle to the Metal2 drain route rectangle list
            drainRectList2.append(connectRect2)

            # connect top contacts of outside column resistors on top row to Bar;
            # note this requires creating metal2 contacts above top resistor unit contact.
            if (self.rows % 2 == 0):
                unit = self.findInstance(self.rows - 1, 0)
                contactBox = Box(unit.findInstPin('A').getBBox().lowerLeft(),
                                 unit.findInstPin('A').getBBox().upperRight())
                # create metal2 contact, using routing directions
                connectContact = Contact(self.metalLayer, self.routeLayer, routeDir1=EAST_WEST, routeDir2=EAST_WEST)
                connectContact.stretch(contactBox)
                connectRect1 = Rect(self.metalLayer, connectContact.getBBox(ShapeFilter(self.metalLayer)))
                connectRect2 = Rect(self.routeLayer, connectContact.getBBox(ShapeFilter(self.routeLayer)))
                # add this route rectangle to the route rectangle group
                routeRects.add(connectRect1)
                # add this route rectangle to the Metal2 source route rectangle list
                sourceRectList2.append(connectRect2)
    
                unit = self.findInstance(self.rows - 1, self.columns - 1)
                contactBox = Box(unit.findInstPin('A').getBBox().lowerLeft(),
                                 unit.findInstPin('A').getBBox().upperRight())
                # create metal2 contact, using routing directions
                connectContact = Contact(self.metalLayer, self.routeLayer, routeDir1=EAST_WEST, routeDir2=EAST_WEST)
                connectContact.stretch(contactBox)
                connectRect1 = Rect(self.metalLayer, connectContact.getBBox(ShapeFilter(self.metalLayer)))
                connectRect2 = Rect(self.routeLayer, connectContact.getBBox(ShapeFilter(self.routeLayer)))
                # add this route rectangle to the route rectangle group
                routeRects.add(connectRect1)
                # add this route rectangle to the Metal2 drain route rectangle list
                drainRectList2.append(connectRect2)


            # make parallel connections between the outside columns;
            # these are simply metal rectangles between each column,
            # which will be used for connecting to Bars.
            for i in range(self.rows-1):

                fromUnit = self.findInstance(i, 0)
                toUnit = self.findInstance(i+1, 0)
                if i % 2 == 0:
                    connectBox = Box(fromUnit.findInstPin('B').getBBox().lowerLeft(),
                                     toUnit.findInstPin('B').getBBox().upperRight())
                    connectRect = Rect(self.metalLayer, connectBox)
                else:
                    connectBox = Box(fromUnit.findInstPin('A').getBBox().lowerLeft(),
                                     toUnit.findInstPin('A').getBBox().upperRight())
                    connectRect = Rect(self.metalLayer, connectBox)
                # also extend this rectangle to meet the route Bar
                if (i % 2 == 0):
                    connectBox.setLeft(self.sourceBar.getRect().getBBox().getLeft())
                    connectRect.setBBox(connectBox)
                    # add this route rectangle to the source route rectangle list
                    sourceRectList.append(connectRect)
                # add this route rectangle to the route rectangle group
                routeRects.add(connectRect)
                # check for additional Metal1 enclosure for resistor unit contact
                if i % 2 == 0:
                    self.adjustRouteEnclosure(connectRect, toUnit.findInstPin('B'))
                else:
                    self.adjustRouteEnclosure(connectRect, toUnit.findInstPin('A'))

                fromUnit = self.findInstance(i, self.columns-1)
                toUnit = self.findInstance(i+1, self.columns-1)
                if i % 2 == 0:
                    connectBox = Box(fromUnit.findInstPin('B').getBBox().lowerLeft(),
                                     toUnit.findInstPin('B').getBBox().upperRight())
                    connectRect = Rect(self.metalLayer, connectBox)
                else:
                    connectBox = Box(fromUnit.findInstPin('A').getBBox().lowerLeft(),
                                     toUnit.findInstPin('A').getBBox().upperRight())
                    connectRect = Rect(self.metalLayer, connectBox)
                # also extend this rectangle to meet the route Bar
                if (i % 2 == 0):
                    connectBox.setRight(self.drainBar.getRect().getBBox().getRight())
                    connectRect.setBBox(connectBox)
                    # add this route rectangle to the drain route rectangle list
                    drainRectList.append(connectRect)
                # add this route rectangle to the route rectangle group
                routeRects.add(connectRect)
                # check for additional Metal1 enclosure for resistor unit contact
                if (i % 2 == 0):
                    self.adjustRouteEnclosure(connectRect, toUnit.findInstPin('B'))
                else:
                    self.adjustRouteEnclosure(connectRect, toUnit.findInstPin('A'))


            # now calculate the spacing which will need to be used by all CShape routes.
            # Note that some CShape routes may be connected to "wide metal", while others
            # may not be; to make all routing consistent, find the largest such spacing.
            unit = self.findInstance(0,0)
            w = minWidth
            l = unit.getBBox().getHeight()
            tempBar = Bar(self.barLayer, Direction.EAST_WEST, 'T', Point(0,0), Point(l,w))
            maxSpacing = 0
            if len(routeRects.getComps()) > 0:
                for shape in routeRects:
                    spacing = fgMinSpacing(tempBar, NORTH, shape)
                    if spacing > maxSpacing:
                        maxSpacing = spacing
            else:
                maxSpacing = fgMinSpacing(tempBar, NORTH, tempBar)
            tempBar.destroy()
            offset = maxSpacing + (self.contactLength + minWidth)/2

            # check that the length of the resistor body is large enough
            # for the two CShape routes, as well as the required minimum
            # metal spacing between these two CShape route objects.
            spacing = 2 * offset + self.CShapeSpacing
            if spacing > self.length:
                raise ValueError, "Length of resistor finger (%s) must be at least %s to satisfy metal1 spacing rules" % \
                                  (str(self.length), str(spacing))

            for i in range(self.rows):
                # make the parallel connections between fingers for this row
                # make connections for the first resistor (using even columns)
                # This is done using an "inside" C-Shape route for top terminal
                # and an "outside" C-Shape route for the bottom terminal.

                for j in range(0, self.columns - 2, 2):
                    fromUnit = self.findInstance(i, j)
                    toUnit = self.findInstance(i, j+2)
                    if i % 2 == 0:
                        # determine position for proper spacing of "outside" CShape for bottom terminal
                        position = fromUnit.findInstPin('A').getBBox().getCenter()
                        position.y = position.y - offset
                        # for all interior rows, merge "outside" CShape objects into single CShape
                        if (i > 0) and (i <= self.rows-1):
                            position.y = fromUnit.getBBox().getBottom() - self.dY/2
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('A'), toUnit.findInstPin('A'), self.metalLayer, position, Direction.SOUTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)
                        # determine position for proper spacing of "inside" CShape for top terminal
                        position = fromUnit.findInstPin('B').getBBox().getCenter()
                        position.y = position.y + offset
                        spacing = position.getSpacing(Direction.NORTH, fromUnit.findInstPin('B').getBBox().getCenter())
                        position2 = Point()
                        position2.place(Direction.SOUTH, fromUnit.findInstPin('B').getBBox().getCenter(), spacing, align=False)
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('B'), toUnit.findInstPin('B'), self.metalLayer, position2, Direction.SOUTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)
                    else:
                        # determine position for proper spacing of "outside" CShape for bottom terminal
                        position = fromUnit.findInstPin('A').getBBox().getCenter()
                        position.y = position.y + offset
                        # for all interior rows, merge "outside" CShape objects into single CShape
                        if (i >= 0) and (i < self.rows-1):
                            position.y = fromUnit.getBBox().getTop() + self.dY/2
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('A'), toUnit.findInstPin('A'), self.metalLayer, position, Direction.NORTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)
                        # determine position for proper spacing of "inside" CShape for top terminal
                        position = fromUnit.findInstPin('B').getBBox().getCenter()
                        position.y = position.y - offset
                        spacing = position.getSpacing(Direction.SOUTH, fromUnit.findInstPin('B').getBBox().getCenter())
                        position2 = Point()
                        position2.place(Direction.NORTH, fromUnit.findInstPin('B').getBBox().getCenter(), spacing, align=False)
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('B'), toUnit.findInstPin('B'), self.metalLayer, position2, Direction.NORTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)
                # make connections for the second resistor (using odd columns)
                # This is done using an "outside" C-Shape route for top terminal
                # and an "inside" C-Shape route for the bottom terminal.
                for j in range(1, self.columns - 2, 2):
                    fromUnit = self.findInstance(i, j)
                    toUnit = self.findInstance(i, j+2)
                    if i % 2 == 0:
                        # determine position for proper spacing of "outside" CShape for top terminal
                        position = fromUnit.findInstPin('B').getBBox().getCenter()
                        position.y = position.y + offset
                        # for all interior rows, merge "outside" CShape objects into single CShape
                        if (i >= 0) and (i < self.rows-1):
                            position.y = fromUnit.getBBox().getTop() + self.dY/2
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('B'), toUnit.findInstPin('B'), self.metalLayer, position, Direction.NORTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)
                        # determine position for proper spacing of "inside" CShape for bottom terminal
                        position = fromUnit.findInstPin('A').getBBox().getCenter()
                        position.y = position.y - offset
                        spacing = position.getSpacing(Direction.SOUTH, fromUnit.findInstPin('A').getBBox().getCenter())
                        position2 = Point()
                        position2.place(Direction.NORTH, fromUnit.findInstPin('A').getBBox().getCenter(), spacing)
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('A'), toUnit.findInstPin('A'), self.metalLayer, position2, Direction.NORTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)
                    else:
                        # determine position for proper spacing of "outside" CShape for top terminal
                        position = fromUnit.findInstPin('B').getBBox().getCenter()
                        position.y = position.y - offset
                        # for all interior rows, merge "outside" CShape objects into single CShape
                        if (i > 0) and (i <= self.rows-1):
                            position.y = fromUnit.getBBox().getBottom() - self.dY/2
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('B'), toUnit.findInstPin('B'), self.metalLayer, position, Direction.SOUTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)
                        # determine position for proper spacing of "inside" CShape for bottom terminal
                        position = fromUnit.findInstPin('A').getBBox().getCenter()
                        position.y = position.y + offset
                        spacing = position.getSpacing(Direction.NORTH, fromUnit.findInstPin('A').getBBox().getCenter())
                        position2 = Point()
                        position2.place(Direction.SOUTH, fromUnit.findInstPin('A').getBBox().getCenter(), spacing)
                        connectCShape = RoutePath.CShape(fromUnit.findInstPin('A'), toUnit.findInstPin('A'), self.metalLayer, position2, Direction.SOUTH, minWidth)
                        # add this CShape route to the route CShape group
                        routeCShapes.add(connectCShape)


        elif self.connect == "series":

            # make the series connections between fingers for the top and bottom rows;
            # first make connections for the first resistor (using even columns), by
            # using an "outside" C-Shape route. Note that we need to save these
            # "outside" C-Shape routes, so that we can align the Bars with them.
            self.topCShape = None
            self.bottomCShape = None
            for j in range(0, self.columns - 2, 2):
                if ((j/2) % 2 == 0):
                    fromUnit = self.findInstance(self.rows-1, j)
                    toUnit = self.findInstance(self.rows-1, j+2)
                    # determine position for proper spacing of "outside" CShape
                    position = self.calculatePosition(fromUnit, Direction.NORTH, minWidth)
                    self.topCShape = RoutePath.CShape(fromUnit.findInstPin('B'), toUnit.findInstPin('B'), self.metalLayer, position, Direction.NORTH, minWidth)
                else:
                    fromUnit = self.findInstance(0, j)
                    toUnit = self.findInstance(0, j+2)
                    # determine position for proper spacing of "outside" CShape
                    position = self.calculatePosition(fromUnit, Direction.SOUTH, minWidth)
                    self.bottomCShape = RoutePath.CShape(fromUnit.findInstPin('A'), toUnit.findInstPin('A'), self.metalLayer, position, Direction.SOUTH, minWidth)
            # make connections for the second resistor (using odd columns)
            # This is done using an "inside" C-Shape route
            for j in range(1, self.columns - 2, 2):
                if ((j/2) % 2 == 0):
                    fromUnit = self.findInstance(self.rows-1, j)
                    toUnit = self.findInstance(self.rows-1, j+2)
                    # determine position for proper spacing of "inside" CShape
                    position = self.calculatePosition(fromUnit, Direction.NORTH, minWidth)
                    spacing = position.getSpacing(Direction.NORTH, fromUnit.findInstPin('B').getBBox().getCenter())
                    position2 = Point()
                    position2.place(Direction.SOUTH, fromUnit.findInstPin('B').getBBox().getCenter(), spacing)
                    RoutePath.CShape(fromUnit.findInstPin('B'), toUnit.findInstPin('B'), self.metalLayer, position2, Direction.SOUTH, minWidth)
                else:
                    fromUnit = self.findInstance(0, j)
                    toUnit = self.findInstance(0, j+2)
                    # determine position for proper spacing of "inside" CShape
                    position = self.calculatePosition(fromUnit, Direction.SOUTH, minWidth)
                    spacing = position.getSpacing(Direction.SOUTH, fromUnit.findInstPin('A').getBBox().getCenter())
                    position2 = Point()
                    position2.place(Direction.NORTH, fromUnit.findInstPin('A').getBBox().getCenter(), spacing)
                    RoutePath.CShape(fromUnit.findInstPin('A'), toUnit.findInstPin('A'), self.metalLayer, position2, Direction.NORTH, minWidth)

            # check that the length of the resistor body is large enough
            # for the "inside" CShape route, as well as the required minimum
            # metal spacing between this CShape route and the contact.
            # Note that there are two CShapes when there is only a single row.
            if self.bottomCShape:
                spacing = self.bottomCShape.getBBox().getHeight() + self.CShapeSpacing
                if self.rows == 1:
                    spacing = spacing + self.bottomCShape.getBBox().getHeight()
                if spacing > self.length:
                    raise ValueError, "Length of resistor finger (%s) must be at least %s to satisfy metal1 spacing rules" % \
                                      (str(self.length), str(spacing))

            # make the series connections between rows
            for i in range(self.rows - 1):
                for j in range(self.columns):
                    fromUnit = self.findInstance(i, j)
                    toUnit = self.findInstance(i + 1, j)
                    RoutePath.StraightLine(fromUnit.findInstPin('B'), 
                                           toUnit.findInstPin('A'), 
                                           self.metalLayer, self.width)  
                    # check for additional Metal1 enclosure for resistor unit contact
                    self.adjustSeriesRouteEnclosure([fromUnit.findInstPin('B'), toUnit.findInstPin('A')], toUnit.findInstPin('A'))

            # connect beginning and ending terminals to Bars. If the number of fingers is even,
            # then the beginning and ending terminals are connected to the bottom Source Bar.
            # If the number of fingers is odd, then the ending terminals are connected to
            # the top Drain Bar, while the beginning terminals are connected to the bottom Bar.
            if (self.fingers % 2 == 0):
                # connect beginning and ending terminals to bottom Bar using StraightLine route;
                # align bottom bar to "outside" CShape, so that metal route tabs do not extend.
                if self.bottomCShape:
                    self.sourceBar.alignEdge(NORTH, self.bottomCShape, SOUTH)
                unit = self.findInstance(0, 0)
                self.routeTab1Plus = RoutePath.StraightLineToBar(unit.findInstPin('A'), 
                                                                 self.sourceBar, 
                                                                 self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([self.routeTab1Plus.getComps()[0], unit.findInstPin('A')], unit.findInstPin('A'))

                unit = self.findInstance(0, 1)
                self.routeTab2Plus = RoutePath.StraightLineToBar(unit.findInstPin('A'), 
                                                                 self.sourceBar, 
                                                                 self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([self.routeTab2Plus.getComps()[0], unit.findInstPin('A')], unit.findInstPin('A'))

                unit = self.findInstance(0, self.columns-2)
                self.routeTab1Minus = RoutePath.StraightLineToBar(unit.findInstPin('A'), 
                                                                  self.sourceBar, 
                                                                  self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([self.routeTab1Minus.getComps()[0], unit.findInstPin('A')], unit.findInstPin('A'))

                unit = self.findInstance(0, self.columns-1)
                self.routeTab2Minus = RoutePath.StraightLineToBar(unit.findInstPin('A'), 
                                                                  self.sourceBar, 
                                                                  self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([self.routeTab2Minus.getComps()[0], unit.findInstPin('A')], unit.findInstPin('A'))

            else:
                # connect beginning terminals to bottom Bar using StraightLine route;
                # align bottom bar to "outside" CShape, so metal route tabs do not extend.
                if self.bottomCShape:
                    self.sourceBar.alignEdge(NORTH, self.bottomCShape, SOUTH)
                unit = self.findInstance(0, 0)
                self.routeTab1Plus = RoutePath.StraightLineToBar(unit.findInstPin('A'), 
                                                                 self.sourceBar, 
                                                                 self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([self.routeTab1Plus.getComps()[0], unit.findInstPin('A')], unit.findInstPin('A'))

                unit = self.findInstance(0, 1)
                self.routeTab2Plus = RoutePath.StraightLineToBar(unit.findInstPin('A'), 
                                                                 self.sourceBar, 
                                                                 self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([self.routeTab2Plus.getComps()[0], unit.findInstPin('A')], unit.findInstPin('A'))

                # connect ending terminals to top Bar using StraightLine route;
                # align top bar to "outside" CShape, so metal route tabs do not extend.
                if self.topCShape:
                    self.drainBar.alignEdge(SOUTH, self.topCShape, NORTH)
                unit = self.findInstance(self.rows-1, self.columns-2)
                self.routeTab1Minus = RoutePath.StraightLineToBar(unit.findInstPin('B'), 
                                                                  self.drainBar, 
                                                                  self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([unit.findInstPin('B'), self.routeTab1Minus.getComps()[0]], unit.findInstPin('B'))

                unit = self.findInstance(self.rows-1, self.columns-1)
                self.routeTab2Minus = RoutePath.StraightLineToBar(unit.findInstPin('B'), 
                                                                  self.drainBar, 
                                                                  self.metalLayer, self.width)
                # check for additional Metal1 enclosure for resistor unit contact
                self.adjustSeriesRouteEnclosure([unit.findInstPin('B'), self.routeTab2Minus.getComps()[0]], unit.findInstPin('B'))



        # After routing has been completed, place the source and drain bars again
        # for the parallel case; this is done to account for any "wide metal"
        # created during routing. In addition, after Bars are placed and the
        # route rectangles are extended, "wide metal" may also be introduced.
        # Thus, it may be necessary to call fgPlace() multiple times. 
        # Simply remove the bars for the series case.

        if self.connect == "parallel":
            resistorStack = Grouping.find('resistorStack')
            # Add all route rectangles to the "resistorStack" grouping
            # for placement of Bars, except for the Source and Drain route
            # rectangles, which are extended to the Source and Drain Bars.
            for rect in routeRects.getComps():
                routeRects.remove(rect)
                resistorStack.add(rect)
            for shape in routeCShapes.getComps():
                routeCShapes.remove(shape)
                resistorStack.add(shape)
            for rect in sourceRectList:
                resistorStack.remove(rect)
            for rect in drainRectList:
                resistorStack.remove(rect)

            while True:
                # first extend route rectangles to meet the source and drain route Bars
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
                fgPlace(self.sourceBar, WEST, resistorStack)
                fgPlace(self.drainBar, EAST, resistorStack)

                # check to see if this placement resulted in any changes;
                # if not, then the placement of Bars has been completed.
                if ((spacing1 == self.sourceBar.getSpacing(WEST, resistorStack)) and
                    (spacing2 == self.drainBar.getSpacing(EAST, resistorStack))):
                    break

            # now place Metal2 Source and Drain Bars, after placing Metal1 Bars
            fgPlace(self.sourceBar2, Direction.WEST, self.sourceBar)
            fgPlace(self.drainBar2, Direction.EAST, self.drainBar)

            # extend Metal2 route rectangles to meet the Metal2 source and drain route Bars
            for rect in sourceRectList2:
                connectBox = rect.getBBox()
                connectBox.setLeft(self.sourceBar2.getRect().getBBox().getLeft())
                rect.setBBox(connectBox)
            for rect in drainRectList2:
                connectBox = rect.getBBox()
                connectBox.setRight(self.drainBar2.getRect().getBBox().getRight())
                rect.setBBox(connectBox)

        elif self.connect == "series":
            self.sourceBar.destroy()
            self.drainBar.destroy()



    def createPins(self):

        # Create the device pins for this resistor pair, based upon the connection type.
        # If the connection type is "series", then use the route tabs on the beginning
        # and ending resistor units; if "parallel", then use the two route bars.

        if self.connect == "series":
            # use the route tabs for beginning and ending resistor units to create pins
            self.addPin('PLUS1', 'PLUS1', 
                        self.routeTab1Plus.getBBox(),
                        self.metalLayer)
            self.addPin('MINUS1', 'MINUS1', 
                        self.routeTab1Minus.getBBox(),
                        self.metalLayer)
            self.addPin('PLUS2', 'PLUS2', 
                        self.routeTab2Plus.getBBox(),
                        self.metalLayer)
            self.addPin('MINUS2', 'MINUS2', 
                        self.routeTab2Minus.getBBox(),
                        self.metalLayer)

        elif self.connect == "parallel":
            # use the bars created for parallel routing to create pins
            self.addPin('PLUS1', 'PLUS1', self.sourceBar.getBBox(), self.barLayer)
            self.addPin('MINUS1', 'MINUS1', self.drainBar.getBBox(), self.barLayer)
            self.addPin('PLUS2', 'PLUS2', self.sourceBar2.getBBox(), self.routeLayer)
            self.addPin('MINUS2', 'MINUS2', self.drainBar2.getBBox(), self.routeLayer)

        # Remove extra nets which were only used during device construction;
        # the 'A' and 'B' instance terminals for resistor units are required
        # to access the contacts for connection of individual resistor units.
        for netName in ['A', 'B']:
            if Net.find(netName):
                Net.find(netName).destroy()



    def  findInstance(self, i, j):
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
            dX = fgMinSpacing(baseUnit, Direction.EAST,
                              baseUnit1, env = tmpGroup.getComps()[0])
            dY = fgMinSpacing(baseUnit, Direction.NORTH, 
                              baseUnit1, env = tmpGroup.getComps()[0])
            tmpGroup.destroy()
        else:
            dX = fgMinSpacing(baseUnit, Direction.EAST, baseUnit1)
            dY = fgMinSpacing(baseUnit, Direction.NORTH, baseUnit1)
        return(dX, dY)



    def calculatePosition(self, unit, direction, width):
        # calculate proper spacing to be used for CShape objects.
        # this is done by creating a temporary Bar, and then
        # using fgPlace() to place it from the resistor units.
        # The position point is the center point of the Bar;
        # note that only the coordinate in the specified direction is used.
        w = width
        l = unit.getBBox().getHeight()
        if (direction == Direction.NORTH or direction == Direction.SOUTH):
            tempBar = Bar(self.barLayer, Direction.EAST_WEST, 'T', Point(0,0), Point(l,w))
        elif (direction == Direction.EAST or direction == Direction.WEST):
            tempBar = Bar(self.barLayer, Direction.NORTH_SOUTH, 'T', Point(0,0), Point(w,l))
        fgPlace(tempBar, direction, unit)
        position = tempBar.getBBox().getCenter()
        tempBar.destroy()
        return(position)



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

        # adjust the routing rectangle as needed
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



# Define derived classes for various types of resistor pairs;
# these classes implement the different types of resistor pairs
# for the PyCell library.
#
# These resistor pairs include the following types:
#
#  silicided N-type Poly resistor pair 
#  silicided P-type Poly resistor pair 
#  silicided N-type Diffusion resistor pair 
#  silicided P-type Diffusion resistor pair 
#  un-silicided N-type Poly resistor pair 
#  un-silicided P-type Poly resistor pair 
#  un-silicided N-type Diffusion resistor pair 
#  un-silicided P-type Diffusion resistor pair
#
#
# Note that all of these different types of resistor pairs are generated
# by setting the appropriate parameter values for the base ResistorPair class.
# Note that these three additional parameter values are added to the
# ParamArray which is then passed to the base Resistor Pair class.
# In order to do so, we only need to override the single "setupParams()"
# method on the base ResistorPair class; all other methods are not overridden.
#
#

class SilNPolyResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'N'
        params['silicided'] = True
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class SilPPolyResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'P'
        params['silicided'] = True
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class SilNDiffResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'diff'
        params['implantType'] = 'N'
        params['silicided'] = True
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class SilPDiffResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'diff'
        params['implantType'] = 'P'
        params['silicided'] = True
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class unSilNPolyResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'N'
        params['silicided'] = False
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class unSilPPolyResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'poly'
        params['implantType'] = 'P'
        params['silicided'] = False
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class unSilNDiffResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'diff'
        params['implantType'] = 'N'
        params['silicided'] = False
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class unSilPDiffResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'diff'
        params['implantType'] = 'P'
        params['silicided'] = False
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)


class NWellResPair(ResistorPair):

    def setupParams(self, params):
        # set the necessary parameter values
        params['resistorType'] = 'nwell'
        params['implantType'] = 'None'
        params['silicided'] = True
        # call method on base Resistor Pair class
        ResistorPair.setupParams(self, params)

