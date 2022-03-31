#******************************************************************************************
#******************************************************************************************
#**********                       SAED_PDK90 1P9M                         *****************
#******************************************************************************************
#******************************************************************************************

###########################################################################################
#                                                                                         #
# NPN.py                                                                                  #
#                                                                                         #
###########################################################################################

from __future__ import with_statement

from cni.dlo import *
from cni.geo import *
from cni.constants import *
from cni.integ.common import renameParams, reverseDict
import techUtils

#######################################################################
#                                                                     # 
# Class of SAED_PDK_90nm NPN                                          #
#                                                                     #
#######################################################################

class npn(DloGen):

    diffLayer =   ("DIFF",    "drawing")
    metal1Layer = ("M1",  "drawing")
    nimpLayer =   ("NIMP",    "drawing")
    pimpLayer =   ("PIMP",    "drawing")
    nwellLayer =  ("NWELL",   "drawing")
    dmyLayer =    ("BJTMY",  "drawing")

    paramNames = dict(
        we            = "we",
        he            = "he",
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
        #mySpecs('we', cls.default.get('we', 2.0), 
        #        'emitter width',
        #        StepConstraint(gridSize, width, None, action=REJECT))
	
	mySpecs('we', cls.default.get('we', 2.0), 
                'emitter width')
	
        #mySpecs('he', cls.default.get('he', 2.0),
        #        'emitter height',
        #        StepConstraint(gridSize, height, None, action=REJECT))
	
	mySpecs('he', cls.default.get('he', 2.0),
                'emitter height')
        
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
        self.ruleset = myParams['ruleset']

        # lookup portable layer names
        self.diffLayer = Layer(*self.diffLayer)
        self.metalLayer = Layer(*self.metal1Layer)
        self.nimpLayer = Layer(*self.nimpLayer)
        self.pimpLayer = Layer(*self.pimpLayer)
        self.nwellLayer = Layer(*self.nwellLayer)
	self.emitterLayer = self.diffLayer
        self.dmyLayer = Layer(*self.dmyLayer)
	
        self.deviceContext = self.tech.getActiveDeviceContext().name
        self.baseName = "NPN"
    
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
                if self.width < 3e-4:
			self.width = self.width*1e6
			self.width = max(self.width, minWidth)
                
		if self.height < 3e-4:
			self.height = self.height*1e6
			self.height = max(self.height, minHeight) 

        # check to see if metal striping needs to be used to construct
        # the Emitter body; this will be required if the width of the
        # emitter is greater than the maximum metal width value.
        self.checkEmitterStriping()



    def genLayout(self):
        # use specified rule set and device context to construct NPN unit
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
        PPlusRect = fgAddEnclosingRects(emitterGroup, [self.nimpLayer]) 
        
        # construct the base, using a contact ring
        self.baseContactRing = ContactRing(self.emitterLayer, self.metalLayer, 
                                           addLayers=[self.pimpLayer], 
                                           fillLayers=[self.dmyLayer],
                                           name='B')

        # construct the enclosing NWell rectangle for the emitter and base
        EBWell = self.makeGrouping()
	       
        # Now construct the collector, using another contact ring.
        # Since collectors will be shared, measure required spacing between
        # the emitter/base units, which will be used for collector sharing.
        #spacing = fgMinSpacing(EBWell, NORTH, EBWell)
	spacing = 1.2
	
        encloseBox = EBWell.getBBox()
        EBWell.ungroup()
        tempContactRing = ContactRing(self.emitterLayer, self.metalLayer, overlapContact=True, addLayers=[self.nwellLayer, self.nimpLayer])
        length = tempContactRing.getContact(SOUTH).getRefBox().getHeight()
	# calculate space needed for contact ring, including the implant layer overlap
        spacing1 = tempContactRing.getBBox().getWidth()
        spacing2 = tempContactRing.getBBox(ShapeFilter().exclude(self.nwellLayer)).getWidth()
        length = length + (spacing1 - spacing2)
        tempContactRing.destroy()
	encloseBox.expand((spacing - length) / 2.0) 
        self.collectorContactRing = ContactRing(self.emitterLayer, self.metalLayer,  
                                                addLayers=[self.nwellLayer, self.nimpLayer],
						fillLayers=[], 
                                                encloseBox=encloseBox, 
                                                overlapContact=True, 
                                                name='C')

        # create compound component for this NPN cell
        emitterGroup.ungroup()
        npnCell = CompoundComponent('NPN')
        npnCell.add(self.emitterContacts)
        npnCell.add(self.baseContactRing)
        npnCell.add(PPlusRect)
        npnCell.add(self.collectorContactRing)
        npnCell.lock()
        

        # Place NPN cells into an array, each one next to the previous one;
        # want to share collectors, by overlapping collector contact rings.
        #collectorWidth = length
        #xOffset = npnCell.getBBox().getWidth() - 0.65 
        #yOffset = npnCell.getBBox().getHeight() - 0.65
        #tmpGroup = npnCell.makeArray(xOffset, yOffset, self.rows, self.fingers, self.baseName)
        #tmpGroup.ungroup()


        ####def createPins(self):
   	####    # assign all emitter pins to pin "E"
  	####    emitterPin = Pin('E', 'E')
   	####    basePin = Pin('B', 'B')
   	####    collectorPin = Pin('C', 'C')
   	####    for i in range(self.rows):
   	####        for j in range(self.fingers):
   	#### 	   npnComp = self.findComponent(i,j)
   	#### 	   for comp in npnComp.getComps():
   	#### 	       # check to see if this is an emitter contact;
   	#### 	       # if so, then assign this shape to pin "E".
   	#### 	       if isinstance(comp, Contact):
   	#### 		   emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
   	#### 	       elif isinstance(comp, ContactRing):
   	#### 		   # check for either base or collector contact ring
   	#### 		   if comp.getName() == 'B' + '_' + str(i) + '_' + str(j):
   	#### 		       for dir in [NORTH, SOUTH, EAST, WEST]:
   	#### 			   basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
   	#### 		   elif comp.getName() == 'C' + '_' + str(i) + '_' + str(j):
   	#### 		       for dir in [NORTH, SOUTH, EAST, WEST]:
   	#### 			   collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))

    def createPins(self):
    	# assign all emitter pins to pin "E"
    	emitterPin = Pin('E', 'E')
    	basePin = Pin('B', 'B')
    	collectorPin = Pin('C', 'C')
    	npnComp = self.findComponent()
    	for comp in npnComp.getComps():
    	       # check to see if this is an emitter contact;
    	       # if so, then assign this shape to pin "E".
    	       if isinstance(comp, Contact):
    		   emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
    	       elif isinstance(comp, ContactRing):
    		   # check for either base or collector contact ring
    		   if comp.getName() == 'B':
    		       for dir in [NORTH, SOUTH, EAST, WEST]:
    			   basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
    		   elif comp.getName() == 'C':
    		       for dir in [NORTH, SOUTH, EAST, WEST]:
    			   collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))


    def findComponent(self):
        # create component name from base name
        name = self.baseName
        # find this component in the array of NPN cells
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

