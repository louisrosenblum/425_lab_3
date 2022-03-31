#######################################################################
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
# Mosfet3.py                                                           #
#                                                                      #
########################################################################
"""Module: Mosfet3

This module implements a MosfetTemplate class for creating MOS
transistor PyCells.






MosfetTemplate provides the following capabilities:
    - (float  )  Transistor width
    - (float  )  Transistor length
    - (integer)  Fingers, number of transistors

    - (string )  Diffusion contact coverage
    - (string )  Diffusion contact alignment
    - (string )  Diffusion contact wire connection

    - (string )  Gate contact location
    - (string )  Gate contact coverage
    - (string )  Gate contact alignment

    - (string )  Design rule set
    - (float  )  Diffusion contact to gate spacing
    - (float  )  Left  diffusion extension
    - (float  )  Right diffusion extension

    - (string )  Guard ring locations.



    - (string )  Gate oxide voltage tolerance
    - Stretch handles for contacts
    - Electrical connectivity, i.e. nets, pins, terminals.



Class variables:
    - (string )  contact,   layer name
    - (string )  diffusion, layer name
    - (string )  poly,      layer name
    - (string )  metal1,    layer name
    - (string )  metal2,    layer name

    - (list   )  encLayers, list of layer names
    - (list   )  envLayers, list of layer names



Technology file requirements:
    - (minEnclosure  poly       diffusion)
    - (minEnclosure  diffusion  poly     )
    - (minSpacing    contact    poly     )
    - (minSpacing    poly                )
    - (minWidth      contact             )



Module dependencies:
    - cni.dlo,      Ciranova PyCell APIs.



Exceptions:
    - ValueError, for incorrect parameter values.
    """

from __future__ import with_statement

__version__  = "$Revision: #1 $"
__fileinfo__ = "$Id: //depot/deviceKits_4.2.5/baseKit/Mosfet3.py#1 $"
__author__   = "Lyndon C. Lim"

import traceback

from cni.dlo import (
    Box,
    ChoiceConstraint,
    DeviceContext,
    Direction,
    DloGen,
    FailAction,
    Grid,
    Grouping,
    Instance,
    Layer,
    LayerMaterial,
    Location,
    Net,
    ParamArray,
    ParamSpecArray,
    Pin,
    Point,
    RangeConstraint,
    Rect,
    Ruleset,
    Shape,
    ShapeFilter,
    SnapType,
    StepConstraint,
    Term,
    TermType,
    Text,
    Unique,
)

from MosUtils import (
    calculateDeviceParameter,
    getComp,
    getCompsSorted,
    orderedRuleset,
    rulesmgr,
    ContactCenter,
    ContactEdge,
    ContactEdge1,
    ContactGate,
    ContactGate1,
    EnclosingRects,
    EnclosingRectsAbut,
    GuardRing,
    LayerDict,
    MosBody,
    MosBody1,
    MosDummy,
    MosDummy1,
    MosGate,
    MosStack2,
    Pattern,
    RulesDict,
    ViaX,
)

from cni.integ.common import (
    createInstances,
    renameParams,
    reverseDict,
    stretchHandle,
    Compare
)

########################################################################

