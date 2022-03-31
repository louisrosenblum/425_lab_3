########################################################################
# Copyright (c) 2001-2008 Ciranova, Inc. All Rights Reserved.          #
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
# pnp.py                                                               #
#                                                                      #
########################################################################

from __future__ import with_statement

from cni.dlo import *
from cni.geo import *
from cni.constants import *
from cni.integ.common import renameParams, reverseDict
import techUtils


class pnp(DloGen):

    # Portable layer names
    diffLayer =   ("DIFF",    "drawing")
    metal1Layer = ("M1",  "drawing")
    nimpLayer =   ("NIMP",    "drawing")
    pimpLayer =   ("PIMP",    "drawing")
    nwellLayer =  ("NWELL",   "drawing")

    paramNames = dict(
        we            = "we",
        he            = "he",
        fr            = "fr",
        rw            = "rw",
        deviceContext = "deviceContext",
        ruleset       = "ruleset",
    )

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # use variables to set default values for all parameters

        # Use minimum contact size to set minimum width and height for emitter

        (width, height) = cls.getMinimumContactSize(specs.tech, cls.diffLayer)

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # use these default parameter values in the parameter definitions;
        # note that any out-of-range parameter values will be rejected.
        gridSize = specs.tech.getGridResolution()
        mySpecs('we', cls.default.get('we', 2.0), 
                'emitter width',
                StepConstraint(gridSize, width, None, action=REJECT))
        mySpecs('he', cls.default.get('he', 2.0),
                'emitter height',
                StepConstraint(gridSize, height, None, action=REJECT))
        mySpecs('fr', cls.default.get('fr', 1), 
                'number of cells per row',
                RangeConstraint(1, None, REJECT))
        mySpecs('rw', cls.default.get('rw', 1), 
                'number of rows',
                RangeConstraint(1, None, REJECT))

        # also define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)



    def setupParams(self, params):

        # Parameter renaming
        self.paramNamesReversed = reverseDict( self.paramNames)
        myParams = ParamArray()
        renameParams( params, myParams, self.paramNamesReversed)

        # save parameter values using class variables
        self.width = myParams['we']
        self.height = myParams['he']
        self.fingers = myParams['fr']
        self.rows = myParams['rw']
        self.ruleset = myParams['ruleset']

        # lookup portable layer names
        self.diffLayer = Layer(*self.diffLayer)
        self.metalLayer = Layer(*self.metal1Layer)
        self.nimpLayer = Layer(*self.nimpLayer)
        self.pimpLayer = Layer(*self.pimpLayer)
        self.nwellLayer = Layer(*self.nwellLayer)
        self.emitterLayer = self.diffLayer

        self.deviceContext = self.tech.getActiveDeviceContext().name
        self.baseName = "PNP"
    
        # set up ruleset to be used during device construction
        rulesets = ['construction', 'default']
        if self.ruleset == 'recommended':
            rulesets.insert(0, 'recommended')
        self.ruleset = techUtils.orderedRuleset(self.tech, rulesets)

        # use specified rule set and device context to determine minimum values
        with RulesetManager(self.tech, self.ruleset):
            with DeviceContextManager(self.tech, self.deviceContext):

                # readjust width and height, since minimum values may be different
                (minWidth, minHeight) = self.getMinimumContactSize(self.tech, self.diffLayer)
                self.width = max(self.width, minWidth)
                self.height = max(self.height, minHeight) 

        # check to see if metal striping needs to be used to construct
        # the Emitter body; this will be required if the width of the
        # emitter is greater than the maximum metal width value.
        self.checkEmitterStriping()



    def genLayout(self):
        # use specified rule set and device context to construct PNP unit
        with RulesetManager(self.tech, self.ruleset):
            with DeviceContextManager(self.tech, self.deviceContext):
                self.construct()
                self.createPins()


    def construct(self):

        # First construct the emitter body, which consists of a diffusion
        # rectangle, along with a metal contact for this emitter body.
        # Also check to see if metal striping is required; if so, then
        # multiple emitter contacts will need to be constructed instead.
       
        emitterGroup = Grouping('Emitter_Group')

        if self.striping:
            prevContact = None
            for i in range(self.numStripes):
                emitterBox = Box(0, 0, self.stripeHeight, self.width)
                emitterRect = Rect(self.emitterLayer, emitterBox)
                emitterContact = Contact(self.emitterLayer, self.metalLayer, name='E' + str(i))
                # ensure size of contact is same as size of the emitter stripe
                emitterContact.stretch(emitterBox)
                if prevContact:
                    # use fgPlace() to place this emitter contact
                    fgPlace(emitterContact, Direction.EAST, prevContact)
                emitterGroup.add(emitterContact)
                prevContact = emitterContact
            # also generate diffusion rectangle for all emitter stripes
            emitterBox = Box(0, 0, self.height, self.width)
            emitterRect = Rect(self.emitterLayer, emitterBox)
            emitterGroup.add(emitterRect)
        else:
            emitterBox = Box(0, 0, self.height, self.width)
            emitterRect = Rect(self.emitterLayer, emitterBox)
            emitterContact = Contact(self.emitterLayer, self.metalLayer, name='E')
            # ensure size of contact is same as size of the emitter body
            emitterContact.stretch(emitterBox)
            emitterGroup.add(emitterContact)

        # save all emitter contacs to create compound component
        self.emitterContacts = []
        for emitter in emitterGroup:
            self.emitterContacts.append(emitter)


        # Now construct the P+ region for the emitter. Note that it is necessary
        # to use a temporary NWell rectangle, since the emitter will be contained
        # within an NWell, and P+ enclosure rules are larger when NWell is used.
        PPlusRect = fgAddEnclosingRects(emitterGroup, [self.pimpLayer, self.nwellLayer])
        for comp in PPlusRect.getComps():
            if comp.getLayer() == self.nwellLayer:
                PPlusRect.remove(comp)
                comp.destroy()

        # construct the base, using a contact ring
        self.baseContactRing = ContactRing(self.emitterLayer, self.metalLayer, 
                                           addLayers=[self.nimpLayer], 
                                           fillLayers=[self.nwellLayer],
                                           name='B')

        # construct the enclosing NWell rectangle for the emitter and base
        EBWell = self.makeGrouping()
        NWellRect = fgAddEnclosingRects(EBWell, [self.nwellLayer])


        # Now construct the collector, using another contact ring.
        # Since collectors will be shared, measure required spacing between
        # the emitter/base units, which will be used for collector sharing.
        spacing = fgMinSpacing(EBWell, NORTH, EBWell)

        encloseBox = EBWell.getBBox()
        EBWell.ungroup()
        tempContactRing = ContactRing(self.emitterLayer, self.metalLayer, overlapContact=True, addLayers=[self.pimpLayer])
        length = tempContactRing.getContact(SOUTH).getRefBox().getHeight()
        # calculate space needed for contact ring, including the implant layer overlap
        spacing1 = tempContactRing.getBBox().getWidth()
        spacing2 = tempContactRing.getBBox(ShapeFilter().exclude(self.pimpLayer)).getWidth()
        length = length + (spacing1 - spacing2)
        tempContactRing.destroy()
        encloseBox.expand((spacing - length) / 2.0)
        self.collectorContactRing = ContactRing(self.emitterLayer, self.metalLayer,
                                                addLayers=[self.pimpLayer], 
                                                encloseBox=encloseBox, 
                                                overlapContact=True,
                                                name='C')

        # create compound component for this PNP cell
        emitterGroup.ungroup()
        pnpCell = CompoundComponent('PNP')
        pnpCell.add(self.emitterContacts)
        pnpCell.add(self.baseContactRing)
        pnpCell.add(NWellRect)
        pnpCell.add(PPlusRect)
        pnpCell.add(self.collectorContactRing)
        pnpCell.lock()
        

        # Place PNP cells into an array, each one next to the previous one;
        # want to share collectors, by overlapping collector contact rings.
        collectorWidth = length
        xOffset = pnpCell.getBBox().getWidth() - collectorWidth 
        yOffset = pnpCell.getBBox().getHeight() - collectorWidth
        tmpGroup = pnpCell.makeArray(xOffset, yOffset, self.rows, self.fingers, self.baseName)
        tmpGroup.ungroup()


    def createPins(self):
        # assign all emitter pins to pin "E"
        emitterPin = Pin('E', 'E')
        basePin = Pin('B', 'B')
        collectorPin = Pin('C', 'C')
        for i in range(self.rows):
            for j in range(self.fingers):
                pnpComp = self.findComponent(i,j)
                for comp in pnpComp.getComps():
                    # check to see if this is an emitter contact;
                    # if so, then assign this shape to pin "E".
                    if isinstance(comp, Contact):
                        emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
                    elif isinstance(comp, ContactRing):
                        # check for either base or collector contact ring
                        if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))


    def findComponent(self, i, j):
        # create component name from base name
        name = self.baseName + '_' + str(i) + '_' + str(j)
        # find this component in the array of PNP cells
        return(CompoundComponent.find(name))




    def getMinimumContactSize(self, tech, layer):
        #
        # create default contact using design rules specified in technology file;
        # use this contact to determine default contact width and length values.
        #
        # tech - technology object for design rule lookup
        # layer - layer on which BJT emitter is defined (diffusion)
        #
   
        # first create default contact between diffusion layer and metal layer
        contact = Contact(layer, self.metalLayer)
        contactWidth = contact.getBBox().getWidth()
        contactHeight = contact.getBBox().getHeight()
        contact.destroy()
    
        return(contactWidth, contactHeight)


    def checkEmitterStriping(self):
        #
        # In the case that the size of the emitter contact is greater than 
        # the maximum metal1 width for the technology, then metal striping
        # is required. In this case, multiple emitter contacts are created.
        # All emitter contacts will be the same size, allowing for design
        # rule correct spacing between these multiple emitter contacts.
        #

        # set default values for emitter striping
        self.striping = False
        self.numStripes = 0
        self.stripeHeight = 0

        # first check to see if the design rule for maximum metal1 width
        # has been defined in the technology file which is being used.
        if self.tech.physicalRuleExists('maxWidth', self.metalLayer):
            maxWidth = self.tech.getPhysicalRule('maxWidth', self.metalLayer)
            # check to see if metal striping will be required
            if maxWidth < self.width:
                # Striping will be required for Emitter body construction;
                # calculate the number of stripes which will be required.
                # Note that all emitter stripes should be the same size.
                numStripes = int(self.width/maxWidth + 1)
                # Calculate the length of each emitter stripe;
                # this depends upon the size of each stripe,
                # as well as the spacing between the stripes.
                tempContact = Contact(self.emitterLayer, self.metalLayer)
                tempContact.stretch(Box(0, 0, self.height, self.width/numStripes))
                stripeSpacing = fgMinSpacing(tempContact, Direction.EAST, tempContact)
                tempContact.destroy()
                stripeHeight = (self.height - (numStripes-1) * stripeSpacing)/numStripes

                # set values for emitter striping
                self.striping = True
                self.numStripes = numStripes
                self.stripeHeight = stripeHeight




