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
# Mosfet2.py                                                           #
#                                                                      #
########################################################################
"""Module: Mosfet2

This module implements a MosfetTemplate class for creating MOS
transistor PyCells.






MosfetTemplate provides the following capabilities:
    - (float  )  Transistor width
    - (float  )  Transistor length
    - (integer)  Fingers, number of transistors

    - (string )  Left   diffusion style
    - (float  )  Left   diffusion contact, bottom offset
    - (float  )  Left   diffusion contact, top    offset
    - (float  )  Left   diffusion extension

    - (boolean)  Center diffusion contacts
    - (float  )  Center diffusion contact, bottom offset
    - (string )  Center diffusion contact, top    offset

    - (string )  Right  diffusion style
    - (float  )  Right  diffusion contact, bottom offset
    - (float  )  Right  diffusion contact, top    offset
    - (float  )  Right  diffusion extension

    - (string )  Gate contact
    - (float  )  Gate contact, left  offset
    - (float  )  Gate contact, right offset
    - (float  )  Gate contact, top extension

    - (string )  Design rule set
    - (float  )  Diffusion contact to gate spacing
    - (string )  Gate oxide voltage tolerance

    - (string )  Guard ring locations.

    - Stretch handles for contacts

    - Auto-abutment
    - Electrical connectivity, i.e. nets, pins, terminals.



MosfetTemplate2 is derived from and provides all the capabilities
of MosfetTemplate.  In addition, MosfetTemplate2 provides an
additional parameter, m, which multiplies the transistor width.
    - (integer)  transistor width multiplier



Class variables:
    - (string )  contact,   layer name
    - (string )  diffusion, layer name
    - (string )  poly,      layer name
    - (string )  metal1,    layer name

    - (string )  well,      layer name
    - (string )  implant,   layer name
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



Other notes:
    [1] Dogbone configurations are not supported.
    """

from __future__ import with_statement

__version__  = "$Revision: #1 $"
__fileinfo__ = "$Id: //depot/deviceKits_4.2.5/baseKit/Mosfet2.py#1 $"
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
    BorrowGrouping,
    ContactCenter,
    ContactEdge,
    ContactEdge2,
    ContactEdgeAbut2,
    ContactGate,
    ContactGate2,
    DiffAbut,
    DiffEdge,
    DiffEdgeAbut,
    DiffHalf,
    EnclosingRects,
    EnclosingRectsAbut,
    GuardRing,
    LayerDict,
    MosBody,
    MosBody2,
    MosDiffusion,
    MosDummy,
    MosDummy2,
    MosGate,
    MosStack2,
    Pattern,
    RulesDict,
)