class MosfetTemplate( DloGen):
    """Defines a MosfetTemplate class.
        """
    tranType   = "nmos"
    oxide      = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        metal2       = ( "M2",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = None,
    )

    encLayers  = [ "implant"]
    envLayers  = [ "implant"]

    transistorContext  = None
    guardringContext   = None

    paramNames = dict(
        w                  = "w",
        l                  = "l",
        fingers            = "fingers",

        diffLeftStyle      = "diffLeftStyle",
        diffRightStyle     = "diffRightStyle",
        diffContactCov     = "diffContactCov",
        diffContactJustify = "diffContactJustify",
        diffContactWire    = "diffContactWire",

        gateContact        = "gateContact",
        gateContactCov     = "gateContactCov",
        gateContactAlign   = "gateContactAlign",

        ruleset            = "ruleset",
        cgSpacingAdd       = "cgSpacingAdd",
        leftDiffAdd        = "leftDiffAdd",
        rightDiffAdd       = "rightDiffAdd",

        guardRing          = "guardRing",
    )

    default = dict()

    ####################################################################

    @classmethod
    def defineParamSpecs( cls, specs):
        """Define the PyCell parameters.  The order of invocation of
        specs() becomes the order on the form.

        Arguments:
        specs - (ParamSpecArray)  PyCell parameters
            """
        mySpecs    = ParamSpecArray()

        maskgrid   = specs.tech.getGridResolution()
        resolution = specs.tech.uu2dbu(1) * 10

        # Minimum transistor dimensions.
        w = max( specs.tech.getMosfetParams( cls.tranType, cls.oxide, "minWidth"), cls.default.get( "w", -1))
        stepConstraint = StepConstraint( maskgrid, start=w, resolution=resolution, action=FailAction.REJECT)
        #mySpecs( "w", w, constraint = stepConstraint)
	mySpecs("w",w)

        l = max( specs.tech.getMosfetParams( cls.tranType, cls.oxide, "minLength"), cls.default.get( "l", -1))
        stepConstraint = StepConstraint( maskgrid, start=l, resolution=resolution, action=FailAction.REJECT)
        #mySpecs( "l", l, constraint = stepConstraint)
	mySpecs("l", l)
	#Nerses
	
        # fingers is a non-zero integer.
        stepConstraint = StepConstraint( 1, start=1, resolution=1, action=FailAction.REJECT)

        fingers = max( 1, cls.default.get( "fingers", 1))
        mySpecs( "fingers", fingers, constraint=stepConstraint)

        # Intentional blank.
        #

        # Left & right S/D end styles.
        parameters = (
            ("diffLeftStyle",  "ContactEdge1" ),
            ("diffRightStyle", "ContactEdge1" ),
        )
        choiceConstraint = ChoiceConstraint(["ContactEdge1", "MosDummy1"])
        for parameter in parameters:
            mySpecs( parameter[0], cls.default.get( parameter[0], parameter[1]), constraint=choiceConstraint)

        # Source/drain contact coverage.
        diffContactCov = max( 0.0, min( 1.0, cls.default.get( "diffContactCov", 1.0)))
        mySpecs( "diffContactCov",  diffContactCov, constraint=RangeConstraint( 0.0, 1.0))

        # Source/drain contact alignment.
        diffContactJustify = cls.default.get( "diffContactJustify", "center")
        mySpecs( "diffContactJustify",  diffContactJustify, constraint=ChoiceConstraint([ "top", "center", "bottom"]))

        # Source/drain contact connection.
        diffContactWire = cls.default.get( "diffContactWire", "none")
        mySpecs( "diffContactWire",  diffContactWire, constraint=ChoiceConstraint([ "none", "source", "drain", "both"]))

        # Gate contact option.
        gateContact = cls.default.get( "gateContact", "top")
        mySpecs( "gateContact",  gateContact, constraint=ChoiceConstraint([ "top", "bottom", "both", "none"]))

        # Gate contact coverage.
        gateContactCov = max( 0.0, min( 1.0, cls.default.get( "gateContactCov", 1.0)))
        mySpecs( "gateContactCov",  gateContactCov, constraint=RangeConstraint( 0.0, 1.0))

        # Gate contact alignment.
        gateContactAlign = cls.default.get( "gateContactAlign", "center")
        mySpecs( "gateContactAlign",  gateContactAlign, constraint=ChoiceConstraint([ "left", "center", "right"]))

        # Design ruleset.
        ruleset = cls.default.get( "ruleset", "construction")
        mySpecs( "ruleset",  ruleset, constraint=ChoiceConstraint([ "recommended", "construction"]))

        # Positive values only
        stepConstraint = StepConstraint( maskgrid, start=0.0, resolution=resolution, action=FailAction.REJECT)

        cgSpacingAdd = max( 0.0, cls.default.get( "cgSpacingAdd", 0.0))
        mySpecs( "cgSpacingAdd", cgSpacingAdd, constraint=stepConstraint)

        # Intentional blank.
        #

        leftDiffAdd  = max( 0.0, cls.default.get( "leftDiffAdd", 0.0))
        mySpecs( "leftDiffAdd", leftDiffAdd, constraint=stepConstraint)

        rightDiffAdd = max( 0.0, cls.default.get( "rightDiffAdd", 0.0))
        mySpecs( "rightDiffAdd", rightDiffAdd, constraint=stepConstraint)

        guardRing = cls.default.get( "guardRing", "")
        mySpecs( "guardRing", guardRing)

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    ####################################################################

    def setupParams( self, params):
        """Process PyCell parameters, prior to geometric construction.
        Decisions about process rules and PyCell-specific behaviors
        should be confined to this method.
        
        Create most useful format for variables to be used in later
        methods.

        Arguments:
        params - (ParamArray)  PyCell parameters
            """
        # Convert all parameters into instance attributes,
        #     which makes them globally available in all methods.
        # Parameter renaming
        self.paramNamesReversed = reverseDict( self.paramNames)
        myParams = ParamArray()
        renameParams( params, myParams, self.paramNamesReversed)

        for key in myParams:
            setattr( self, key, myParams[ key])

        self.diffContactJustify = dict(
            top    = Direction.NORTH,
            center = Direction.NORTH_SOUTH,
            bottom = Direction.SOUTH,
        )[ self.diffContactJustify]

        # Convert string to boolean
        if self.diffContactWire in ( "source", "both", ):
            self.sourceWire = True
        else:
            self.sourceWire = False

        if self.diffContactWire in ( "drain",  "both", ):
            self.drainWire = True
        else:
            self.drainWire = False

        # Convert string to Direction
        self.gateContact = dict(
            top    = [ Direction.NORTH],
            bottom = [ Direction.SOUTH],
            both   = [ Direction.NORTH, Direction.SOUTH],
            none   = [ ],
        )[ self.gateContact]

        self.gateContactAlign = dict(
            left   = Direction.WEST,
            center = Direction.EAST_WEST,
            right  = Direction.EAST,
        )[ self.gateContactAlign]

        # Convert guard ring locations.
        self.guardRing = GuardRing.convertStringToList( self.guardRing)

        # Convert to process layer names
        self.layer      = LayerDict( self.tech, self.layerMapping)
        self.encLayers  = [ self.layer[ l] for l in self.encLayers if l]
        self.envLayers  = [ self.layer[ l] for l in self.envLayers if l]

        # Design ruleset
        rulesets = [ "construction", "default"]
        if self.ruleset == "recommended":
            rulesets.insert( 0, "recommended")
        self.ruleset = orderedRuleset( self.tech, rulesets)

        # Final parameter checking
        self.maskgrid = self.tech.getGridResolution()
        self.grid     = Grid( self.maskgrid, snapType=SnapType.CEIL)

        # Check for legal minimum again because it may depend changes in parameters.
        minW   = self.tech.getMosfetParams( self.tranType, self.oxide, "minWidth")
        minW   = self.grid.snap( minW)
        if self.w < 6e-5:
	    self.w = self.w*1e6	
	    self.w  = self.grid.snap( self.w)
	    
	#Nerses
        self.w = self.grid.snap( self.w)
        if self.w < minW:
            raise ValueError, "w (%f) is less than minimum (%f)." % ( self.w, minW)

        minL   = self.tech.getMosfetParams( self.tranType, self.oxide, "minLength")
        minL   = self.grid.snap( minL)
	
	if self.l < 6e-5:
	    self.l = self.l*1e6	
	    self.l  = self.grid.snap( self.l)
	#Nerses
        self.l = self.grid.snap( self.l)
        if self.l  < minL:
            raise ValueError, "l (%f) is less than minimum (%f)." % ( self.l, minL)

        # RuleDict for parameter to rule mapping.
        self.rules = RulesDict()
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.contact, Direction.EAST,     )] = self.rightDiffAdd
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.contact, Direction.WEST,     )] = self.leftDiffAdd
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.poly,    Direction.EAST,     )] = self.rightDiffAdd
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.poly,    Direction.WEST,     )] = self.leftDiffAdd
        self.rules[ ( "minClearance", self.layer.contact,   self.layer.poly,    Direction.EAST_WEST,)] = self.cgSpacingAdd

    ####################################################################

    def genTopology( self):
        """Define topology (connectivity) for multi-device circuit PyCells.
        Some terminals are created, then later destroyed.  This makes the
        coding simpler, since finger0 same as the base terminal.
            """
        dTerm = Term( "D", TermType.INPUT_OUTPUT)
        gTerm = Term( "G", TermType.INPUT       )
        sTerm = Term( "S", TermType.INPUT_OUTPUT)
        bTerm = Term( "B", TermType.INPUT_OUTPUT)

        # Additional gate terminals for multi-fingers
        if not self.gateContact:
            for i in range( 1, self.fingers):
                termName = "G_%d" % i
                termObj  = Term( termName, TermType.INPUT)
                termObj.setMustJoin( gTerm)

        # Additional drain terminals for multi-fingers
        if not self.drainWire:
            for i in range( 0, self.fingers + 1, 2):
                termObj  = Term( "D_%d" % (i / 2), TermType.INPUT_OUTPUT)
                termObj.setMustJoin( dTerm)

        # Additional source terminals for multi-fingers
        if not self.sourceWire:
            for i in range( 1, self.fingers + 1, 2):
                termObj  = Term( "S_%d" % (i / 2), TermType.INPUT_OUTPUT)
                termObj.setMustJoin( sTerm)

    ####################################################################

    def sizeDevices( self):
        """Define device sizes within multi-device circuit PyCells.
            """
        pass

    ####################################################################

    def genLayout( self):
        """Main body of geometric construction code.  Create the transistor
        body.  Add gate contact.
            """
        with rulesmgr( self.tech, Ruleset, self.ruleset):
            with rulesmgr( self.tech, DeviceContext, self.transistorContext):
                # Create transistor body.
                self.createOneRow()

                # Final touches.
                all = self.makeGrouping()
                EnclosingRectsAbut( all, self.encLayers).ungroup()
                all.ungroup()



        if self.guardRing:
            with rulesmgr( self.tech, Ruleset, self.ruleset):
                with rulesmgr( self.tech, DeviceContext, self.guardringContext):
                    GuardRing(
                        comps        = self.getComps(),
                        lowerLayer   = self.layer.tapDiffusion,
                        upperLayer   = self.layer.metal1,
                        locations    = self.guardRing,
                        implantLayer = self.layer.tapImplant,
                        encLayers    = self.encLayers,
                    )



        # Stretch handles and electrical connectivity.
        self.addStretchProperties()
        self.setPins()

    ####################################################################

    def addStretchProperties(
        self):
        """Add stretch handle information for layout editors.
            """
        mosBody = getComp( self, MosBody)

        # Gate W & L.
        minW = calculateDeviceParameter( self.tech, self.tranType, self.oxide, "minWidth", [ self.layer.contact, self.layer.diffusion])
        minW = self.grid.snap( minW)

        # Minimum transistor length based on process requirement.
        minL = self.tech.getMosfetParams( self.tranType, self.oxide, "minLength")
        minL = self.grid.snap( minL)

        g = mosBody.getComp( MosGate)
        if g:
            rect = [ comp for comp in g.getLeafComps() if comp.getLayer() == self.layer.diffusion]
            if rect:
                rect = rect[ 0]

                sname = Unique.Name()
                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames[ "w"],
                    location    = Location.UPPER_CENTER,
                    direction   = Direction.NORTH_SOUTH,
                    stretchType = "relative",
                    minVal      = minW,
                    userSnap    = "%f" % ( 2.0 * self.maskgrid),
                )

                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames[ "l"],
                    location    = Location.CENTER_RIGHT,
                    direction   = Direction.EAST_WEST,
                    stretchType = "relative",
                    minVal      = minL,
                    userSnap    = "%f" % ( 2.0 * self.maskgrid),
                )

    ####################################################################

    def createOneRow( self):
        """Create the transistor body.  Add gate contact.
            """
        # Create transistor body.
        mosBody = MosBody1(
            diffLayer       = self.layer.diffusion,
            gateLayer       = self.layer.poly,
            metal1Layer     = self.layer.metal1,
            metal2Layer     = self.layer.metal2,
            contactLayer    = self.layer.contact,
            fingers         = self.fingers,
            gateWidth       = self.w,
            gateLength      = self.l,
            coverage        = self.diffContactCov,
            diffLeftStyle   = "ContactEdge1",
            diffRightStyle  = "ContactEdge1",
            flip            = False,
            envLayers       = self.envLayers,
            justify         = self.diffContactJustify,
            withGateContact = (self.fingers < 2),
            addRules        = self.rules,
        )
        mosBody.unlock()
        env = EnclosingRects( mosBody, self.envLayers, grid=self.grid)



        # Connect source, then drain contacts.
        if self.sourceWire and ( self.fingers > 2):
            pattern  = Pattern.odd( self.fingers + 1)
            diffConn = mosBody.addDiffConn(
                direction = Direction.NORTH,
                pattern   = pattern,
                env       = env,
            )
            mosBody.wireDiffConn( diffConn, Direction.NORTH, pattern)

        if self.drainWire  and ( self.fingers > 1):
            pattern  = Pattern.even( self.fingers + 1)
            diffConn = mosBody.addDiffConn(
                direction = Direction.SOUTH,
                pattern   = pattern,
                env       = env)
            mosBody.wireDiffConn( diffConn, Direction.SOUTH, pattern)



        # Create gate contact.
        for gateContactDir in self.gateContact:
            polyFilter  = ShapeFilter( self.layer.poly)
            box         = mosBody.getBBox( polyFilter)
            width       = box.getWidth()
            gateContact = ContactGate1(
                lowerLayer = self.layer.poly,
                upperLayer = self.layer.metal1,
                width      = width,
                coverage   = self.gateContactCov,
                justify    = self.gateContactAlign,
                addRules   = self.rules,
            )

            # Place gate contact.
            pattern = Pattern.all( self.fingers)
            mosBody.addGateConn(
                direction  = gateContactDir,
                pattern    = pattern,
                gateConn   = gateContact,
                pitchMatch = False,
                env        = env,
            )

            # Wire gate contact.
            mosBody.wireGateConn(
                gateConn   = gateContact,
                pattern    = pattern,
            )



        # Update leftmost and rightmost S/D diffusion for dummies.
        mosBody.changeEndStyle( self.diffLeftStyle, self.diffRightStyle)



        env.destroy()
        mosBody.lock()

    ####################################################################

    def setPins(
        self):
        """Model electrical connectivity.

        Gate pins
            Weakly/resistively connected.

        Source/drain pins
            Multiple pins per source/drain, which must be externally
            connected (must-join).  Metal and diffusion rectangles
            are strongly connected within a single source/drain.
            """
        guardRing = getComp( self, GuardRing)
        if guardRing:
            guardRing.setPin(
                pinName  = "B",
                termName = "B",
            )



        mosBody = getComp( self, MosBody)

        # Define gate pins.
        if self.gateContact:
            gateContact = mosBody.getComp( ContactGate)
            gateContact.setPin(
                pinName  = "G",
                termName = "G",
                layer=[ self.layer.metal1]
            )
        else:
            comps = mosBody.getCompsSorted( objType=MosGate)
            comps[ 0].setPin(
                pinNamePrefix = "G",
                termName      = "G",
            )

            for i in range( 1, len( comps)):
                name = "G_%d" % i
                comps[ i].setPin(
                    pinNamePrefix = name,
                    termName      = name,
                )



        # Define drain and source pins.
        comps = mosBody.getCompsSorted( objType=( ContactEdge, ContactCenter, MosDummy, ))
        conns = mosBody.getCompsSorted( objType=ViaX, sortFunction=Compare.cmpCenterYAscend)

        # Drain pin.
        if self.drainWire  and ( self.fingers > 1):
            conns[ 0].setPin( "D", "D")
        else:
            for i in range( 0, len( comps), 2):
                name  = "D_%d" % (i / 2)
                comps[ i].setPin( name, name, layer=[ self.layer.metal1])

        # Source pin.
        if self.sourceWire and ( self.fingers > 2):
            conns[ -1].setPin( "S", "S")
        else:
            for i in range( 1, len( comps), 2):
                name  = "S_%d" % (i / 2)
                comps[ i].setPin( name, name, layer=[ self.layer.metal1])



        # Remove redundant terminals for finger0, and reassign
        # pins to base terminals.
        rename = dict(
            D_0 = "D",
            S_0 = "S",
        )

        for old in rename:
            pin  = Pin.find( old)
            if pin:
                pin.setName( rename[ old])

                term = Term.find( rename[ old])
                pin.setTerm( term)

                term = Term.find( old)
                term.destroy()

                net  = Net.find( old)
                net.destroy()