#
# Define derived classes for various sizes of PNP cells
#
# These PNP cells include the following:
#
#  pnp2 - same as "pnp", but with emitter width and length 2um
#  pnp5 - same as "pnp", but with emitter width and length 5um
#  pnp10 - same as "pnp", but with emitter width and length 10um
#  bandgap3x3pnp10 - fixed 3x3 bandgap array of pnp cells
#  bandgap4x3pnp10 - fixed 4x3 bandgap array of pnp cells
#  bandgap5x5pnp5 - fixed 5x5 bandgap array of pnp cells
#  bandgap3x3 - 3x3 bandgap array of pnp cells, user-specified emitter size
#  bandgap4x3 - 4x3 bandgap array of pnp cells, user-specified emitter size
#  bandgap5x5 - 5x5 bandgap array of pnp cells, user-specified emitter size
#
#
# Note that all of these different types of PNP cells and bandgap cells are
# generated by setting the appropriate parameter values for the base pnp class.
# The bandgap cells also have to define the different pin assignments for the
# different emitters; these pin assignments are all fixed for the PNP cells.
#

class pnp2(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameters to support rows and columns
        mySpecs('rw', cls.default.get('rw', 1), 
                'number of rows', 
                RangeConstraint(1, None, REJECT))
        mySpecs('fr', cls.default.get('fr', 1), 
                'number of cells per row', 
                RangeConstraint(1, None, REJECT))

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['we'] = 2.0
        params['he'] = 2.0
        # call method on base pnp class
        pnp.setupParams(self, params)


class pnp5(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameters to support rows and columns
        mySpecs('rw', cls.default.get('rw', 1), 
                'number of rows', 
                RangeConstraint(1, None, REJECT))
        mySpecs('fr', cls.default.get('fr', 1), 
                'number of cells per row', 
                RangeConstraint(1, None, REJECT))

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['we'] = 5.0
        params['he'] = 5.0
        # call method on base pnp class
        pnp.setupParams(self, params)


class pnp10(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameters to support rows and columns
        mySpecs('rw', cls.default.get('rw', 1), 
                'number of rows', 
                RangeConstraint(1, None, REJECT))
        mySpecs('fr', cls.default.get('fr', 1), 
                'number of cells per row', 
                RangeConstraint(1, None, REJECT))

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['we'] = 10.0
        params['he'] = 10.0
        # call method on base pnp class
        pnp.setupParams(self, params)



class bandgap3x3pnp10(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['we'] = 10.0
        params['he'] = 10.0
        params['fr'] = 3
        params['rw'] = 3
        # call method on base pnp class
        pnp.setupParams(self, params)

    def createPins(self):
        # assign emitter pins
        emitterPin = Pin('E', 'E')
        emitterPin1 = Pin('E1', 'E1')
        basePin = Pin('B', 'B')
        collectorPin = Pin('C', 'C')
        for i in range(self.rows):
            for j in range(self.fingers):
                pnpComp = self.findComponent(i,j)
                for comp in pnpComp.getComps():
                    # check to see if this is the emitter contact;
                    # if so, then assign this shape to proper pin.
                    if isinstance(comp, Contact):
                        if ((i == 1) and (j == 1)):
                            emitterPin1.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        else:
                            emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
                    elif isinstance(comp, ContactRing):
                        # check for either base or collector contact ring
                        if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        



class bandgap4x3pnp10(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['we'] = 10.0
        params['he'] = 10.0
        params['fr'] = 4
        params['rw'] = 3
        # call method on base pnp class
        pnp.setupParams(self, params)

    def createPins(self):
        # assign emitter pins
        emitterPin = Pin('E', 'E')
        emitterPin1 = Pin('E1', 'E1')
        emitterPin2 = Pin('E2', 'E2')
        basePin = Pin('B', 'B')
        collectorPin = Pin('C', 'C')
        for i in range(self.rows):
            for j in range(self.fingers):
                pnpComp = self.findComponent(i,j)
                # Dummy devices located on ends of row 1 have no pins
                if ((i == 1) and (j == 0)):
                    continue
                if ((i == 1) and (j == 3)):
                    continue
                for comp in pnpComp.getComps():
                    # check to see if this is the emitter contact;
                    # if so, then assign this shape to proper pin.
                    if isinstance(comp, Contact):
                        if ((i == 1) and (j == 1)):
                            emitterPin1.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        elif ((i == 1) and (j == 2)):
                            emitterPin2.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        else:
                            emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
                    elif isinstance(comp, ContactRing):
                        # check for either base or collector contact ring
                        if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        


class bandgap5x5pnp5(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['we'] = 5.0
        params['he'] = 5.0
        params['fr'] = 5
        params['rw'] = 5
        # call method on base pnp class
        pnp.setupParams(self, params)

    def createPins(self):
        # assign emitter pins
        emitterPin = Pin('E', 'E')
        emitterPin1 = Pin('E1', 'E1')
        basePin = Pin('B', 'B')
        collectorPin = Pin('C', 'C')
        for i in range(self.rows):
            for j in range(self.fingers):
                pnpComp = self.findComponent(i,j)
                # Dummy devices completely surround inner 3x3 bandgap cell;
                # these dummies occupy the bottom and top rows and columns.
                if ((i == 0) or (i == 4)):
                    continue
                if ((j == 0) or (j == 4)):
                    continue
                for comp in pnpComp.getComps():
                    # check to see if this is the emitter contact;
                    # if so, then assign this shape to proper pin.
                    if isinstance(comp, Contact):
                        if ((i == 2) and (j == 2)):
                            emitterPin1.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        else:
                            emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
                    elif isinstance(comp, ContactRing):
                        # check for either base or collector contact ring
                        if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        

class bandgap3x3(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # Define parameters for emitter dimensions; note that these width and
        # height parameter values get passed directly to the base PNP class.
        gridSize = specs.tech.getGridResolution()
        mySpecs('we', cls.default.get('we', 2.0), 
                'emitter width',
                StepConstraint(gridSize, 2.0, None, action=REJECT))
        mySpecs('he', cls.default.get('he', 2.0),
                'emitter height',
                StepConstraint(gridSize, 2.0, None, action=REJECT))

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['fr'] = 3
        params['rw'] = 3
        # call method on base pnp class
        pnp.setupParams(self, params)

    def createPins(self):
        # assign emitter pins
        emitterPin = Pin('E', 'E')
        emitterPin1 = Pin('E1', 'E1')
        basePin = Pin('B', 'B')
        collectorPin = Pin('C', 'C')
        for i in range(self.rows):
            for j in range(self.fingers):
                pnpComp = self.findComponent(i,j)
                for comp in pnpComp.getComps():
                    # check to see if this is the emitter contact;
                    # if so, then assign this shape to proper pin.
                    if isinstance(comp, Contact):
                        if ((i == 1) and (j == 1)):
                            emitterPin1.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        else:
                            emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
                    elif isinstance(comp, ContactRing):
                        # check for either base or collector contact ring
                        if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        


class bandgap4x3(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # Define parameters for emitter dimensions; note that these width and
        # height parameter values get passed directly to the base PNP class.
        gridSize = specs.tech.getGridResolution()
        mySpecs('we', cls.default.get('we', 2.0), 
                'emitter width',
                StepConstraint(gridSize, 2.0, None, action=REJECT))
        mySpecs('he', cls.default.get('he', 2.0),
                'emitter height',
                StepConstraint(gridSize, 2.0, None, action=REJECT))

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['fr'] = 4
        params['rw'] = 3
        # call method on base pnp class
        pnp.setupParams(self, params)

    def createPins(self):
        # assign emitter pins
        emitterPin = Pin('E', 'E')
        emitterPin1 = Pin('E1', 'E1')
        emitterPin2 = Pin('E2', 'E2')
        basePin = Pin('B', 'B')
        collectorPin = Pin('C', 'C')
        for i in range(self.rows):
            for j in range(self.fingers):
                pnpComp = self.findComponent(i,j)
                # Dummy devices located on ends of row 1 have no pins
                if ((i == 1) and (j == 0)):
                    continue
                if ((i == 1) and (j == 3)):
                    continue
                for comp in pnpComp.getComps():
                    # check to see if this is the emitter contact;
                    # if so, then assign this shape to proper pin.
                    if isinstance(comp, Contact):
                        if ((i == 1) and (j == 1)):
                            emitterPin1.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        elif ((i == 1) and (j == 2)):
                            emitterPin2.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        else:
                            emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
                    elif isinstance(comp, ContactRing):
                        # check for either base or collector contact ring
                        if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        


class bandgap5x5(pnp):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # Define parameters for emitter dimensions; note that these width and
        # height parameter values get passed directly to the base PNP class.
        gridSize = specs.tech.getGridResolution()
        mySpecs('we', cls.default.get('we', 2.0), 
                'emitter width',
                StepConstraint(gridSize, 2.0, None, action=REJECT))
        mySpecs('he', cls.default.get('he', 2.0),
                'emitter height',
                StepConstraint(gridSize, 2.0, None, action=REJECT))

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
        params['fr'] = 5
        params['rw'] = 5
        # call method on base pnp class
        pnp.setupParams(self, params)

    def createPins(self):
        # assign emitter pins
        emitterPin = Pin('E', 'E')
        emitterPin1 = Pin('E1', 'E1')
        basePin = Pin('B', 'B')
        collectorPin = Pin('C', 'C')
        for i in range(self.rows):
            for j in range(self.fingers):
                pnpComp = self.findComponent(i,j)
                # Dummy devices completely surround inner 3x3 bandgap cell;
                # these dummies occupy the bottom and top rows and columns.
                if ((i == 0) or (i == 4)):
                    continue
                if ((j == 0) or (j == 4)):
                    continue
                for comp in pnpComp.getComps():
                    # check to see if this is the emitter contact;
                    # if so, then assign this shape to proper pin.
                    if isinstance(comp, Contact):
                        if ((i == 2) and (j == 2)):
                            emitterPin1.addShape(Rect(self.metalLayer, comp.getRefBox()))
                        else:
                            emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
                    elif isinstance(comp, ContactRing):
                        # check for either base or collector contact ring
                        if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
                        elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
                            for dir in [NORTH, SOUTH, EAST, WEST]:
                                collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))