from cni.integ.common import (
    autoAbutment,
    createInstances,
    renameParams,
    reverseDict,
    stretchHandle,
    Compare,
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
        w                             = "w",
        l                             = "l",
        nf                            = "nf",

        diffLeftStyle                 = "diffLeftStyle",
        diffRightStyle                = "diffRightStyle",

        diffContactLeftBottomOffset   = "diffContactLeftBottomOffset",
        diffContactLeftTopOffset      = "diffContactLeftTopOffset",

        diffContactCenterBottomOffset = "diffContactCenterBottomOffset",
        diffContactCenterTopOffset    = "diffContactCenterTopOffset",

        diffContactRightBottomOffset  = "diffContactRightBottomOffset",
        diffContactRightTopOffset     = "diffContactRightTopOffset",

        gateContact                   = "gateContact",
        gateContactLeftOffset         = "gateContactLeftOffset",
        gateContactRightOffset        = "gateContactRightOffset",

        ruleset                       = "ruleset",
        cgSpacingAdd                  = "cgSpacingAdd",
        leftDiffAdd                   = "leftDiffAdd",
        rightDiffAdd                  = "rightDiffAdd",

        guardRing                     = "guardRing",
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
        maskgridX2 = 2.0 * maskgrid
        gridX2     = Grid( maskgridX2, snapType=SnapType.CEIL)
        resolution = specs.tech.uu2dbu(1) * 10

        # Minimum transistor width matches diffusion contact to avoid dogbone.
        layer = LayerDict( specs.tech, cls.layerMapping)

        w = max(
            calculateDeviceParameter(
                specs.tech, cls.tranType, cls.oxide, "minWidth", [ layer.contact, layer.diffusion],
                ruleset=[ cls.default.get( "ruleset", "construction"), "default"],
                deviceContext=cls.transistorContext,
            ),
            cls.default.get( "w", -1.0),
        )
        stepConstraint = StepConstraint( maskgrid, start=w, resolution=resolution, action=FailAction.REJECT)
        #mySpecs( "w", w, constraint = stepConstraint)
	mySpecs ("w",w)
	
        # Minimum transistor length based on process requirement.
        # 2x grid requirement because PyCell uses path constructs.
        l = max(
            calculateDeviceParameter(
                specs.tech, cls.tranType, cls.oxide, "minLength", [ layer.poly],
                ruleset=[ cls.default.get( "ruleset", "construction"), "default"],
                deviceContext=cls.transistorContext,
            ),
            cls.default.get( "l", -1.0),
        )
        l = gridX2.snap( l)
        #print maskgridX2;
	stepConstraint = StepConstraint( maskgrid, start=l, resolution=resolution, action=FailAction.REJECT)
        #mySpecs( "l", l, constraint = stepConstraint)
	mySpecs("l",l)	
	#Nerses

        # fingers is a non-zero integer.
        stepConstraint = StepConstraint( 1, start=1, resolution=1, action=FailAction.REJECT)

        nf = max( 1, cls.default.get( "nf", 1))
        mySpecs( "nf", nf, constraint=stepConstraint)

        # Intentional blank.
        #

        # Left & right source/drain end styles.
        parameters = (
            ( "diffLeftStyle",  "ContactEdge2"),
            ( "diffRightStyle", "ContactEdge2"),
        )
        choiceConstraint = ChoiceConstraint(["ContactEdge2", "ContactEdgeAbut2", "DiffAbut", "DiffEdge", "DiffEdgeAbut", "DiffHalf", "MosDummy2"])
        for parameter in parameters:
            mySpecs( parameter[0], cls.default.get( parameter[0], parameter[1]), constraint=choiceConstraint)

        # Source/drain contact offsets, legal values <= 0.
        parameters = (
            ( "diffContactLeftBottomOffset",   0.0),
            ( "diffContactLeftTopOffset",      0.0),

            ( "diffContactCenterBottomOffset", 0.0),
            ( "diffContactCenterTopOffset",    0.0),

            ( "diffContactRightBottomOffset",  0.0),
            ( "diffContactRightTopOffset",     0.0),

            ( "gateContactLeftOffset",         0.0),
            ( "gateContactRightOffset",        0.0),
        )
        stepConstraint = StepConstraint( -maskgrid, start=0.0, resolution=resolution, action=FailAction.REJECT)
        for parameter in parameters:
            mySpecs( parameter[0], min( parameter[1], cls.default.get( parameter[0], parameter[1])), constraint=stepConstraint)

        # Optional gate contact.
        gateContact = cls.default.get( "gateContact", "none")
        mySpecs( "gateContact",  gateContact, constraint=ChoiceConstraint(["top", "bottom", "none"]))

        # Intentional blank.

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

        # Convert guard ring locations.
        self.guardRing = GuardRing.convertStringToList( self.guardRing)

        # Convert offsets to positive numbers.
        for key in (
            "diffContactLeftBottomOffset",
            "diffContactLeftTopOffset",
            "diffContactCenterBottomOffset",
            "diffContactCenterTopOffset",
            "diffContactRightBottomOffset",
            "diffContactRightTopOffset",
            "gateContactLeftOffset",
            "gateContactRightOffset"):

            setattr( self, key, abs( getattr( self, key)))

        # Convert string to Direction
        if self.gateContact == "top":
            self.gateContact = Direction.NORTH
        elif self.gateContact == "bottom":
            self.gateContact = Direction.SOUTH
        else:
            self.gateContact = None

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
        self.gridX2   = Grid( 2.0 * self.maskgrid, snapType=SnapType.CEIL)

        # Check for legal minimum again because it may depend
        # on the selected ruleset.
        minW    = calculateDeviceParameter(
            self.tech, self.tranType, self.oxide, "minWidth", [ self.layer.contact, self.layer.diffusion],
            ruleset=self.ruleset,
            deviceContext=self.transistorContext,
        )
        minW    = self.grid.snap( minW)
	
	if self.w < 6e-5:
	    self.w = self.w*1e6	
	    self.w  = self.grid.snap( self.w)
	
	#Nerses
	
        self.w  = self.grid.snap( self.w)
        if self.w < minW:
            raise ValueError, "w (%f) is less than minimum (%f)." % ( self.w, minW)

        minL    = calculateDeviceParameter(
            self.tech, self.tranType, self.oxide, "minLength", [ self.layer.poly],
            ruleset=self.ruleset,
            deviceContext=self.transistorContext,
        )
        minL    = self.gridX2.snap( minL)
	
	if self.l < 6e-5:
	    self.l = self.l*1e6	
	    self.l  = self.grid.snap( self.l)
	    
	#Nerses    
        self.l  = self.gridX2.snap( self.l)
        if self.l  < minL:
            raise ValueError, "lf (%f) is less than minimum (%f)." % ( self.lf, minL)

        for side in ( ( "diffLeftStyle", Direction.WEST), ( "diffRightStyle", Direction.EAST)):
            if eval( getattr( self, side[ 0])).isAbutable:
                if side[1] in self.guardRing:
                    raise ValueError, "%s (%s) is not compatible with guardRing direction (%s)." % ( side[0], getattr( self, side[0]), side[1])

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
            for i in range( 1, self.nf):
                termName = "G_%d" % i
                termObj = Term( termName, TermType.INPUT)
                termObj.setMustJoin( gTerm)

        # Additional source/drain terminals for multi-fingers
        termNames = ("D",   "S"   )
        termObjs  = (dTerm, sTerm )
        for i in range( 0, self.nf + 1):
            termName = "%s_%d" % ( termNames[ i % 2], i / 2)
            termObj  = Term( termName, TermType.INPUT_OUTPUT)
            termObj.setMustJoin( termObjs[ i % 2])

    ####################################################################

    def sizeDevices( self):
        """Define device sizes within multi-device circuit PyCells.
            """
        pass

    ####################################################################

    def genLayout( self):
        """Build the layout.  Use "construction" ruleset if available.
            """
        with RulesetManager( self.tech, self.ruleset):
            self.construct()

    ####################################################################

    def genLayout( self):
        """Main body of geometric construction code.  Create the transistor
        body.  Add gate contact.
            """
        self.props["diffLeftStyle"]  = self.diffLeftStyle
        self.props["diffRightStyle"] = self.diffRightStyle

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



        # Stretch handles, abutment, and electrical connectivity.
        self.addStretchProperties()
        self.addAbutProperties()
        self.setPins()

    ####################################################################

    def addStretchProperties(
        self):
        """Add stretch handle information for layout editors.
            """
        mosBody = getComp( self, MosBody)
        comps   = mosBody.getCompsSorted( objType=(MosDiffusion, MosDummy, ContactCenter, ContactEdge))

        # Leftmost diffusion contact.
        d    = comps[0]
        rect = [ comp for comp in d.getLeafComps() if comp.getLayer() == self.layer.metal1]
        if rect:
            rect.sort( Compare.cmpCenterXAscend)
            rect = rect[-1]

            sname = Unique.Name()
            stretchHandle(
                name        = sname,
                shape       = rect,
                parameter   = self.paramNames["diffContactLeftBottomOffset"],
                location    = Location.LOWER_CENTER,
                direction   = Direction.NORTH_SOUTH,
                stretchType = "relative",
                minVal      = -self.w,
                maxVal      = 0.0,
            )

            stretchHandle(
                name        = sname,
                shape       = rect,
                parameter   = self.paramNames["diffContactLeftTopOffset"],
                location    = Location.UPPER_CENTER,
                direction   = Direction.NORTH_SOUTH,
                stretchType = "relative",
                minVal      = -self.w,
                maxVal      = 0.0,
            )



        # Rightmost diffusion contact.
        b    = comps[-1]
        rect = [ comp for comp in b.getLeafComps() if comp.getLayer() == self.layer.metal1]
        if rect:
            rect.sort( Compare.cmpCenterXAscend)
            rect = rect[0]

            sname = Unique.Name()
            stretchHandle(
                name        = sname,
                shape       = rect,
                parameter   = self.paramNames["diffContactRightBottomOffset"],
                location    = Location.LOWER_CENTER,
                direction   = Direction.NORTH_SOUTH,
                stretchType = "relative",
                minVal      = -self.w,
                maxVal      = 0.0,
            )

            stretchHandle(
                name        = sname,
                shape       = rect,
                parameter   = self.paramNames["diffContactRightTopOffset"],
                location    = Location.UPPER_CENTER,
                direction   = Direction.NORTH_SOUTH,
                stretchType = "relative",
                minVal      = -self.w,
                maxVal      = 0.0,
            )



        # First center diffusion contact, if it exists.
        if len( comps) > 2:
            c    = comps[1]
            rect = [ comp for comp in c.getLeafComps() if comp.getLayer() == self.layer.metal1]
            if rect:
                rect = rect[0]

                sname = Unique.Name()
                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames["diffContactCenterBottomOffset"],
                    location    = Location.LOWER_CENTER,
                    direction   = Direction.NORTH_SOUTH,
                    stretchType = "relative",
                    minVal      = -self.w,
                    maxVal      = 0.0,
                )

                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames["diffContactCenterTopOffset"],
                    location    = Location.UPPER_CENTER,
                    direction   = Direction.NORTH_SOUTH,
                    stretchType = "relative",
                    minVal      = -self.w,
                    maxVal      = 0.0,
                )



        # Gate contact.
        g = mosBody.getCompsSorted( objType=ContactGate)
        if g:
            g = g[0]
            rect = [ comp for comp in g.getLeafComps() if comp.getLayer() == self.layer.metal1]
            if rect:
                rect  = rect[0]
                width = rect.getBBox().getWidth()

                sname = Unique.Name()
                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames["gateContactLeftOffset"],
                    location    = Location.CENTER_LEFT,
                    direction   = Direction.EAST_WEST,
                    stretchType = "relative",
                    minVal      = -width,
                    maxVal      = 0.0,
                )

                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames["gateContactRightOffset"],
                    location    = Location.CENTER_RIGHT,
                    direction   = Direction.EAST_WEST,
                    stretchType = "relative",
                    minVal      = -width,
                    maxVal      = 0.0,
                )



        # Gate W & L.
        minW = calculateDeviceParameter( self.tech, self.tranType, self.oxide, "minWidth", [ self.layer.contact, self.layer.diffusion])
        minW = self.grid.snap( minW)

        # Minimum transistor length based on process requirement.
        minL = self.tech.getMosfetParams( self.tranType, self.oxide, "minLength")
        minL = self.gridX2.snap( minL)

        g = mosBody.getCompsSorted( objType=MosGate)
        if g:
            g = g[0]
            rect = [ comp for comp in g.getLeafComps() if comp.getLayer() == self.layer.diffusion]
            if rect:
                rect = rect[0]

                sname = Unique.Name()
                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames["w"],
                    location    = Location.UPPER_CENTER,
                    direction   = Direction.NORTH_SOUTH,
                    stretchType = "relative",
                    minVal      = minW,
                    userSnap    = "%f" % ( 2.0 * self.maskgrid),
                )

                stretchHandle(
                    name        = sname,
                    shape       = rect,
                    parameter   = self.paramNames["l"],
                    location    = Location.CENTER_RIGHT,
                    direction   = Direction.EAST_WEST,
                    stretchType = "relative",
                    minVal      = minL,
                    userSnap    = "%f" % ( 2.0 * self.maskgrid),
                )

    ####################################################################

    def addAbutProperties(
        self):
        """Add abutment information for layout editors.
            """
        comps   = getComp( self, MosBody).getCompsSorted()
        d = comps[0]
        b = comps[-1]



        # Auto abutment
        if not isinstance( d, MosDummy):
            rect = d.getComp( Rect)
            rect.setName( "DRAIN")
            autoAbutment(
                rect,
                self.w,
                [ Direction.WEST],
                "cniMOS",
                abut2PinEqual   = [ { "spacing":0.0}, { "diffLeftStyle":"DiffHalf"        },  { "diffLeftStyle":"DiffHalf"        } ],
                abut2PinBigger  = [ { "spacing":0.0}, { "diffLeftStyle":"DiffEdgeAbut"    },  { "diffLeftStyle":"DiffEdgeAbut"    } ],
                abut3PinBigger  = [ { "spacing":0.0}, { "diffLeftStyle":"ContactEdgeAbut2"},  { "diffLeftStyle":"ContactEdgeAbut2"} ],
                abut3PinEqual   = [ { "spacing":0.0}, { "diffLeftStyle":"DiffAbut"        },  { "diffLeftStyle":"ContactEdgeAbut2"} ],
                abut2PinSmaller = [ { "spacing":0.0}, { "diffLeftStyle":"DiffEdgeAbut"    },  { "diffLeftStyle":"DiffEdgeAbut"    } ],
                abut3PinSmaller = [ { "spacing":0.0}, { "diffLeftStyle":"DiffEdgeAbut"    },  { "diffLeftStyle":"DiffEdgeAbut"    } ],
                noAbut          = [ { "spacing":0.4}],
                function        = "cniAbut",
            )

        if not isinstance( b, MosDummy):
            rect = b.getComp( Rect)
            rect.setName( "SOURCE")
            autoAbutment(
                rect,
                self.w,
                [ Direction.EAST],
                "cniMOS",
                abut2PinEqual   = [ { "spacing":0.0}, { "diffRightStyle":"DiffHalf"        }, { "diffRightStyle":"DiffHalf"        } ],
                abut2PinBigger  = [ { "spacing":0.0}, { "diffRightStyle":"DiffEdgeAbut"    }, { "diffRightStyle":"DiffEdgeAbut"    } ],
                abut3PinBigger  = [ { "spacing":0.0}, { "diffRightStyle":"ContactEdgeAbut2"}, { "diffRightStyle":"ContactEdgeAbut2"} ],
                abut3PinEqual   = [ { "spacing":0.0}, { "diffRightStyle":"DiffAbut"        }, { "diffRightStyle":"ContactEdgeAbut2"} ],
                abut2PinSmaller = [ { "spacing":0.0}, { "diffRightStyle":"DiffEdgeAbut"    }, { "diffRightStyle":"DiffEdgeAbut"    } ],
                abut3PinSmaller = [ { "spacing":0.0}, { "diffRightStyle":"DiffEdgeAbut"    }, { "diffRightStyle":"DiffEdgeAbut"    } ],
                noAbut          = [ { "spacing":0.4}],
                function        = "cniAbut",
            )

    ####################################################################

    def createOneRow( self):
        """Create the transistor body.  Add gate contact.
            """
        mosBody = MosBody2(
            diffLayer                     = self.layer.diffusion,
            gateLayer                     = self.layer.poly,
            metal1Layer                   = self.layer.metal1,
            contactLayer                  = self.layer.contact,
            nf                            = self.nf,
            gateWidth                     = self.w,
            gateLength                    = self.l,
            diffLeftStyle                 = self.diffLeftStyle,
            diffRightStyle                = self.diffRightStyle,
            diffContactLeftBottomOffset   = self.diffContactLeftBottomOffset,
            diffContactLeftTopOffset      = self.diffContactLeftTopOffset,
            diffContactCenterBottomOffset = self.diffContactCenterBottomOffset,
            diffContactCenterTopOffset    = self.diffContactCenterTopOffset,
            diffContactRightBottomOffset  = self.diffContactRightBottomOffset,
            diffContactRightTopOffset     = self.diffContactRightTopOffset,
            envLayers                     = self.envLayers,
            withGateContact               = (self.nf < 2),
            addRules                      = self.rules,
        )



        # Create gate contact.
        if self.gateContact:
            mosBody.unlock()
            env = EnclosingRects( mosBody, self.envLayers, grid=self.grid)

            tmpGroup = BorrowGrouping( components=mosBody.getCompsSorted( objType=MosGate))
            box      = tmpGroup.getBBox( ShapeFilter( self.layer.poly))
            width    = box.getWidth()
            tmpGroup.ungroup()
            gateContact = ContactGate2(
                lowerLayer  = self.layer.poly,
                upperLayer  = self.layer.metal1,
                width       = width,
                leftOffset  = self.gateContactLeftOffset,
                rightOffset = self.gateContactRightOffset,
            )

            # Place gate contact.
            pattern = Pattern.all( self.nf)
            mosBody.addGateConn(
                direction  = self.gateContact,
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
                layer=[ self.layer.poly, self.layer.metal1]
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



        # Define source/drain pins.
        termNames = ("D", "S")
        comps     = mosBody.getCompsSorted( objType=( ContactCenter, ContactEdge, MosDiffusion, MosDummy))
        for i in range( len( comps)):
            name  = "%s_%d" % ( termNames[ i % 2], i / 2)
            comps[ i].setPin(
                pinName  = name,
                termName = name,
                layer=[ self.layer.diffusion, self.layer.metal1],
            )



        # Remove redundant terminals for finger0, and reassign
        # pins to base terminals.
        rename = dict(
            D_0 = "D",
            S_0 = "S",
        )

        for old in rename:
            pin  = Pin.find( old)
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
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "DIFF_18",     "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################
class PmosHvt( MosfetTemplate):
    """PmosH class implements high voltage PMOS transistors.
        """
    tranType  = "pmos"
    oxide     = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "HVTIMP",     "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################
class NmosHvt( MosfetTemplate):
    """PmosH class implements high voltage PMOS transistors.
        """
    tranType  = "nmos"
    oxide     = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        #well         = ( "NWELL",   "drawing"),
        od2          = ( "HVTIMP",     "drawing"),
    )

    encLayers  = [ "implant", "od2"]
    envLayers  = [ "implant", "od2"]

