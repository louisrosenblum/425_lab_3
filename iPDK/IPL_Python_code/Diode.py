#******************************************************************************************
#******************************************************************************************
#**********                       SAED_PDK90 1P9M                         *****************
#******************************************************************************************
#******************************************************************************************

########################################################################
#                                                                      #
# diode.py                                                             #
#                                                                      #
########################################################################

from __future__ import with_statement

from cni.dlo import *
from cni.geo import *
from cni.constants import *
from cni.integ.common import renameParams, reverseDict
from MosUtils import LayerDict
import techUtils

# Base class for Ndiode, Pdiode, NdiodeH, PdiodeH and NWdiode 
class diode(DloGen):

    innerPinName = "MINUS"
    outerPinName = "PLUS"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        nplus        = ( "NIMP",    "drawing"),
        pplus        = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        nwell        = ( "NWELL",   "drawing"),
	diod         = ( "DIOD",    "drawing"),
        pwell        = None,
        od2          = None,
        innerWell    = None,
    )

    innerLayer  = "nplus"
    outerLayer  = "pplus"
    well        = "pwell"
    diod        = "diod"

    paramNames = dict(
        width         = "w",
        height        = "l",
        deviceContext = "deviceContext",
        ruleset       = "ruleset",
    )

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # use variables to set default values for all parameters

        # Use minimum contact size to set minimum width and height for diode

        layer = LayerDict( specs.tech, cls.layerMapping)
        (width, height) = cls.getMinimumContactSize(specs.tech, layer)

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # use these default parameter values in the parameter definitions;
        # note that any out-of-range parameter values will be rejected.
        gridSize = specs.tech.getGridResolution()
        #mySpecs('width', cls.default.get('width', 10.0), 
        #        'diode width',
        #        StepConstraint(gridSize, width, None, action=REJECT))
	
	mySpecs('width', cls.default.get('width', 2.0), 
                'diode width')
	
        #mySpecs('height', cls.default.get('height', 10.0),
        #        'diode height',
        #        StepConstraint(gridSize, height, None, action=REJECT))
	
	mySpecs('height', cls.default.get('height', 2.0),
                'diode height')

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
        self.width = myParams['width']
        self.height = myParams['height']
        self.ruleset = myParams['ruleset']

        # Convert to process layer names
        self.layer      = LayerDict( self.tech, self.layerMapping)
        self.innerLayer  = self.layer[ self.innerLayer]
        self.outerLayer  = self.layer[ self.outerLayer]
        self.well        = self.layer[ self.well]
	self.diod        = self.layer[ self.diod]
	self.Name	 = "Diode"
        self.deviceContext = self.tech.getActiveDeviceContext().name
    
        # set up ruleset to be used during device construction
        rulesets = ['construction', 'default']
        if self.ruleset == 'recommended':
            rulesets.insert(0, 'recommended')
        self.ruleset = techUtils.orderedRuleset(self.tech, rulesets)

        # use specified rule set and device context to determine minimum values
        with RulesetManager(self.tech, self.ruleset):
            with DeviceContextManager(self.tech, self.deviceContext):

                # readjust width and height, since minimum values may be different
                (minWidth, minHeight) = self.getMinimumContactSize(self.tech, self.layer)
                if self.width < 6e-5:
			self.width = self.width*1e6
			self.width = max(self.width, minWidth)
                if self.height < 6e-5:
			self.height = self.height*1e6
			self.height = max(self.height, minHeight) 

        # check to see if metal striping needs to be used to construct
        # the Diode diffusion body; this will be required if the width
        # of the diode body is greater than the maximum metal width value.
        self.checkMetalStriping()


    def genLayout(self):
        # use specified rule set and device context to construct Diode unit
        with RulesetManager(self.tech, self.ruleset):
            with DeviceContextManager(self.tech, self.deviceContext):
                self.construct()
                self.createPins()


    def construct(self):

        # Construct inner terminal:
        # 1. Create inner diffusion with specified width and hight params.
        # 2. Combine it with same-sized difussion-metal1 contact
        layer = LayerDict( self.tech, self.layerMapping)
       
        diodeGroup = Grouping('Diode_Group')
    
        if self.striping:
            prevContact = None
            for i in range(self.numStripes):
                innerBox = Box(0, 0, self.stripeHeight, self.width)
                innerRect = Rect(self.layer.diffusion, innerBox)
                self.innerContact = Contact(self.layer.diffusion, self.layer.metal1, name=self.innerPinName + str(i))
                # ensure size of contact is same as size of the diode stripe
                self.innerContact.stretch(innerBox)
                if prevContact:
                    # use pre-calculated stripe spacing to place this diode contact
                    place(self.innerContact, Direction.EAST, prevContact, self.stripeSpacing)
                diodeGroup.add(self.innerContact)
                prevContact = self.innerContact
            # also generate diffusion rectangle for all emitter stripes
            innerBox = Box(0, 0, self.height, self.width)
            innerRect = Rect(self.layer.diffusion, innerBox)
            diodeGroup.add(innerRect)
        else:
            innerBox = Box(0, 0, self.width, self.height)
            innerRect = Rect(self.layer.diffusion, innerBox)
            self.innerContact = Contact(self.layer.diffusion, self.layer.metal1, name=self.innerPinName)

            # Ensure size of contact is same as size of the diode body
            self.innerContact.stretch(innerBox)
            diodeGroup.add(self.innerContact)

        # save all inner contacs to create compound component
        self.innerContacts = []
        for c in diodeGroup:
            self.innerContacts.append(c)

        # Now construct the active region for diode inner terminal. Note that it is necessary
        # to use a temporary well rectangle, since the inner terminal will be contained
        # within an well, and active (P+ and N+) enclosure rules are larger when well is used.
        innerList = [self.innerLayer]
        if self.well:
            innerList.append(self.well)
        if self.layer.innerWell:
            innerList.append(self.layer.innerWell)

        innerRect = fgAddEnclosingRects(diodeGroup, innerList)
        for comp in innerRect.getComps():
            if comp.getLayer() == self.well:
                innerRect.remove(comp)
                comp.destroy()

        # Construct the outer terminal, using a contact ring
        fillList = [self.diod]
        if self.well:
            fillList.append(self.well)
        if self.layer.od2:
            fillList.append(self.layer.od2)
        self.outerContactRing = ContactRing(self.layer.diffusion, self.layer.metal1,
                                            addLayers=[self.outerLayer],
                                            fillLayers=fillList,
                                            name=self.outerPinName)
        
        # Surround everything with well and thick oxide
        # Thick oxide must not be smaller than contact ring (transistor matching requirement)
        bbox = self.outerContactRing.getBBox(ShapeFilter(self.layer.metal1))
        wellGroup = self.makeGrouping()
        outerList = []
        if self.well:
            outerList.append(self.well)
            outerRect = fgAddEnclosingRects(wellGroup, outerList)

            # If PdiodeH we will make od2 rect as large as well rect to avoid drc errors
            for comp in outerRect.getComps():
                if comp.getLayer() == self.well:
                    bbox = comp.getBBox()

        # Extend thick oxide and well to the bbox of Contact Ring
        if self.layer.od2:
            # for NdiodeH create second od2 rect to avoid enclosure rule errors for diff and od2
            ruleExists = self.tech.physicalRuleExists('minExtension', self.layer.od2, self.layer.diffusion)
            #if (not self.well) and ruleExists:
            if ruleExists:
                oxideGroup = self.makeGrouping()
                oxideRects = fgAddEnclosingRects(oxideGroup, [self.layer.od2])
                for comp in oxideRects.getComps():
                    bbox.merge(comp.getBBox())
                    oxideRects.remove(comp)
                    comp.destroy()
            oxideRect = Rect(self.layer.od2, bbox)
            
        # Extend contact ring's well rect to the size of surrounding well rect and remove it
        if self.well:
            for comp in self.outerContactRing.getLeafComps():
                if isinstance(comp, Rect):
                    if comp.getLayer() == self.well:
                        comp.setBBox(bbox)
            for comp in outerRect.getComps():
                if comp.getLayer() == self.well:
                    outerRect.remove(comp)
                    comp.destroy()

        # Create compound component for this Diode cell
        wellGroup.ungroup()
        diodeGroup.ungroup()
        diodeCell = CompoundComponent('Diode')
        diodeCell.add(self.innerContacts)
        diodeCell.add(self.outerContactRing)
        diodeCell.add(innerRect)
        if self.well and outerRect.getComps():
            diodeCell.add(outerRect)
        if self.layer.od2:
            diodeCell.add(oxideRect)
        diodeCell.lock()
        
    def createPins(self):
        innerPin = Pin(self.innerPinName, self.innerPinName)
        outerPin = Pin(self.outerPinName, self.outerPinName)
	diodeComp = self.findComponent()
	for comp in diodeComp.getComps():
            # check to see if this is a contact;
            # if so, then assign this shape to innerPin
            if isinstance(comp, Contact):
                innerPin.addShape(Rect(self.layer.metal1, comp.getRefBox()))
            # check to see if this is a ContactRing;
            # if so, then assign this shape to pin outerPin
            elif isinstance(comp, ContactRing):
                for dir in [NORTH, SOUTH, EAST, WEST]:
                    outerPin.addShape(Rect(self.layer.metal1, comp.getContact(dir).getRefBox()))
    
    def findComponent(self):
        # create component name from base name
        name = self.Name
        # find this component in the array of PNP cells
        return(CompoundComponent.find(name))
    
    
    @classmethod
    def getMinimumContactSize(cls, tech, layer):
        #
        # create default contact using design rules specified in technology file;
        # use this contact to determine default contact width and length values.
        #
        # tech - technology object for design rule lookup
        # layer - layer on which diode is defined (diffusion)
        #
   
        # first create default contact between diffusion layer and metal layer;
        # note that route directions are specified to avoid mimimum area rules.  
        contact = Contact(layer.diffusion, layer.metal1, routeDir1=NORTH_SOUTH, routeDir2=EAST_WEST)
        contactWidth = contact.getBBox().getWidth()
        contactHeight = contact.getBBox().getHeight()
        contact.destroy()
    
        return(contactWidth, contactHeight)

    def checkMetalStriping(self):
        #
        # In the case that the size of the diode contact is greater than
        # the maximum metal1 width for the technology, then metal striping
        # is required. In this case, multiple diode contacts are created.
        # All diode contacts will be the same size, allowing for design
        # rule correct spacing between these multiple diode contacts.
        #

        # set default values for diode striping
        self.striping = False
        self.numStripes = 0
        self.stripeHeight = 0

        # first check to see if the design rule for maximum metal1 width
        # has been defined in the technology file which is being used.
        if self.tech.physicalRuleExists('maxWidth', self.layer.metal1):
            maxWidth = self.tech.getPhysicalRule('maxWidth', self.layer.metal1)
            # check to see if metal striping will be required
            if maxWidth < self.width:
                # Striping will be required for Diode body construction;
                # calculate the number of stripes which will be required.
                # Note that all diode stripes should be the same size.
                numStripes = int(self.width/maxWidth + 1)
                # Calculate the length of each diode stripe;
                # this depends upon the size of each stripe,
                # as well as the spacing between the stripes.
                tempContact = Contact(self.layer.diffusion, self.layer.metal1)
                tempContact.stretch(Box(0, 0, self.height, self.width/numStripes))
                stripeSpacing = fgMinSpacing(tempContact, Direction.EAST, tempContact)
                tempContact.destroy()
                stripeHeight = min(maxWidth, (self.height - (numStripes-1) * stripeSpacing)/numStripes)
                stripeSpacing = (self.height - (numStripes * stripeHeight))/(numStripes-1)

                # set values for diode striping
                self.striping = True
                self.numStripes = numStripes
                self.stripeHeight = stripeHeight
                self.stripeSpacing = stripeSpacing

class nd(diode):

    innerPinName = "MINUS"
    outerPinName = "PLUS"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        nplus        = ( "NIMP",    "drawing"),
        pplus        = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        nwell        = ( "NWELL",   "drawing"),
	diod         = ( "DIOD",    "drawing"),
        pwell        = None,
        od2          = None,
        innerWell    = None,
    )

    innerLayer  = "nplus"
    outerLayer  = "pplus"
    well        = "pwell"
    diod        = "diod"

class pd(diode):

    innerPinName = "PLUS"
    outerPinName = "MINUS"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        nplus        = ( "NIMP",    "drawing"),
        pplus        = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        nwell        = ( "NWELL",   "drawing"),
	diod         = ( "DIOD",    "drawing"),
        pwell        = None,
        od2          = None,
        innerWell    = None,
    )

    innerLayer  = "pplus"
    outerLayer  = "nplus"
    well        = "nwell"
    diod        = "diod"
