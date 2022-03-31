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
# combCapacitor.py                                                     #
#                                                                      #
########################################################################

from __future__ import with_statement

import math
from cni.dlo import *
from cni.geo import *
from cni.constants import *
from cni.integ.common import renameParams, reverseDict
import techUtils

# tolerance factor for performing floating-point comparisons
epsilon = 1e-5

# base class for single multi-metal layered comb capacitor

class CombCapacitor(DloGen):
    paramNames = dict(
        wf               = "wf",
        lf               = "lf",
        nf               = "nf",

        topLayer         = "topLayer",
        bottomLayer      = "bottomLayer",

        bottomShield     = "bottomShield",

        ruleset          = "ruleset",
        dummies          = "dummies",
    )

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs    = ParamSpecArray()

        # use variables to set default values for parameters

        # check for maximum number of metal layers from tech file
        maxMetalLayerIndex = techUtils.getNumMetalLayers(mySpecs.tech)

        # use metal layer index values to generate sorted list
        # of metal layers which will be used by comb capacitor.
        metalLayers = techUtils.getMetalLayers(mySpecs.tech, 1, 5)

        # obtain minimum width and length values using the minimum via sizes
        # for the default metal layers which are used for the comb capacitor
        (width, length) = getMaxViaSize(mySpecs.tech, metalLayers)

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameters for this comb capacitor parameterized cell;
        # note that out-of-range parameter values will be rejected.
        gridSize = specs.tech.getGridResolution()
        mySpecs('wf', cls.default.get('wf', width),
              'width per finger', 
              StepConstraint(gridSize, width, None, action=REJECT))
        mySpecs('lf', cls.default.get('lf', 2.0),
              'length per finger', 
              StepConstraint(gridSize, length, None, action=REJECT))
        mySpecs('nf', cls.default.get('nf', 4), 
              'number of fingers per bottom terminal per layer',
              RangeConstraint(1, None, REJECT))

        # use maximum number of metal layers for range constraint upper value
        mySpecs('topLayer', cls.default.get('topLayer', min(5, maxMetalLayerIndex)), 
              'Top metal layer index',
              RangeConstraint(1, maxMetalLayerIndex, REJECT))
        mySpecs('bottomLayer', cls.default.get('bottomLayer', 1), 
              'Bottom metal layer index',
              RangeConstraint(1, maxMetalLayerIndex, REJECT))

        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
              'Ruleset type (construction or recommended)',
              ChoiceConstraint(['construction', 'recommended']))                        

        mySpecs('bottomShield', cls.default.get('bottomShield', True), 'Bottom metal layer constructed as shield plate')
        mySpecs('dummies', cls.default.get('dummies', True), 'Generate dummy metal fingers around structure')

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)



    def setupParams(self, params):

        # Parameter renaming
        self.paramNamesReversed = reverseDict( self.paramNames)
        myParams = ParamArray()
        renameParams( params, myParams, self.paramNamesReversed)

        # save parameter values using class variables
        self.width = myParams['wf']
        self.length = myParams['lf']
        self.fingers = myParams['nf']
        self.topLayerIndex = myParams['topLayer']
        self.bottomLayerIndex = myParams['bottomLayer']
        self.bottomShield = myParams['bottomShield']
        self.ruleset = myParams['ruleset']
        self.dummies = myParams['dummies']
    
        # set up ruleset to be used during device construction
        rulesets = ['construction', 'default']
        if self.ruleset == 'recommended':
            rulesets.insert(0, 'recommended')
        self.ruleset = techUtils.orderedRuleset(self.tech, rulesets)

        # use any specified rule set to calculate minimum values
        with RulesetManager(self.tech, self.ruleset):

            # check that bottom metal layer index <= top metal layer index;
            # these can only be equal, if no bottom shield layer is used.
            if self.bottomLayerIndex > self.topLayerIndex:
                raise RuntimeError("topLayer (%d) must be greater than or equal to bottomLayer (%d)"\
                                     % (self.topLayerIndex, self.bottomLayerIndex))

            if self.bottomLayerIndex == self.topLayerIndex:
                # can not use bottom shield layer
                if self.bottomShield:
                    raise RuntimeError("can not use bottomShield, unless topLayer is greater than bottomLayer")

            # use metal layer index values to generate sorted list
            # of metal layers which will be used by comb capacitor.
            self.metalLayers = techUtils.getMetalLayers(self.tech, self.bottomLayerIndex, self.topLayerIndex)

            # readjust width and length parameter values, since the actual
            # minimum values may be different; use the minimum via sizes
            # for all of these metal layers to calculate minimum values.
            (maxWidth, maxLength) = getMaxViaSize(self.tech, self.metalLayers)
            self.width = max(self.width, maxWidth)
            self.length = max(self.length, maxLength)

            # calculate proper abut via spacing factor for abutting contacts
            self.calculateAbutViaSpaceFactor()

            # Calculate the minimum DRC correct spacing between fingers.
            # Note that the total finger length incorporates this finger spacing.
            # In addition, the total finger length affects the spacing between vias.
            # Thus, it may be necessary to calculate finger spacing multiple times.
            self.fingerSpacing = 0
            while True:
                spacing = self.fingerSpacing
                self.calculateFingerSpacing()
                if spacing == self.fingerSpacing:
                    break



    def genLayout(self):
        # use specified rule set to construct capacitor
        with RulesetManager(self.tech, self.ruleset):
            self.construct()


    def construct(self):

        # create Bars for terminal1 and terminal2 on each metal layer
        self.createTerminalBars()

        # check if bottom metal layer is being used as a shield plate layer;
        # if so, generate special shield structure on the bottom metal layer.
        if self.bottomShield:
            self.createShield()

        # now create fingers on each of the different metal layers
        self.createFingers()

        # check to see if dummy fingers should be created
        if self.dummies:
            self.createDummies()

        # create pins for each terminal
        self.createPins()


    def getConservativeViaSpacing(self, cutLayer):
        # Returns the most conservative via spacing for the cut layer.
        # Checks for regular and all conditional via spacing rules.
        result = None
        
        # standard 'minSpacing' rule
        if self.tech.physicalRuleExists('minSpacing', cutLayer):
            rule = self.tech.getPhysicalRule('minSpacing', cutLayer)
            result = float(rule)
            
        # standard 'minAdjacentViaSpacing' rule
        if self.tech.physicalRuleExists('minAdjacentViaSpacing', cutLayer):
            rule = self.tech.getPhysicalRule('minAdjacentViaSpacing', cutLayer)
            minAdjacentViaSpacing = float(rule)
            result = max(minAdjacentViaSpacing, result)
                  
        # standard 'minLargeViaArrayCutSpacing' rule
        if self.tech.physicalRuleExists('minLargeViaArrayCutSpacing', cutLayer):
            rule = self.tech.getPhysicalRule('minLargeViaArrayCutSpacing', cutLayer)
            minLargeViaArrayCutSpacing = float(rule)
            result = max(minLargeViaArrayCutSpacing, result)
      
        # enable this part for backward compatibility with old techfiles
        # non-standard 'minSpacing' rule with 'neighbours' parameter
        ##if self.tech.conditionalRuleExists('minSpacing', cutLayer, ['neighbours']):
        ##    spacing = self.tech.getPhysicalRule('minSpacing', cutLayer, params={'neighbours':4})
        ##    result = max(spacing, result)
                
        return result
    
    def calculateAbutViaSpaceFactor(self):
        # check to see if there are conditional via spacing rules defined
        # for this technology. If so, then we need to adjust the abut via
        # spacing factor for the AbutContact which is used for the bars
        # and fingers of this comb capacitor. This adjustment is calculated
        # by determining the ratio between the most conservative rule value
        # and the regular via spacing design rule. This is done for each
        # metal layer, and the maximum ratio value is used to calculate
        # the abut via spacing factor to be used for all abut contacts.
        
        # first find all of the via layers
        viaLayers = self.tech.getIntermediateLayers(self.metalLayers[0], self.metalLayers[-1])[1]

        # check to see if there are conditional via spacing rules defined for these via layers
        maxViaSpacingRatio = 0
        for layer in viaLayers:
            viaSpacing = self.getConservativeViaSpacing(layer)
            minSpacing = self.tech.getPhysicalRule('minSpacing', layer)
            if viaSpacing > minSpacing:
                viaSpacingRatio = viaSpacing / minSpacing
                if viaSpacingRatio > maxViaSpacingRatio:
                    maxViaSpacingRatio = viaSpacingRatio

        # calculate the maximum abut via spacing factor for the AbutContact
        if maxViaSpacingRatio > 1.0:
            self.abutViaSpaceFactor = int(math.ceil(2 * maxViaSpacingRatio))
        else:
           self.abutViaSpaceFactor = 2



    def calculateFingerSpacing(self):
        # calculate minimum spacing between fingers, using fgMinSpacing().
        # In order to ensure that all "via spacing" design rules
        # are invoked, it is necessary to construct two abut contacts with vias.
        # The minimum DRC-correct spacing will be calculated for each layer,
        # and then the maximum of these values will be use to explicitly place
        # the comb fingers on each layer. Note that this is done to generate
        # a very regular structure, versus having a more optimal structure
        # which uses the minimal spacing for each metal layer.
        w = self.width
        l = self.length + self.fingerSpacing
        for i in range(len(self.metalLayers)):
            layer = self.metalLayers[i]
            # if this is not the top metal layer, create via to metal layer above this one
            if layer != self.metalLayers[-1]:
                contact1 = AbutContact(layer, self.metalLayers[i+1], 
                                       routeDir1=NORTH_SOUTH, routeDir2=NORTH_SOUTH, 
                                       abutDir=NORTH, abutViaSpaceFactor=self.abutViaSpaceFactor, 
                                       point1=Point(0,0), point2=Point(w,l))
                contact2 = AbutContact(layer, self.metalLayers[i+1], 
                                       routeDir1=NORTH_SOUTH, routeDir2=NORTH_SOUTH, 
                                       abutDir=NORTH, abutViaSpaceFactor=self.abutViaSpaceFactor, 
                                       point1=Point(0,0), point2=Point(w,l))
                spacing = fgMinSpacing(contact1, EAST, contact2)
                if spacing > self.fingerSpacing:
                    self.fingerSpacing = spacing
                # check to see that created contacts have the requested length and width;
                # if not, generate error that user will need to adjust parameter values.
                minWidth = max(contact1.getBBox().getWidth(), contact2.getBBox().getWidth())
                if ((minWidth - self.width) > epsilon):
                    raise ValueError, "Width of capacitor finger (%s) must be at least %s to satisfy %s/%s via spacing rules" % \
                                      (str(self.width), str(minWidth), str(self.metalLayers[i]), str(self.metalLayers[i+1]))
                minLength = max(contact1.getBBox().getHeight(), contact2.getBBox().getHeight())
                minLength = minLength - self.fingerSpacing
                if ((minLength - self.length) > epsilon):
                    raise ValueError, "Length of capacitor finger (%s) must be at least %s to satisfy %s/%s via spacing rules" % \
                                      (str(self.length), str(minLength), str(self.metalLayers[i]), str(self.metalLayers[i+1]))
                # also check for possible "wide metal" spacing between fingers and terminal bars;
                # this is done by creating "dummy" terminal contacts for use with fgMinSpacing().
                # This also handles all via spacing rules as well as wide metal rules.
                if self.dummies:
                    barLength = w * (self.fingers + 2) + self.fingerSpacing * (self.fingers + 1)
                else:
                    barLength = w * (self.fingers) + self.fingerSpacing * (self.fingers - 1)
                dummyContact = Contact(layer, self.metalLayers[i+1],
                                       routeDir1=EAST_WEST, routeDir2=EAST_WEST, 
                                       point1=Point(0,0), point2=Point(barLength,w))
                spacing = fgMinSpacing(dummyContact, NORTH, dummyContact)
                if spacing > self.fingerSpacing:
                    self.fingerSpacing = spacing
                contact1.destroy()
                contact2.destroy()
                dummyContact.destroy()
            else:
                # since no via required, just use Bars to measure minimum spacing
                bar1 = Bar(layer, NORTH_SOUTH, 'B1', Point(0,0), Point(w,l))
                bar2 = Bar(layer, NORTH_SOUTH, 'B2', Point(0,0), Point(w,l))
                spacing = fgMinSpacing(bar1, EAST, bar2)
                if spacing > self.fingerSpacing:
                    self.fingerSpacing = spacing
                # check to see that created bars have the requested length and width;
                # if not, generate error that user will need to adjust parameter values.
                minWidth = max(bar1.getBBox().getWidth(), bar2.getBBox().getWidth())
                if ((minWidth - self.width) > epsilon):
                    raise ValueError, "Width of capacitor finger (%s) must be at least %s to satisfy %s minimum width rules" % \
                                      (str(self.width), str(minWidth), str(self.metalLayers[i]))
                minLength = max(bar1.getBBox().getHeight(), bar2.getBBox().getHeight())
                minLength = minLength - self.fingerSpacing
                if ((minLength - self.length) > epsilon):
                    raise ValueError, "Length of capacitor finger (%s) must be at least %s to satisfy %s minimum area rules" % \
                                      (str(self.length), str(minLength), str(self.metalLayers[i]))
                # also check for possible "wide metal" spacing between fingers and terminal bars;
                # this is done by creating "dummy" terminal bars for use with fgMinSpacing().
                if self.dummies:
                    barLength = w * (self.fingers + 2) + self.fingerSpacing * (self.fingers + 1)
                else:
                    barLength = w * (self.fingers) + self.fingerSpacing * (self.fingers - 1)
                dummyBar = Bar(layer, EAST_WEST, 'D0', Point(0,0), Point(barLength,w))
                spacing = fgMinSpacing(dummyBar, NORTH, bar1)
                if spacing > self.fingerSpacing:
                    self.fingerSpacing = spacing
                bar1.destroy()
                bar2.destroy()
                dummyBar.destroy()


        # also check that no metal minimum enclosed area rules will be violated;
        # this specific DRC design rule check is currently required, since the
        # FG methods do not automatically interpret the DRC "HOLES" operation.
        # Note that this is only necessary, if the bottom shield is being used.
        if self.bottomShield:
            layer = self.metalLayers[0]
            if self.tech.physicalRuleExists('minEnclosedArea', layer):
                minArea = self.tech.getPhysicalRule('minEnclosedArea', layer)
                w = self.fingerSpacing
                l = self.length + 2 * self.fingerSpacing
                if (minArea > (w * l)):
                    box1 = Box(Point(0,0), Point(w,l))
                    grid = Grid(self.tech.getGridResolution())
                    box1.expandForMinArea(EAST, minArea, grid)
                    self.fingerSpacing = box1.getWidth()


    def createTerminalBars(self):

        for i in range(len(self.metalLayers)):
            layer = self.metalLayers[i]
            w = self.width
            totalFingers = 2 * self.fingers + 1
            # also add room for possible dummy fingers on each end
            totalFingers = totalFingers + 2 
            l = self.width * totalFingers + self.fingerSpacing * (totalFingers - 1) 
            self.term1Bar = Bar(layer, EAST_WEST, 'T1', Point(0,0), Point(l,w))
            self.term2Bar = Bar(layer, EAST_WEST, 'T2', Point(0,0), Point(l,w))
            # place terminal1 Bar at the top, terminal2 Bar at the bottom
            place(self.term1Bar, NORTH, self.term2Bar, self.length + 2 * self.fingerSpacing)
            # if this is not the top metal layer, create via to metal layer above this one
            if layer != self.metalLayers[-1]:
                contact1 = Contact(layer, self.metalLayers[i+1],
                                   routeDir1=EAST_WEST, routeDir2=EAST_WEST, 
                                   point1=Point(0,0), point2=Point(l,w))
                contact1.alignLocation(Location.UPPER_LEFT, self.term1Bar)
                # if this is not the bottom shield layer, also create via for terminal2
                if not(self.bottomShield and i == 0):
                    contact2 = Contact(layer, self.metalLayers[i+1], 
                                       routeDir1=EAST_WEST, routeDir2=EAST_WEST, 
                                       point1=Point(0,0), point2=Point(l,w))
                    contact2.alignLocation(Location.UPPER_LEFT, self.term2Bar)


    def  createShield(self):

        # generate only a single comb on the bottom metal layer, 
        # where the comb fingers connect the top and bottom bars.
        # Note that a Bar is used to connect the two terminal bars,
        # while a contact is used to create the vias to the upper
        # metal layer. This contact will be the same size as the
        # contacts used on all metal layers above this shield layer.
        layer = self.metalLayers[0]
        for i in range(2* self.fingers+1):
            # first create bar to connect both terminals
            w = self.width
            l = self.length + 2 * self.fingerSpacing
            bar1 = Bar(layer, NORTH_SOUTH, 'B1', Point(0,0), Point(w,l))
            # abut this bar just below terminal1 Bar
            place(bar1, SOUTH, self.term1Bar, 0)
            alignEdge(bar1, WEST, self.term1Bar)
            # place this finger to the right of previous finger
            bar1.moveBy((i+1) * (self.width + self.fingerSpacing), 0)
            # create contact needed to connect to the next metal layer;
            # note this contact is only used by fingers for terminal1.
            if (i % 2 == 0):
                l = self.length + self.fingerSpacing
                contact1 = AbutContact(layer, self.metalLayers[1],
                                       routeDir1=NORTH_SOUTH, routeDir2=NORTH_SOUTH,
                                       abutDir=NORTH, abutViaSpaceFactor=self.abutViaSpaceFactor,
                                       point1=Point(0,0), point2=Point(w,l))
                # align contact to top bar
                contact1.alignLocation(Location.UPPER_LEFT, bar1)


    def  createFingers(self):
        # now generate the fingers for each comb on each metal layer
        for i in range(len(self.metalLayers)):
            # ignore bottom layer, if it was used to create a shield
            if self.bottomShield and i == 0:
                continue
            layer = self.metalLayers[i]
            # generate fingers for terminal1 comb
            for j in range(self.fingers+1):
                w = self.width
                l = self.length + self.fingerSpacing
                bar1 = Bar(layer, NORTH_SOUTH, 'B1', Point(0,0), Point(w,l))
                # if this is not the top metal layer, create via to metal layer above this one
                if layer != self.metalLayers[-1]:
                    contact1 = AbutContact(layer, self.metalLayers[i+1], 
                                           routeDir1=NORTH_SOUTH, routeDir2=NORTH_SOUTH, 
                                           abutDir=NORTH, abutViaSpaceFactor=self.abutViaSpaceFactor, 
                                           point1=Point(0,0), point2=Point(w,l))
                # abut this bar just below terminal1 Bar
                bar1.abut(SOUTH, self.term1Bar)
                bar1.alignEdge(WEST, self.term1Bar)
                # place this finger to the right of previous finger
                bar1.moveBy(self.width + self.fingerSpacing, 0)
                bar1.moveBy(j*(2* self.width + 2 * self.fingerSpacing), 0)
                if layer != self.metalLayers[-1]:
                    contact1.alignLocation(Location.UPPER_LEFT, bar1)
            # generate fingers for terminal2 comb
            for j in range(self.fingers):
                w = self.width
                l = self.length + self.fingerSpacing
                bar2 = Bar(layer, NORTH_SOUTH, 'B2', Point(0,0), Point(w,l))
                # if this is not the top metal layer, create via to metal layer above this one
                if layer != self.metalLayers[-1]:
                    contact2 = AbutContact(layer, self.metalLayers[i+1],
                                           routeDir1=NORTH_SOUTH, routeDir2=NORTH_SOUTH, 
                                           abutDir=SOUTH, abutViaSpaceFactor=self.abutViaSpaceFactor, 
                                           point1=Point(0,0), point2=Point(w,l))
                # abut this bar just above terminal2 Bar
                bar2.abut(NORTH, self.term2Bar)
                bar2.alignEdge(WEST, self.term2Bar)
                # place this finger to the right of previous finger
                bar2.moveBy(2*(self.width + self.fingerSpacing), 0)
                bar2.moveBy(j*(2 * self.width + 2 * self.fingerSpacing), 0)
                if layer != self.metalLayers[-1]:
                    contact2.alignLocation(Location.UPPER_LEFT, bar2)


    def createDummies(self):

        # add any dummies at the top, bottom and sides
        if self.dummies:
            for i in range(len(self.metalLayers)):
                layer = self.metalLayers[i]
                # first place dummies at the top and bottom
                w = self.width
                totalFingers = 2 * self.fingers + 1
                totalFingers = totalFingers + 2  # add dummies on each end
                l = self.width * totalFingers + self.fingerSpacing * (totalFingers - 1) 
                dummyBar1 = Bar(layer, EAST_WEST, 'D1', Point(0,0), Point(l,w))
                # if this is not the top metal layer, create via to metal layer above this one
                if layer != self.metalLayers[-1]:
                    dummyContact1 = Contact(layer, self.metalLayers[i+1], 
                                            routeDir1=EAST_WEST, routeDir2=EAST_WEST, 
                                            point1=Point(0,0), point2=Point(l,w))
                place(dummyBar1, NORTH, self.term1Bar, self.fingerSpacing)
                if layer != self.metalLayers[-1]:
                    dummyContact1.alignLocation(Location.UPPER_LEFT, dummyBar1)
                dummyBar2 = dummyBar1.clone()
                if layer != self.metalLayers[-1]:
                     dummyContact2 = dummyContact1.clone()
                place(dummyBar2, SOUTH, self.term2Bar, self.fingerSpacing)
                if layer != self.metalLayers[-1]:
                    dummyContact2.alignLocation(Location.UPPER_LEFT, dummyBar2)
                # now place dummies at the left and right sides.
                # Note that rectangles are used for these dummies, 
                # and that minimum area checks are made on each layer.
                # This is needed to expand dummies in the required direction,
                # as the Bar expands for minimum area in the bar direction.
                w = self.width
                l = self.length
                dummyRect = Rect(layer, Box(Point(0,0), Point(w,l)))
                if self.tech.physicalRuleExists('minArea', layer):
                    minArea = self.tech.getPhysicalRule('minArea', layer)
                    # make sure that this rectangle for the dummy lies on grid points
                    grid = Grid(self.tech.getGridResolution())
                    dummyRect.setBBox(dummyRect.getBBox().expandForMinArea(WEST, minArea, grid))
                # if this is not the top metal layer, create via to metal layer above this one
                if layer != self.metalLayers[-1]:
                    dummyContact = Contact(layer, self.metalLayers[i+1], 
                                           routeDir1=NORTH_SOUTH, routeDir2=NORTH_SOUTH, 
                                           point1=Point(0,0), point2=Point(w,l))
                dummyRect.moveBy(0, self.width + self.fingerSpacing)
                if layer != self.metalLayers[-1]:
                    dummyContact.alignLocation(Location.UPPER_LEFT, dummyRect)
                dummyRect = Rect(layer, Box(Point(0,0), Point(w,l)))
                if self.tech.physicalRuleExists('minArea', layer):
                    minArea = self.tech.getPhysicalRule('minArea', layer)
                    # make sure that this rectangle for the dummy lies on grid points
                    grid = Grid(self.tech.getGridResolution())
                    dummyRect.setBBox(dummyRect.getBBox().expandForMinArea(EAST, minArea, grid))
                # if this is not the top metal layer, create via to metal layer above this one
                if layer != self.metalLayers[-1]:
                    dummyContact = Contact(layer, self.metalLayers[i+1], 
                                           routeDir1=NORTH_SOUTH, routeDir2=NORTH_SOUTH, 
                                           point1=Point(0,0), point2=Point(w,l))
                dummyRect.moveBy(0, self.width + self.fingerSpacing)
                dummyRect.moveBy((2 * self.fingers + 2) * (self.width + self.fingerSpacing), 0)
                if layer != self.metalLayers[-1]:
                    dummyContact.alignLocation(Location.UPPER_LEFT, dummyRect)
            

    def createPins(self):
        # Add pins for each ternminal, using the bars created on each layer.
        # Note that shapes for pins are created on all layers, and the pin
        # geometry is the width and length of each entire terminal Bar.
        # This approach provides maximum flexibility for the router.

        # create the plus and minus pins for the two terminals
        pin1 = Pin('MINUS', 'MINUS')
        pin2 = Pin('PLUS', 'PLUS')

        # add necessary shapes on each metal layer for these pins
        for i in range(len(self.metalLayers)):
            layer = self.metalLayers[i]
            # only create pin shape on terminal1 for bottom layer, 
            # if this bottom layer was used to create a shield.
            if self.bottomShield and i == 0:
                term1Rect = Rect(layer, self.term1Bar.getBBox())
                pin1.addShape(term1Rect)
            else:
                # create pins for both termonals on this layer
                term1Rect = Rect(layer, self.term1Bar.getBBox())
                pin1.addShape(term1Rect)
                term2Rect = Rect(layer, self.term2Bar.getBBox())
                pin2.addShape(term2Rect)

def getMinimumViaSize(tech, layer1, layer2):
    # create default via using design rules specified in technology file;
    # use this via to determine default via width and length values.
    # tech - technology object for design rule lookup
    # layer1 - lower metal layer
    # layer2 - upper metal layer

    # first create default via/contact between two layers
    via = Contact(layer1, layer2, routeDir1 = NORTH_SOUTH, routeDir2 = NORTH_SOUTH)
    viaWidth = via.getBBox().getWidth()
    viaHeight = via.getBBox().getHeight()
    via.destroy() 

    return(viaWidth, viaHeight)


def getMaxViaSize(tech, metalLayers):
    # use a single contact between bottom layer and top layer
    # to determine the minimum via sizes for all metal layers

    if len(metalLayers) == 1:
        # if there is a single layer, then there are no vias required;
        # in this case, just use minimum width for this single metal layer.
        if tech.physicalRuleExists('minWidth', metalLayers[0]):
            maxWidth = tech.getPhysicalRule('minWidth', metalLayers[0])
            maxLength = maxWidth
    else:
        (maxWidth, maxLength) = getMinimumViaSize(tech, metalLayers[0], metalLayers[-1])

    return(maxWidth, maxLength)