########################################################################

########################################################################
class PmosLvt( MosfetTemplate):
    """PmosH class implements high voltage PMOS transistors.
        """
    tranType  = "pmos"
    oxide     = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "LVTIMP",     "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################
class NmosLvt( MosfetTemplate):
    """PmosH class implements high voltage PMOS transistors.
        """
    tranType  = "nmos"
    oxide     = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        #well         = ( "NWELL",   "drawing"),
        od2          = ( "LVTIMP",     "drawing"),
    )

    encLayers  = [ "implant","od2"]
    envLayers  = [ "implant","od2"]

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
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "DIFF_18",     "drawing"),
    )

    encLayers  = [ "implant", "od2"]
    envLayers  = [ "implant", "od2"]

########################################################################

class PmosH25( MosfetTemplate):
    """PmosH class implements high voltage PMOS transistors.
        """
    tranType  = "pmos"
    oxide     = "thicknes"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "DIFF_25",     "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################
########################################################################

class NmosH25( MosfetTemplate):
    """NmosH class implements high voltage NMOS transistors.
        """
    tranType  = "nmos"
    oxide     = "thicknes"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "DIFF_25",     "drawing"),
    )

    encLayers  = [ "implant", "od2"]
    envLayers  = [ "implant", "od2"]

########################################################################

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
        w                             = "w",
        l                             = "l",
        nf                            = "nf",

        diffLeftStyle                 = "diffLeftStyle",
        diffRightStyle                = "diffRightStyle",

        diffContactLeftBottomOffset   = "diffContactLeftBottomOffset",
        diffContactLeftTopOffset      = "diffContactLeftTopOffset",

        diffContactCenterBottomOffset = "diffContactCenterBottomOffset",
        diffContactCenterTopOffset    = "diffContactCenterTopOffset",

        diffContactRightBottomOffset  = "diffContactRightBottomOffset",
        diffContactRightTopOffset     = "diffContactRightTopOffset",

        gateContact                   = "gateContact",
        gateContactLeftOffset         = "gateContactLeftOffset",
        gateContactRightOffset        = "gateContactRightOffset",

        cgSpacingAdd                  = "cgSpacingAdd",
        leftDiffAdd                   = "leftDiffAdd",
        rightDiffAdd                  = "rightDiffAdd",

        guardRing                     = "guardRing",
    )

    def makeInstances(
        dlogen,
        masters,
        widths,
        lengths,
        nf,
        diffLeftStyles,
        diffRightStyles,
        cgSpacingAdds,
        leftDiffAdds,
        rightDiffAdds,
        gateContacts,
        gateContactLeftOffsets,
        diffContactLeftBottomOffsets,
        diffContactCenterBottomOffsets,
        diffContactRightBottomOffsets,
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
                    for nf in nf:
                        for diffLeftStyle in diffLeftStyles:
                            for diffRightStyle in diffRightStyles:
                                for cgSpacingAdd in cgSpacingAdds:
                                    for leftDiffAdd in leftDiffAdds:
                                        for rightDiffAdd in rightDiffAdds:
                                            for gateContact in gateContacts:
                                                for gateContactLeftOffset in gateContactLeftOffsets:
                                                    for diffContactLeftBottomOffset in diffContactLeftBottomOffsets:
                                                        for diffContactCenterBottomOffset in diffContactCenterBottomOffsets:
                                                            for diffContactRightBottomOffset in diffContactRightBottomOffsets:
                                                                for guardRing in guardRings:
                                                                    params = ParamArray(
                                                                        w = w,
                                                                        l = l,
                                                                        nf = nf,

                                                                        diffLeftStyle                 = diffLeftStyle,
                                                                        diffContactLeftBottomOffset   = diffContactLeftBottomOffset,
                                                                        diffContactLeftTopOffset      = diffContactLeftBottomOffset,

                                                                        diffContactCenterBottomOffset = diffContactCenterBottomOffset,
                                                                        diffContactCenterTopOffset    = diffContactCenterBottomOffset,

                                                                        diffRightStyle                = diffRightStyle,
                                                                        diffContactRightBottomOffset  = diffContactRightBottomOffset,
                                                                        diffContactRightTopOffset     = diffContactRightBottomOffset,

                                                                        gateContact                   = gateContact,
                                                                        gateContactLeftOffset         = gateContactLeftOffset,
                                                                        gateContactRightOffset        = gateContactLeftOffset,

                                                                        cgSpacingAdd                  = cgSpacingAdd,
                                                                        leftDiffAdd                   = leftDiffAdd,
                                                                        rightDiffAdd                  = rightDiffAdd,

                                                                        guardRing                     = guardRing,
                                                                    )
                                                                    paramSets.append( [ master, params])

        createInstances( paramSets, paramNames, minColWidth=30, minRowHeight=30)



    def tinytest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters                        = ( "Pmos2", "Nmos2", ),
            widths                         = ( 1.3, ),
            lengths                        = ( 0.5, ),
            nf                             = ( 1, 2),
            diffLeftStyles                 = ( "ContactEdge2", ),
            diffRightStyles                = ( "ContactEdge2", ),
            cgSpacingAdds                  = ( 0.0, ),
            leftDiffAdds                   = ( 0.0, ),
            rightDiffAdds                  = ( 0.0, ),
            gateContacts                   = ( "none", "top", ),
            gateContactLeftOffsets         = ( 0.0, ),
            diffContactLeftBottomOffsets   = ( 0.0, ),
            diffContactCenterBottomOffsets = ( 0.0, ),
            diffContactRightBottomOffsets  = ( 0.0, ),
            guardRings                     = ( "", ),
        )
        self.save()



    def smalltest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters                        = ( "Pmos2", ),
            widths                         = ( 1.3, ),
            lengths                        = ( 0.5, ),
            nf                             = ( 1, 2),
            diffLeftStyles                 = ( "ContactEdge2", "ContactEdgeAbut2", "DiffAbut", "DiffEdge", "DiffEdgeAbut", "DiffHalf", "MosDummy2", ),
            diffRightStyles                = ( "ContactEdge2", "ContactEdgeAbut2", "DiffAbut", "DiffEdge", "DiffEdgeAbut", "DiffHalf", "MosDummy2", ),
            cgSpacingAdds                  = ( 0.0, ),
            leftDiffAdds                   = ( 0.0, ),
            rightDiffAdds                  = ( 0.0, ),
            gateContacts                   = ( "none", "top", ),
            gateContactLeftOffsets         = ( 0.0, ),
            diffContactLeftBottomOffsets   = ( 0.0, ),
            diffContactCenterBottomOffsets = ( 0.0, ),
            diffContactRightBottomOffsets  = ( 0.0, ),
            guardRings                     = ( "top,bottom", "", ),
        )
        self.save()



    def bigtest1( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters                        = ( "Pmos2", ),
            widths                         = ( 0.8, ),
            lengths                        = ( 0.3, ),
            nf                             = ( 1, 2, 3, ),
            diffLeftStyles                 = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            diffRightStyles                = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            cgSpacingAdds                  = ( 0.0, 0.1, ),
            leftDiffAdds                   = ( 0.0, 0.1, ),
            rightDiffAdds                  = ( 0.0, ),
            gateContacts                   = ( "none", "top", "bottom", ),
            gateContactLeftOffsets         = ( 0.0, ),
            diffContactLeftBottomOffsets   = ( 0.0, ),
            diffContactCenterBottomOffsets = ( 0.0, ),
            diffContactRightBottomOffsets  = ( 0.0, ),
            guardRings                     = ( "top,bottom,left,right", "", ),
        )
        self.save()



    def bigtest2( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters                        = ( "Nmos2", ),
            widths                         = ( 1.3, ),
            lengths                        = ( 0.5, ),
            nf                             = ( 1, 2, 3, ),
            diffLeftStyles                 = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            diffRightStyles                = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            cgSpacingAdds                  = ( 0.0, 0.2, ),
            leftDiffAdds                   = ( 0.0, ),
            rightDiffAdds                  = ( 0.0, 0.2, ),
            gateContacts                   = ( "none", "top", "bottom", ),
            gateContactLeftOffsets         = ( -0.1, ),
            diffContactLeftBottomOffsets   = ( -0.1, ),
            diffContactCenterBottomOffsets = ( -0.1, ),
            diffContactRightBottomOffsets  = ( -0.1, ),
            guardRings                     = ( "top,left", "", ),
        )
        self.save()



    def bigtest3( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters                        = ( "PmosH2", ),
            widths                         = ( 2.0, ),
            lengths                        = ( 0.8, ),
            nf                             = ( 1, 2, 3, ),
            diffLeftStyles                 = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            diffRightStyles                = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            cgSpacingAdds                  = ( 0.0, 0.3, ),
            leftDiffAdds                   = ( 0.0, 0.3, ),
            rightDiffAdds                  = ( 0.0, ),
            gateContacts                   = ( "none", "top", "bottom", ),
            gateContactLeftOffsets         = ( -0.2, ),
            diffContactLeftBottomOffsets   = ( -0.2, ),
            diffContactCenterBottomOffsets = ( -0.2, ),
            diffContactRightBottomOffsets  = ( -0.2, ),
            guardRings                     = ( "top,bottom,", "", ),
        )
        self.save()



    def bigtest4( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters                        = ( "NmosH2", ),
            widths                         = ( 3.0, ),
            lengths                        = ( 1.0, ),
            nf                             = ( 1, 2, 3, ),
            diffLeftStyles                 = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            diffRightStyles                = ( "ContactEdge2", "DiffEdge", "MosDummy2", ),
            cgSpacingAdds                  = ( 0.0, 0.4, ),
            leftDiffAdds                   = ( 0.0, ),
            rightDiffAdds                  = ( 0.0, 0.4, ),
            gateContacts                   = ( "none", "top", "bottom", ),
            gateContactLeftOffsets         = ( -0.3, ),
            diffContactLeftBottomOffsets   = ( -0.3, ),
            diffContactCenterBottomOffsets = ( -0.3, ),
            diffContactRightBottomOffsets  = ( -0.3, ),
            guardRings                     = ( "left,right", "", ),
        )
        self.save()



    def bigtest5( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters                        = ( "Pmos2", "Nmos2", ),
            widths                         = ( 3.0, ),
            lengths                        = ( 1.0, ),
            nf                             = ( 1, 2, ),
            diffLeftStyles                 = ( "ContactEdgeAbut2", "DiffAbut", "DiffEdgeAbut", "DiffHalf", ),
            diffRightStyles                = ( "ContactEdgeAbut2", "DiffAbut", "DiffEdgeAbut", "DiffHalf", ),
            cgSpacingAdds                  = ( 0.0, ),
            leftDiffAdds                   = ( 0.0, ),
            rightDiffAdds                  = ( 0.0, ),
            gateContacts                   = ( "none", "top", "bottom", ),
            gateContactLeftOffsets         = ( 0.0, ),
            diffContactLeftBottomOffsets   = ( 0.0, ),
            diffContactCenterBottomOffsets = ( 0.0, ),
            diffContactRightBottomOffsets  = ( 0.0, ),
            guardRings                     = ( "",  ),
        )
        self.save()



    # TEST is defined externally from this file.
    # For building the test cases, invoke like this:
    # cnpy -c "TEST='SMALL';LIB='MyPyCellLib_cni180';execfile('Mosfet2.py')"
    if "TEST" in vars():
        if   vars()["TEST"] == "SMALL":
            DloGen.withNewDlo( tinytest,  vars()["LIB"], "TINYTEST_Mosfet2",  "layout")
            DloGen.withNewDlo( smalltest, vars()["LIB"], "SMALLTEST_Mosfet2", "layout")
        elif vars()["TEST"] == "BIG":
            DloGen.withNewDlo( bigtest1,  vars()["LIB"], "BIGTEST1_Mosfet2",  "layout")
            DloGen.withNewDlo( bigtest2,  vars()["LIB"], "BIGTEST2_Mosfet2",  "layout")
            DloGen.withNewDlo( bigtest3,  vars()["LIB"], "BIGTEST3_Mosfet2",  "layout")
            DloGen.withNewDlo( bigtest4,  vars()["LIB"], "BIGTEST4_Mosfet2",  "layout")
            DloGen.withNewDlo( bigtest5,  vars()["LIB"], "BIGTEST5_Mosfet2",  "layout")

# end