class vnpn(npn):

    @classmethod
    def defineParamSpecs(cls, specs):

        mySpecs = ParamSpecArray()

        # check to see if any default parameter values have already been defined
        # for this class; if so, then use these values for the default values.
        if not hasattr(cls, 'default'):
            cls.default = dict()

        # define parameters to support rows and columns
        gridSize = specs.tech.getGridResolution()
	#mySpecs('we', cls.default.get('we', 2.0), 
        #        'emitter width',
        #        StepConstraint(gridSize, 2.0, None, action=REJECT))
		
	mySpecs('we', cls.default.get('we', 2.0), 
                'emitter width')
		
        #mySpecs('he', cls.default.get('he', 2.0),
        #        'emitter height',
        #        StepConstraint(gridSize, 2.0, None, action=REJECT))
		
	mySpecs('he', cls.default.get('he', 2.0),
                'emitter height')

        # define parameter to support rulesets
        mySpecs('ruleset', cls.default.get('ruleset', 'construction'), 
                'Ruleset type (construction or recommended)',
                ChoiceConstraint(['construction', 'recommended']))                        

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    def setupParams(self, params):
        # set the necessary parameter values
    
        # call method on base npn class
        npn.setupParams(self, params)
	
    def createPins(self):
    	# assign all emitter pins to pin "E"
    	emitterPin = Pin('E', 'E')
    	basePin = Pin('B', 'B')
    	collectorPin = Pin('C', 'C')
    	npnComp = self.findComponent()
    	for comp in npnComp.getComps():
    	       # check to see if this is an emitter contact;
    	       # if so, then assign this shape to pin "E".
    	       if isinstance(comp, Contact):
    		   emitterPin.addShape(Rect(self.metalLayer, comp.getRefBox()))
    	       elif isinstance(comp, ContactRing):
    		   # check for either base or collector contact ring
    		   if comp.getName() == 'B':
    		       for dir in [NORTH, SOUTH, EAST, WEST]:
    			   basePin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
    		   elif comp.getName() == 'C':
    		       for dir in [NORTH, SOUTH, EAST, WEST]:
    			   collectorPin.addShape(Rect(self.metalLayer, comp.getContact(dir).getRefBox()))
