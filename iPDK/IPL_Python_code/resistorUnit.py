########################################################################
# Copyright (c) 2001-2008 by Ciranova, Inc. All rights reserved.          #
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
# resistorUnit.py                                                      #
#                                                                      #
########################################################################

from __future__ import with_statement

from cni.dlo import *
from cni.geo import *
from cni.constants import *
from cni.integ.common import renameParams, reverseDict
from techUtils import (
    deviceContextExists,
    getMinExtensionRule,
    getMinClearanceRule
)

class ResistorUnit(DloGen):

    # Portable layer names
    polyLayer =     ("PO",     "drawing")
    metal1Layer =   ("M1",    "drawing" )
    nimpLayer =     ("NIMP",      "drawing")
    pimpLayer =     ("PIMP",      "drawing")
    nwellLayer =    ("NWELL",     "drawing")
    diffLayer =     ("DIFF",      "drawing")
    contactLayer =  ("CO",   	  "drawing")
    rpoLayer =      ("RMARK",       "drawing")

    paramNames = dict(
        resistorType  = "resistorType",
        width         = "width",
        length        = "length",
        contactLength = "contactLength",
        silicided     = "silicided",
        deviceContext = "deviceContext",
        ruleset       = "ruleset",
    )

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # use variables to set default values for all parameters

        resistorType = 'poly'
        layer = cls.getContactLayer(resistorType)

        # check to see if there are device specific minimum values defined 
        # in the technology file; if not, then just use minimum width value
        # defined for layer on which the resistor will be created. 
        # Use poly resistor type to calculate default values; these values
        # may be overwritten, once the user has specified the resistor type.

        (width, length) = cls.getMinimumResistorSize(True, specs.tech, resistorType)
        (contactWidth, contactLength) = cls.getMinimumContactSize(specs.tech, layer)

        # use these default parameter values in the parameter definitions;
        # note that any out-of-range parameter values will be rejected.
        gridSize = specs.tech.getGridResolution()
        mySpecs('resistorType', resistorType,
              'Resistor type (poly, diff  or nwell)',
              ChoiceConstraint(['poly', 'diff', 'nwell']))
        mySpecs('width', width, 
              'resistor width',
              StepConstraint(gridSize, width, None, action=REJECT))
        mySpecs('length', length,
              'resistor length',
              StepConstraint(gridSize, length, None, action=REJECT))
        mySpecs('contactLength', contactLength,
              'contact length',
              StepConstraint(gridSize, contactLength, None, action=REJECT))

        # also define parameters to support rulesets and device contexts
        rulesetName = specs.tech.getActiveRuleset().name
        deviceContextName = specs.tech.getActiveDeviceContext().name
        mySpecs('ruleset', rulesetName)
        mySpecs('deviceContext', deviceContextName)

        mySpecs('silicided', False)

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)



    def setupParams(self, params):

        # Parameter renaming
        self.paramNamesReversed = reverseDict( self.paramNames)
        myParams = ParamArray()
        renameParams( params, myParams, self.paramNamesReversed)

        # save parameter values using class variables
        self.resistorType = myParams['resistorType']
        self.width = myParams['width']
        self.length = myParams['length']
        self.contactLength = myParams['contactLength']
        self.silicided = myParams['silicided']
        self.ruleset = myParams['ruleset']
        self.deviceContext = myParams['deviceContext']
    
        self.resistorLayer = self.getResistorLayer(self.resistorType)

        # use specified rule set and device context to determine minimum values
        with RulesetManager(self.tech, self.ruleset):
            with DeviceContextManager(self.tech, self.deviceContext):

                # readjust width and length parameter values, since the actual
                # minimum values may be different; use any device specific
                # minimum values which may be defined in the technology file.

                (minWidth, minLength) = self.getMinimumResistorSize(self.silicided, self.tech, self.resistorType)
                self.width = max(self.width, minWidth)
                self.length = max(self.length, minLength) 

                # readjust contact length, since minimum values may be different
                layer = self.getContactLayer(self.resistorType)
                (contactWidth, contactLength) = self.getMinimumContactSize(self.tech, layer)
                self.contactLength = max(self.contactLength, contactLength)

                # lookup portable layer names, and save layer values using class variables;
                # the metal layer will be used to add routing to this resistor unit
                self.polyLayer = Layer(*self.polyLayer)
                self.metalLayer = Layer(*self.metal1Layer)
                self.nimpLayer = Layer(*self.nimpLayer)
                self.pimpLayer = Layer(*self.pimpLayer)
                self.nwellLayer = Layer(*self.nwellLayer)
                self.diffLayer = Layer(*self.diffLayer)
                self.contactLayer = Layer(*self.contactLayer)
    
                # define layer which should be used for enclosure rectangles;
                # this is the Resist Protection Layer which is used to block 
                # silicide formation for poly and diffusion resistors.
                # (NOTE: RPO layer not currently used for nwell resistors)
                if (not self.silicided):
                    self.highResLayer = Layer(*self.rpoLayer)



    def genLayout(self):
        # use specified rule set and device context to construct resistor unit
        with RulesetManager(self.tech, self.ruleset):
            with DeviceContextManager(self.tech, self.deviceContext):
                self.construct()


    def construct(self):

        # construct the rectangle for the resistor body
        resistorBox = Box(0, 0, self.width, self.length)
        resistorRect = Rect(self.resistorLayer, resistorBox)

        # construct contacts for each end of the resistor body
        # Note that for nwell resistor, the implicit diffusion
        # layer is used to create the contact with metal layer.
        # If N-Well Resistor device context has been defined,
        # then use it when these contacts are constructed.
        # TODO: Try addLayers = Layer('nwell') construction.
        layer = self.getContactLayer(self.resistorType)
        if (self.resistorType == 'nwell' and
            deviceContextExists(self.tech, 'N-Well Resistor')):
            with DeviceContextManager(self.tech, 'N-Well Resistor'):
                self.sourceContact = Contact(layer, self.metalLayer, 'S')
                self.drainContact = Contact(layer, self.metalLayer, 'D')
        else:
            self.sourceContact = Contact(layer, self.metalLayer, 'S')
            self.drainContact = Contact(layer, self.metalLayer, 'D')

        # ensure width of each contact is same as width of the resistor body
        sourceBox = self.sourceContact.getRefBox()
        drainBox = self.drainContact.getRefBox()
        sourceBox.setRight(self.width)
        drainBox.setRight(self.width)

        # use user-supplied parameter to set the length of each contact
        sourceBox.setTop(self.contactLength)
        drainBox.setTop(self.contactLength)
        self.sourceContact.stretch(sourceBox)
        self.drainContact.stretch(drainBox)

        # place contacts at each end of the resistor body
        place(self.sourceContact, SOUTH, resistorRect, 0)
        place(self.drainContact, NORTH, resistorRect, 0)

        # If this is nwell resistor, add N plus diffusion around each contact;
        # note that this is done using specific design rule enclosure value.
        # Also create resistor rectangle on special nwell resistor layer.
        if self.resistorType == 'nwell':
            # create resistor rectangle on special 'nwr' NWell resistor layer
            if 'nwr' in self.tech.getSantanaLayerNames():
                nwrRect = Rect(Layer('nwr'), resistorBox)
            # extend the nwell resistor body to lie under each contact
            resistorBox.setTop(resistorBox.getTop() + self.sourceContact.getRefBox().getHeight())
            resistorBox.setBottom(resistorBox.getBottom() - self.drainContact.getRefBox().getHeight())
            resistorRect.setBBox(resistorBox)
            # add extra diffusion around contact required for NWell resistor 
            if deviceContextExists(self.tech, 'N-Well Resistor'):
                with DeviceContextManager(self.tech, 'N-Well Resistor'):
                    spacing = getMinExtensionRule(self.tech, self.nwellLayer, self.diffLayer, noRuleValue = 0)
            else:
                spacing = getMinExtensionRule(self.tech, self.nwellLayer, self.diffLayer, noRuleValue = 0)
            # extend diffusion on both sides and bottom
            sourceBox = self.sourceContact.getRefBox()
            sourceBox.setBottom(sourceBox.getBottom() - spacing)
            sourceBox.setRight(sourceBox.getRight() + spacing)
            sourceBox.setLeft(sourceBox.getLeft() - spacing)
            self.sourceContact.stretch(sourceBox)
            # extend diffusion on both sides and top
            drainBox = self.drainContact.getRefBox()
            drainBox.setTop(drainBox.getTop() + spacing)
            drainBox.setRight(drainBox.getRight() + spacing)
            drainBox.setLeft(drainBox.getLeft() - spacing)
            self.drainContact.stretch(drainBox)

            # also add implant around each contact
            if deviceContextExists(self.tech, 'N-Well Resistor'):
                with DeviceContextManager(self.tech, 'N-Well Resistor'):
                    fgAddEnclosingRects(self.sourceContact, [self.nimpLayer])
                    fgAddEnclosingRects(self.drainContact, [self.nimpLayer])
            else:
                fgAddEnclosingRects(self.sourceContact, [self.nimpLayer])
                fgAddEnclosingRects(self.drainContact, [self.nimpLayer])

        # add the terminals for this resistor unit
        self.addTerm('A', TermType.INPUT)           # input terminal
        self.addTerm('B', TermType.OUTPUT)          # output terminal

        self.setTermOrder(['A', 'B'])

        # also define the pins for this resistor unit
        self.addPin('A', 'A', self.sourceContact.getBBox(self.metalLayer), self.metalLayer)
        self.addPin('B', 'B', self.drainContact.getBBox(self.metalLayer), self.metalLayer)



    @classmethod
    def getMinimumResistorSize(cls, silicided, tech, resistorType):
        #
        # check to see if there are any device specific minimum sizes 
        # defined in technology file; if so, then use them, otherwise
        # use the default contact size for resistor layer. 
        #
        # silicided - Boolean flag to indicate use of silicide for resistor
        # tech - technology object for design rule lookup
        # resistorType - type of resistor ('poly', 'diff' or 'nwell')
        #
   
        layer = cls.getContactLayer(resistorType)

        # use minimum contact width as default value for resistor
        (contactWidth, contactLength) = cls.getMinimumContactSize(tech, layer)
        minWidth = contactWidth
        minLength =  contactWidth

        # check to see if there are any resistor specific values in technology file

        if resistorType in ['poly', 'diff']:
            if (not silicided):
                if tech.physicalRuleExists('minResistorWidth', layer): 
                    minWidth = max(minWidth, tech.getPhysicalRule('minResistorWidth', layer))
                if tech.physicalRuleExists('minResistorLength', layer):
                    minLength = max(minLength, tech.getPhysicalRule('minResistorLength', layer))
                # also account for spacing between resistor and each contact on RPO layer
                minLength += 2 * getMinClearanceRule(tech, Layer(*cls.rpoLayer), Layer(*cls.contactLayer), 0)

        if resistorType == 'nwell':
            nwellLayer = Layer(*cls.nwellLayer)
            # check for minimum value using special NWell resistor device context
            if deviceContextExists(tech, 'N-Well Resistor'):
                with DeviceContextManager(tech, 'N-Well Resistor'):
                    if tech.physicalRuleExists('minWidth', nwellLayer):
                        minWidth = max(minWidth, tech.getPhysicalRule('minWidth', nwellLayer))
            else:
                if tech.physicalRuleExists('minWidth', nwellLayer):
                    minWidth = max(minWidth, tech.getPhysicalRule('minWidth', nwellLayer))

        
        # round these computed values to the nearest grid point value
        grid = Grid(tech.getGridResolution(), snapType=SnapType.ROUND)
        minWidth = grid.snap(minWidth)
        minLength = grid.snap(minLength)

        return(minWidth, minLength)


    @classmethod
    def getMaximumResistorSize(cls, tech, resistorType):
        #
        # check to see if there are any device specific device maximum
        # sizes defined in technology file; if so, then use them.
        #
        # tech - technology object for design rule lookup
        # resistorType - type of resistor ('poly', 'diff' or 'nwell')
        #
   
        # check to see if there are any resistor specific values in technology file

        maxWidth = 0
        maxLength = 0

        if resistorType == 'nwell':
            nwellLayer = Layer(*cls.nwellLayer)
            # check for maximum value using special NWell resistor device context
            if deviceContextExists(tech, 'N-Well Resistor'):
                with DeviceContextManager(tech, 'N-Well Resistor'):
                    if tech.physicalRuleExists('maxWidth', nwellLayer):
                        maxWidth = tech.getPhysicalRule('maxWidth', nwellLayer)
                    if tech.physicalRuleExists('maxWidth', nwellLayer):
                        maxLength = tech.getPhysicalRule('maxLength', nwellLayer)
            else:
                if tech.physicalRuleExists('maxWidth', nwellLayer):
                    maxWidth = tech.getPhysicalRule('maxWidth', nwellLayer)
                if tech.physicalRuleExists('maxWidth', nwellLayer):
                    maxWidth = tech.getPhysicalRule('maxWidth', nwellLayer)

        # round these computed values to the nearest grid point value
        grid = Grid(tech.getGridResolution(), snapType=SnapType.ROUND)
        maxWidth = grid.snap(maxWidth)
        maxLength = grid.snap(maxLength)

        return(maxWidth, maxLength)



    @classmethod
    def getMinimumContactSize(cls, tech, layer):
        #
        # create default contact using design rules specified in technology file;
        # use this contact to determine default contact width and length values.
        #
        # tech - technology object for design rule lookup
        # layer - layer on which resistor is defined (poly or diffusion)
        #
   
        # first create default contact between resistor layer and metal layer
        contact = Contact(layer, Layer(*cls.metal1Layer))
        contactWidth = contact.getBBox().getWidth()
        contactHeight = contact.getBBox().getHeight()
        contact.destroy()

        return(contactWidth, contactHeight)


    @classmethod
    def getMetalContactSize(cls, tech, layer1, layer2):
        #
        # create default contact using design rules specified in technology file;
        # use this contact to determine default contact width and length values.
        #
        # tech - technology object for design rule lookup
        # layer1 - first metal layer on which contact is defined
        # layer2 - second metal layer on which contact is defined
        #
   
        # first create default contact between first and second metal layer
        contact = Contact(layer2, layer1)
        contactWidth = contact.getBBox().getWidth()
        contactHeight = contact.getBBox().getHeight()
        contact.destroy()

        return(contactWidth, contactHeight)


    @classmethod
    def  getResistorLayer(cls, resistorType):
        #
        # return layer which should be used to create resistor body
        #

        if resistorType == 'poly':
            return(Layer(*cls.polyLayer))
        elif resistorType == 'diff':
            return(Layer(*cls.diffLayer)) 
        elif resistorType == 'nwell':
            return(Layer(*cls.nwellLayer))



    @classmethod
    def  getContactLayer(cls, resistorType):
        #
        # return the layer which should be used to create contact
        # between the resistor layer and the metal routing layer.
        # Note that for nwell resistor, the implicit diffusion
        # layer is used to create the contact with metal layer.
        #

        if resistorType == 'poly':
            return(Layer(*cls.polyLayer))
        elif resistorType == 'diff':
            return(Layer(*cls.diffLayer))
        elif resistorType == 'nwell':
            return(Layer(*cls.diffLayer))


    @classmethod
    def  expandToGrid(cls, tech, rect):
    
        #
        # expand width of this rectangle, so that it lies on grid points
        #

        grid = Grid(tech.getGridResolution())
        box = rect.getBBox()
        expandBox = Box(box.lowerLeft().snapTowards(grid, WEST),
                        box.upperRight().snapTowards(grid, EAST))
        rect.setBBox(expandBox)
        return(rect)