########################################################################

class Pmos( MosfetTemplate):
    """Pmos class implements PMOS transistors.
        """
    tranType  = "pmos"
    oxide     = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        metal2       = ( "M2",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
    )

    encLayers  = [ "implant", "well"]
    envLayers  = [ "implant", "well"]

########################################################################

class Nmos( MosfetTemplate):
    """Nmos class implements NMOS transistors.
        """
    tranType  = "nmos"
    oxide     = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        metal2       = ( "M2",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = None,
    )

    encLayers  = [ "implant"]
    envLayers  = [ "implant"]

########################################################################

class PmosH( MosfetTemplate):
    """PmosH class implements high voltage PMOS transistors.
        """
    tranType  = "pmos"
    oxide     = "thick"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        metal2       = ( "M2",  "drawing"),
        poly         = ( "A_PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "DIFF_25",     "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################

class NmosH( MosfetTemplate):
    """NmosH class implements high voltage NMOS transistors.
        """
    tranType  = "nmos"
    oxide     = "thick"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        metal2       = ( "M2",  "drawing"),
        poly         = ( "A_PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "DIFF_25",     "drawing"),
    )

    encLayers  = [ "implant", "od2"]
    envLayers  = [ "implant", "od2"]

########################################################################
#                                                                      #
# End                                                                  #
#                                                                      #
########################################################################

########################################################################
#                                                                      #
# Define self-tests                                                    #
#                                                                      #
########################################################################

if __name__ == "__main__":

    paramNames = dict(
        w                   = "w",
        l                   = "l",
        fingers             = "fingers",

        diffLeftStyle       = "diffLeftStyle",
        diffRightStyle      = "diffRightStyle",

        diffContactCov      = "diffContactCov",
        diffContactJustify  = "diffContactJustify",
        diffContactWire     = "diffContactWire",

        gateContact         = "gateContact",
        gateContactCov      = "gateContactCov",
        gateContactAlign    = "gateContactAlign",

        ruleset             = "ruleset",
        cgSpacingAdd        = "cgSpacingAdd",
        leftDiffAdd         = "leftDiffAdd",
        rightDiffAdd        = "rightDiffAdd",

        guardRing           = "guardRing",
    )

    def makeInstances(
        dlogen,
        masters,
        widths,
        lengths,
        fingers,
        diffLeftStyles,
        diffRightStyles,
        diffContactCovs,
        diffContactJustifys,
        diffContactWires,
        gateContacts,
        gateContactCovs,
        gateContactAligns,
        cgSpacingAdds,
        leftDiffAdds,
        rightDiffAdds,
        guardRings):
        """Create layout instances for quick development debugging.
            """
        paramSets = []
        for master in masters:
            # Assume the default parameters are minimum dimensions.
            inst   = Instance(("%s" % master))
            params = inst.getParams()

            listWidths  = [ params["w"]]
            listWidths.extend( widths)

            listLengths = [ params["l"]]
            listLengths.extend( lengths)
            inst.destroy()

            for w in listWidths:
                for l in listLengths:
                    for finger in fingers:
                        for diffLeftStyle in diffLeftStyles:
                            for diffRightStyle in diffRightStyles:
                                for diffContactCov in diffContactCovs:
                                    for diffContactJustify in diffContactJustifys:
                                        for diffContactWire in diffContactWires:
                                            for leftDiffAdd in leftDiffAdds:
                                                for rightDiffAdd in rightDiffAdds:
                                                    for cgSpacingAdd in cgSpacingAdds:
                                                        for gateContact in gateContacts:
                                                            for gateContactCov in gateContactCovs:
                                                                for gateContactAlign in gateContactAligns:
                                                                    for guardRing in guardRings:
                                                                        params = ParamArray(
                                                                            w                  = w,
                                                                            l                  = l,
                                                                            fingers            = finger,

                                                                            diffLeftStyle      = diffLeftStyle,
                                                                            diffRightStyle     = diffRightStyle,

                                                                            diffContactCov     = diffContactCov,
                                                                            diffContactJustify = diffContactJustify,
                                                                            diffContactWire    = diffContactWire,

                                                                            gateContact        = gateContact,
                                                                            gateContactCov     = gateContactCov,
                                                                            gateContactAlign   = gateContactAlign,

                                                                            cgSpacingAdd       = cgSpacingAdd,
                                                                            leftDiffAdd        = leftDiffAdd,
                                                                            rightDiffAdd       = rightDiffAdd,

                                                                            guardRing          = guardRing,
                                                                        )
                                                                        paramSets.append( [ master, params])

        createInstances( paramSets, paramNames, minColWidth=30, minRowHeight=30)



    def tinytest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters             = ( "Pmos3", "Nmos3", ),
            widths              = ( 1.3, ),
            lengths             = ( 0.5, ),
            fingers             = ( 1, 3, ),
            diffLeftStyles      = ( "ContactEdge1", ),
            diffRightStyles     = ( "ContactEdge1", ),
            diffContactCovs     = ( 1.0, ),
            diffContactJustifys = ( "center", ),
            diffContactWires    = ( "both", ),
            gateContacts        = ( "none", "top", ),
            gateContactCovs     = ( 1.0, ),
            gateContactAligns   = ( "center", ),
            cgSpacingAdds       = ( 0.0, ),
            leftDiffAdds        = ( 0.0, ),
            rightDiffAdds       = ( 0.0, ),
            guardRings          = ( "", ),
        )
        self.save()



    def smalltest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters             = ( "Pmos3", ),
            widths              = ( 1.3, ),
            lengths             = ( 0.5, ),
            fingers             = ( 1, 2, 3, ),
            diffLeftStyles      = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles     = ( "ContactEdge1", "MosDummy1", ),
            diffContactCovs     = ( 0.8, ),
            diffContactJustifys = ( "center", ),
            diffContactWires    = ( "none", "source", "drain", "both"),
            gateContacts        = ( "none", "top", ),
            gateContactCovs     = ( 0.8, ),
            gateContactAligns   = ( "center", ),
            cgSpacingAdds       = ( 0.0, ),
            leftDiffAdds        = ( 0.0, ),
            rightDiffAdds       = ( 0.0, ),
            guardRings          = ( "top,bottom,left,right", "", ),
        )
        self.save()



    def bigtest1( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters             = ( "Pmos3", ),
            widths              = ( 0.8, ),
            lengths             = ( 0.3, ),
            fingers             = ( 1, 2),
            diffLeftStyles      = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles     = ( "ContactEdge1", "MosDummy1", ),
            diffContactCovs     = ( 0.8, 1.0, ),
            diffContactJustifys = ( "center", ),
            diffContactWires    = ( "source", "drain", "none", ),
            gateContacts        = ( "none", "top", ),
            gateContactCovs     = ( 0.8, ),
            gateContactAligns   = ( "center", ),
            cgSpacingAdds       = ( 0.0, 0.2, ),
            leftDiffAdds        = ( 0.0, ),
            rightDiffAdds       = ( 0.0, ),
            guardRings          = ( "top,bottom,left,right", "", ),
        )
        self.save()



    def bigtest2( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters             = ( "Nmos3", ),
            widths              = ( 1.0, ),
            lengths             = ( 0.5, ),
            fingers             = ( 1, 2),
            diffLeftStyles      = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles     = ( "ContactEdge1", "MosDummy1", ),
            diffContactCovs     = ( 0.8, ),
            diffContactJustifys = ( "center", ),
            diffContactWires    = ( "source", "drain", "none", ),
            gateContacts        = ( "none", "top", ),
            gateContactCovs     = ( 0.8, 1.0, ),
            gateContactAligns   = ( "center", ),
            cgSpacingAdds       = ( 0.0, ),
            leftDiffAdds        = ( 0.0, 0.2, ),
            rightDiffAdds       = ( 0.0, ),
            guardRings          = ( "top,left", "", ),
        )
        self.save()



    def bigtest3( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters             = ( "PmosH3", ),
            widths              = ( 1.3, ),
            lengths             = ( 0.8, ),
            fingers             = ( 1, 2),
            diffLeftStyles      = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles     = ( "ContactEdge1", "MosDummy1", ),
            diffContactCovs     = ( 0.8, ),
            diffContactJustifys = ( "top", "center", ),
            diffContactWires    = ( "source", "drain", "none", ),
            gateContacts        = ( "none", "top", ),
            gateContactCovs     = ( 0.8, ),
            gateContactAligns   = ( "center", ),
            cgSpacingAdds       = ( 0.0, ),
            leftDiffAdds        = ( 0.0, ),
            rightDiffAdds       = ( 0.0, ),
            guardRings          = ( "top,bottom,", "", ),
        )
        self.save()



    def bigtest4( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters             = ( "NmosH3", ),
            widths              = ( 2.5, ),
            lengths             = ( 1.0, ),
            fingers             = ( 1, 2),
            diffLeftStyles      = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles     = ( "ContactEdge1", "MosDummy1", ),
            diffContactCovs     = ( 0.8, ),
            diffContactJustifys = ( "center", ),
            diffContactWires    = ( "source", "drain", "none", ),
            gateContacts        = ( "none", "top", ),
            gateContactCovs     = ( 0.8, ),
            gateContactAligns   = ( "left", "center", ),
            cgSpacingAdds       = ( 0.0, ),
            leftDiffAdds        = ( 0.0, ),
            rightDiffAdds       = ( 0.0, ),
            guardRings          = ( "left,right", "", ),
        )
        self.save()



    # TEST is defined externally from this file.
    # For building the test cases, invoke like this:
    # cnpy -c "TEST='SMALL';LIB='MyPyCellLib_cni180';execfile('Mosfet3.py')"
    if "TEST" in vars():
        if   vars()[ "TEST"] == "SMALL":
            DloGen.withNewDlo( tinytest,  vars()["LIB"], "TINYTEST_Mosfet3",  "layout")
            DloGen.withNewDlo( smalltest, vars()["LIB"], "SMALLTEST_Mosfet3", "layout")
        elif vars()[ "TEST"] == "BIG":
            DloGen.withNewDlo( bigtest1,  vars()["LIB"], "BIGTEST1_Mosfet3",  "layout")
            DloGen.withNewDlo( bigtest2,  vars()["LIB"], "BIGTEST2_Mosfet3",  "layout")
            DloGen.withNewDlo( bigtest3,  vars()["LIB"], "BIGTEST3_Mosfet3",  "layout")
            DloGen.withNewDlo( bigtest4,  vars()["LIB"], "BIGTEST4_Mosfet3",  "layout")

# end
