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
# Mosfet1.py                                                           #
#                                                                      #
########################################################################
"""Module: Mosfet1

This module implements a RowMosfetTemplate class for creating row-stacking
MOS transistor PyCells.






RowMosfetTemplate provides the following capabilities:
    - (float  )  Transistor width  per finger
    - (float  )  Transistor length per finger

    - (integer)  Fingers per row


    - (integer)  Rows

    - (string )  Left  diffusion style, for abutment.
    - (string )  Right diffusion style, for abutment.

    - (float  )  Diffusion contact coverage
    - (string )  Design rule set

    - (float  )  Additional wire width connecting S/D contacts
    - (float  )  Additional diffusion contact to gate spacing
    - (float  )  Additional left  diffusion extension
    - (float  )  Additional right diffusion extension

    - (string )  Guard ring locations.

    - Electrical connectivity, i.e. nets, pins, terminals.



Class variables:
    - (tuple  )  contact,    layer & purpose name
    - (tuple  )  diffusion,  layer & purpose name
    - (tuple  )  metal1,     layer & purpose name
    - (tuple  )  metal2,     layer & purpose name
    - (tuple  )  poly,       layer & purpose name

    - (string )  tranType,   "pmos" or "nmos" transistor
    - (string )  oxide,      "thin" or "thick" oxide

    - (list   )  encLayers,  list of tuples of layer & purpose name
    - (list   )  envLayers,  list of tuples of layer & purpose name

    - (tuple  )  tapImplant, layer & purpose name

    - (Direction) diffContactJustify



Technology file requirements:
    - (minExtension  poly       diffusion)
    - (minExtension  diffusion  poly     )
    - (minClearance  contact    poly     )
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
__fileinfo__ = "$Id: //depot/deviceKits_4.2.5/baseKit/Mosfet1.py#1 $"
__author__   = "Lyndon C. Lim"

import traceback

from cni.dlo import (
    Bar,
    Box,
    ChoiceConstraint,
    CompoundComponent,
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
    RoutePath,
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
    Compare,
    ContactCenter,
    ContactEdge,
    ContactEdge1,
    ContactEdgeAbut1,
    ContactGate,
    DiffAbut,
    DiffEdgeAbut,
    DiffHalf,
    EnclosingRects,
    EnclosingRectsAbut,
    GuardRing,
    LayerDict,
    MosBody,
    MosBody1,
    MosDiffusion,
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
    isEven,
    isOdd,
    renameParams,
    reverseDict,
)

########################################################################

class RowMosfetTemplate( DloGen):
    """Defines a RowMosfetTemplate class.
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

    diffContactJustify = Direction.SOUTH

    paramNames = dict(
        wf             = "wf",
        lf             = "lf",
        fr             = "fr",
        rw             = "rw",

        diffLeftStyle  = "diffLeftStyle",
        diffRightStyle = "diffRightStyle",

        diffContactCov = "diffContactCov",
        ruleset        = "ruleset",

        cgSpacingAdd   = "cgSpacingAdd",
        wireWidthAdd   = "wireWidthAdd",
        leftDiffAdd    = "leftDiffAdd",
        rightDiffAdd   = "rightDiffAdd",

        guardRing      = "guardRing",
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

        wf = max(
            calculateDeviceParameter(
                specs.tech, cls.tranType, cls.oxide, "minWidth", [ layer.contact, layer.diffusion],
                ruleset=[ cls.default.get( "ruleset", "construction"), "default"],
                deviceContext=cls.transistorContext,
            ),
            cls.default.get( "wf", -1.0),
        )
        stepConstraint = StepConstraint( maskgrid, start=wf, resolution=resolution, action=FailAction.REJECT)
        
	#mySpecs( "wf", wf, constraint = stepConstraint)
	mySpecs("w",w)
	#Nerses
	
        # Minimum transistor length based on process requirement.
        # 2x grid requirement because PyCell uses path constructs.
        lf = max(
            calculateDeviceParameter(
                specs.tech, cls.tranType, cls.oxide, "minLength", [ layer.poly],
                ruleset=[ cls.default.get( "ruleset", "construction"), "default"],
                deviceContext=cls.transistorContext,
            ),
            cls.default.get( "lf", -1.0),
        )
        lf = gridX2.snap( lf)
        stepConstraint = StepConstraint( maskgridX2, start=lf, resolution=resolution, action=FailAction.REJECT)
        #mySpecs( "lf", lf, constraint = stepConstraint)
	mySpecs( "l",l)
	#Nerses
	
        # Rows and fingers are non-zero integers.
        stepConstraint = StepConstraint( 1, start=1, resolution=1, action=FailAction.REJECT)

        fr = max( 1, cls.default.get( "fr", 1))
        mySpecs( "fr", fr, constraint=stepConstraint)

        rw = max( 1, cls.default.get( "rw", 1))
        mySpecs( "rw", rw, constraint=stepConstraint)

        # Left & right S/D end styles.
        parameters = (
            ("diffLeftStyle",  "ContactEdge1" ),
            ("diffRightStyle", "ContactEdge1" ),
        )
        choiceConstraint = ChoiceConstraint(["ContactEdge1", "ContactEdgeAbut1", "DiffAbut", "DiffEdgeAbut", "DiffHalf", "MosDummy1"])
        for parameter in parameters:
            mySpecs( parameter[0], cls.default.get( parameter[0], parameter[1]), constraint=choiceConstraint)

        # Source/drain contact parameters
        diffContactCov = max( 0.0, min( 1.0, cls.default.get( "diffContactCov", 1.0)))
        floatConstraint = RangeConstraint(0.0, 1.0, FailAction.REJECT)
        mySpecs( "diffContactCov", diffContactCov, constraint=floatConstraint)

        # Intentional blank.
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #

        # Design ruleset.
        ruleset = cls.default.get( "ruleset", "construction")
        mySpecs( "ruleset",  ruleset, constraint=ChoiceConstraint([ "recommended", "construction"]))

        # Positive values only
        stepConstraint = StepConstraint( maskgrid, start=0.0, resolution=resolution, action=FailAction.REJECT)

        cgSpacingAdd = max( 0.0, cls.default.get( "cgSpacingAdd", 0.0))
        mySpecs( "cgSpacingAdd", cgSpacingAdd, constraint=stepConstraint)

        wireWidthAdd = max( 0.0, cls.default.get( "wireWidthAdd", 0.0))
        mySpecs( "wireWidthAdd", wireWidthAdd, constraint=stepConstraint)

        leftDiffAdd  = max( 0.0, cls.default.get( "leftDiffAdd", 0.0))
        mySpecs( "leftDiffAdd",  leftDiffAdd, constraint=stepConstraint)

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
	
	self.wf = self.grid.snap( self.wf)
        if self.wf < minW:
            raise ValueError, "wf (%f) is less than minimum (%f)." % ( self.wf, minW)

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
	self.lf = self.gridX2.snap( self.lf)
        if self.lf < minL:
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

        if "wireWidthAdd" in myParams:
            via1Layer = self.tech.getIntermediateLayers( self.layer.metal1, self.layer.metal2)[1][0]
            self.rules[ ("minExtension", self.layer.metal1, via1Layer, Direction.EAST_WEST)] = self.grid.snap( self.wireWidthAdd / 2.0)

    ####################################################################

    def genTopology( self):
        """Define topology (connectivity) for multi-device circuit PyCells.
            """
        dTerm = Term( "D", TermType.INPUT_OUTPUT)
        gTerm = Term( "G", TermType.INPUT       )
        sTerm = Term( "S", TermType.INPUT_OUTPUT)
        bTerm = Term( "B", TermType.INPUT_OUTPUT)

        # Create source/drain terminals on other rows.
        # Terminals are must-join, because rows are not connected.
        # Diffusion w/o contacts for abutment will also be must-join.
        #
        # Some terminals will be destroyed later, since row0 is
        # same as the base terminal.
        for i in range( self.rw):
            termName = "D_%d_0" % i
            termObj  = Term( termName, TermType.INPUT_OUTPUT)
            termObj.setMustJoin( dTerm)

            termName = "S_%d_0" % i
            termObj  = Term( termName, TermType.INPUT_OUTPUT)
            termObj.setMustJoin( sTerm)

        # Must-join terminals for diffusion abutment.
        diffLeftStyle  = eval( self.diffLeftStyle )
        diffRightStyle = eval( self.diffRightStyle)

        if issubclass( diffLeftStyle,  MosDiffusion) and ( self.fr > 1):
            for i in range( self.rw):
                termName = "D_%d_1" % i
                termObj  = Term( termName, TermType.INPUT_OUTPUT)
                termObj.setMustJoin( dTerm)

        if issubclass( diffRightStyle, MosDiffusion):
            if ( self.fr > 2) and isOdd( self.fr):
                for i in range( self.rw):
                    termName = "S_%d_1" % i
                    termObj  = Term( termName, TermType.INPUT_OUTPUT)
                    termObj.setMustJoin( sTerm)
            elif isEven( self.fr):
                for i in range( self.rw):
                    termName = "D_%d_2" % i
                    termObj  = Term( termName, TermType.INPUT_OUTPUT)
                    termObj.setMustJoin( sTerm)

    ####################################################################

    def sizeDevices( self):
        """Define device sizes within multi-device circuit PyCells.
            """
        pass

    ####################################################################

    def genLayout( self):
        """Main body of geometric construction code.  Build one row, based
        on minimum fingers=3 configuration.  This forces correct row height
        for pitch matching.  Remove unwanted transistor fingers as needed.
        Update leftmost and rightmost contacts for abutment.  Create
        succeeeding rows.  Add topmost contact, and connect all gates.
        Add implants.
            """
        with rulesmgr( self.tech, Ruleset, self.ruleset):
            with rulesmgr( self.tech, DeviceContext, self.transistorContext):
                # Create first row.
                self.createOneRow()

                # Create other rows.
                self.createOtherRows()

                # Add poly strips to close gaps.
                self.gapFillPoly()

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



        # Electrical connectivity.
        self.setPins()

    ####################################################################

    def createOneRow(
        self):
        """Create single row of transistors.
            """
        # Pitch matching rows require when fingers < 3, the minimum row
        #     is built with 3 fingers, then the extra fingers are removed.
        #     This ensures the S/D routing is created correctly for the
        #     row height.
        #
        # Use ContactEdge1 to ensure S/D routing is correct size when left
        #     or right S/D has no contact.
        nf = max( self.fr, 3)

        mosBody = MosBody1(
            diffLayer       = self.layer.diffusion,
            gateLayer       = self.layer.poly,
            metal1Layer     = self.layer.metal1,
            metal2Layer     = self.layer.metal2,
            contactLayer    = self.layer.contact,
            nf              = nf,
            gateWidth       = self.wf,
            gateLength      = self.lf,
            coverage        = self.diffContactCov,
            diffLeftStyle   = "ContactEdge1",
            diffRightStyle  = "ContactEdge1",
            envLayers       = self.envLayers,
            justify         = self.diffContactJustify,
            withGateContact = False,
            addRules        = self.rules,
            flip            = True,
        )
        mosBody.unlock()
        env = EnclosingRects( mosBody, self.envLayers, grid=self.grid)

        # Connect source, then drain contacts.
        pattern  = Pattern.even( nf + 1)
        diffConn = mosBody.addDiffConn(
            direction    = Direction.SOUTH,
            pattern      = pattern,
            env          = env,
        )
        mosBody.wireDiffConn( diffConn, Direction.SOUTH, pattern)

        pattern  = Pattern.odd( nf + 1)
        diffConn = mosBody.addDiffConn(
            direction    = Direction.NORTH,
            pattern      = pattern,
            env          = env,
        )
        mosBody.wireDiffConn( diffConn, Direction.NORTH, pattern)

        # Add gate contact, but leave connection until after
        # all rows are added.
        pattern = Pattern.all( nf)
        mosBody.addGateConn(
            direction = Direction.SOUTH,
            pattern   = pattern,
            env       = env,
        )

        mosBody.addGateConn(
            direction = Direction.NORTH,
            pattern   = pattern,
            env       = env,
        )



        # Remove unwanted transistor fingers, etc.
        self.prune()

        # Update leftmost and rightmost S/D diffusion for abutment.
        # Update routing.  Update gate contact.
        self.updateContacts()



        env.destroy()
        mosBody.lock()

    ####################################################################

    def createOtherRows(
        self):
        """Build and stack additional rows.
            """
        rowN = getComp( self, MosBody)

        # Create other rows of transistors.
        if self.rw > 1:
            conts = rowN.getCompsSorted( objType=ContactGate, sortFunction=Compare.cmpCenterYAscend)
            gcBot = conts[0]
            gcTop = conts[1]

            pitch = gcTop.getBBox().getBottom() - gcBot.getBBox().getBottom() 

            row0  = rowN.clone()
            conts = row0.getCompsSorted( objType=ContactGate, sortFunction=Compare.cmpCenterYAscend)
            gcTop = conts[1]
            row0.unlock()
            row0.remove( gcTop)
            gcTop.destroy()
            row0.lock()

            rowN.moveTowards( Direction.NORTH, pitch)

        if self.rw > 2:
            rows = row0.makeArray( 0, pitch, self.rw - 2, 1) 
            row0.moveTowards( Direction.NORTH, (self.rw - 2) * pitch)
            rowN.moveTowards( Direction.NORTH, (self.rw - 2) * pitch)
            rows.ungroup()

    ####################################################################

    def gapFillPoly(
        self):
        """Add poly strips to close gaps caused by source/drain contact
        routing.
            """
        polyFilter = ShapeFilter( self.layer.poly)
        box        = self.getBBox( polyFilter)
        topEdge    = box.getTop()
        botEdge    = box.getBottom()

        row = getComp( self, MosBody)

        for gate in row.getCompsSorted( objType=(MosGate, MosDummy)):
            box = gate.getBBox( polyFilter)
            box.setTop( topEdge)
            box.setBottom( botEdge)
            Rect( self.layer.poly, box)

    ####################################################################

    def prune(
        self):
        """Remove extra transistor fingers, contacts, and routing which
        were created as part of building pitch-matched rows.
            """
        polyFilter = ShapeFilter( self.layer.poly)
        mosBody    = getComp( self, MosBody)

        # Remove extra transistors, contacts, routing.
        comps = mosBody.getCompsSorted( objType=( MosGate, ContactCenter, ContactEdge))
        conns = mosBody.getCompsSorted( objType=ViaX, sortFunction=Compare.cmpCenterYAscend)
        if self.fr < 3:
            for i in range( 6, 2 * self.fr, -1):
                mosBody.remove( comps[ i])
                comps[ i].destroy()
                del comps[i]

            # Remove upper routing.
            mosBody.unwire( conns[1], self.layer.metal1)
            mosBody.remove( conns[1])
            conns[1].destroy()

        # Remove lower routing.
        if self.fr < 2:
            mosBody.unwire( conns[0], self.layer.metal1)
            mosBody.remove( conns[0])
            conns[0].destroy()

        # Update params after pruning.  Otherwise, later decision, such
        # as calculation of MosDiffusion for abutment is incorrect.
        mosBody.params.nf = self.fr

    ####################################################################

    def routeAdjust(
        self,
        conn,
        comp,
        layer):
        """Extend source/drain routing to diffusion edge when abutment
        is enabled.
            """
        filter  = ShapeFilter( layer)
        connBox = conn.getBBox()

        if isinstance( comp, MosDummy):
            comp = comp.getComp( objType=ContactCenter)

        if comp.isAbutable:
            compBox = comp.getBBox()
        else:
            compBox = comp.getBBox( filter)

        if connBox.getRangeX().overlaps( compBox.getRangeX()):
            if compBox.getLeft() < connBox.getCenterX():
                connBox.setLeft( compBox.getLeft())
            else:
                connBox.setRight( compBox.getRight())

            conn.getLeafComps()[0].setBBox( connBox)

    ####################################################################

    def setPins(
        self):
        """Model electrical connectivity.
        Gate - Multiple pins are resistively/weakly connected.
        Source/drain - Multiple pins which must be externally connected.
        (must-join).
            """
        comps = self.getComps()

        guardRing = getComp( self, GuardRing)
        if guardRing:
            guardRing.setPin(
                pinName  = "B",
                termName = "B",
            )



        # Define gate pins for each MosBody1.
        i = 0
        gateConts = [
            g
            for m in comps if isinstance( m, MosBody)
            for g in m.getCompsSorted( objType=ContactGate)
        ]
        for i in range( len( gateConts)):
            # Resistive pin connection.
            gateConts[ i].setPin(
                pinName  = "G_%d" % i,
                termName = "G",
                layer    = self.layer.metal1
            )



        # Define source/drain pins in each row.
        names  = ( "D", "S")
        rows   = [ c for c in comps if isinstance( c, MosBody)]
        rows.sort( Compare.cmpCenterYAscend)



        for i in range( self.rw):
            # Routing rectangle.
            conns = rows[ i].getCompsSorted( objType=ViaX, sortFunction=Compare.cmpCenterYAscend)
            for j in range( len( conns)):
                termName = "%s_%d_0" % ( names[ j], i)
                conns[ j].setPin( termName, termName)

            contacts = rows[ i].getCompsSorted( objType=( ContactCenter, ContactEdge, MosDiffusion, MosDummy))

            # If leftmost S/D diffusion has no contact.
            j = 0
            if isinstance( contacts[0], MosDiffusion) and ( self.fr > 1):
                termName = "D_%d_1" % i
                contacts[0].setPin( termName, termName, layer=[ self.layer.diffusion, self.layer.metal1])
                del contacts[0]
                j += 1

            # If rightmost S/D diffusion has no contact.
            if isinstance( contacts[-1], MosDiffusion):
                if ( self.fr > 2) and isOdd( self.fr):
                    termName = "S_%d_1" % i
                    contacts[-1].setPin( termName, termName, layer=[ self.layer.diffusion, self.layer.metal1])
                    del contacts[-1]
                elif isEven( self.fr):
                    termName = "D_%d_2" % i
                    contacts[-1].setPin( termName, termName, layer=[ self.layer.diffusion, self.layer.metal1])
                    del contacts[-1]

            # Remaining S/D diffusions.
            for contact in contacts:
                termName = "%s_%d_0" % ( names[ j % 2], i)
                contact.setPin( termName, termName, layer=[ self.layer.diffusion, self.layer.metal1])
                j += 1



        # Remove redundant terminals for row0, and reassign
        # their pins to base terminals.
        rename = dict(
            D_0_0 = "D",
            S_0_0 = "S",
        )

        for old in rename:
            oldPin  = Pin.find( old)
            newPin  = Pin.find( rename[ old])

            if oldPin and not newPin:
                oldPin.setName( rename[ old])

                term = Term.find( rename[ old])
                oldPin.setTerm( term)

                term = Term.find( old)
                term.destroy()

                net  = Net.find( old)
                net.destroy()

    ####################################################################

    def updateContacts(
        self):
        """Replace left/right source/drain diffusion contacts which were
        built for pitch matching requirements with user requested style.
            """
        diffFilter = ShapeFilter( self.layer.diffusion)
        polyFilter = ShapeFilter( self.layer.poly     )



        # Substitute requested left and right S/D diffusion.
        mosBody = getComp( self, MosBody)
        mosBody.changeEndStyle( self.diffLeftStyle, self.diffRightStyle)

        # Correct gate contact size.
        for conn in mosBody.getCompsSorted( objType=ContactGate):
            newConn = mosBody.addGateConn( Direction.SOUTH, Pattern.all( self.fr))
            mosBody.remove( conn)
            newConn.alignEdge( Direction.NORTH, conn, filter=polyFilter)
            conn.destroy()




        # Lopsided abutment patch.  (2007-04-12, lyndon, Bugzilla #1130)
        # This temporary patch added to compensate for Helix, which cannot
        # correctly abut transistors when the poly contact extends beyond
        # the pin abutment edge.
        exempt = BorrowGrouping( components=mosBody.getCompsSorted( objType=ViaX))
        mBox   = mosBody.getBBox()
        exempt.ungroup()

        mL     = mBox.getLeft()
        mR     = mBox.getRight()
        comps  = mosBody.getCompsSorted( objType=( ContactEdge, MosDiffusion, MosDummy))

        comp = comps[0]
        if comp.isAbutable:
            rect = comp.getComp( Rect)
            box  = rect.getBBox()
            if box.getLeft() > mL:
                box.setLeft( mL)
                rect.setBBox( box)

        comp = comps[-1]
        if comp.isAbutable:
            rect = comp.getComp( Rect)
            box  = comp.getBBox()
            if box.getRight() < mR:
                box.setRight( mR)
                rect.setBBox( box)
        # End patch



        # Adjust routing for abutment.
        comps = mosBody.getCompsSorted( objType=( ContactEdge, MosDiffusion, MosDummy))
        conns = mosBody.getCompsSorted( objType=ViaX, sortFunction=Compare.cmpLeftAscend)

        for i in range( len( conns)):
            self.routeAdjust( conns[i], comps[0],  self.layer.metal1)
            self.routeAdjust( conns[i], comps[-1], self.layer.metal1)

########################################################################

class Pmos( RowMosfetTemplate):
    """Pmos class implements row-stacking PMOS transistors.
        """
    tranType   = "pmos"
    oxide      = "thin"

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

class Nmos( RowMosfetTemplate):
    """Nmos class implements row-stacking PMOS transistors.
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

########################################################################

class PmosH( RowMosfetTemplate):
    """PmosH class implements row-stacking high voltage PMOS transistors.
        """
    tranType   = "pmos"
    oxide      = "thick"

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
        od2          = ( "DIFF_18",     "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################
class PmosHvt( RowMosfetTemplate):
    """PmosH class implements row-stacking high voltage PMOS transistors.
        """
    tranType   = "pmos"
    oxide      = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        metal2       = ( "M2",  "drawing"),
        poly         = ( "PO",  "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "HVTIMP",  "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################
class PmosLvt( RowMosfetTemplate):
    """PmosH class implements row-stacking high voltage PMOS transistors.
        """
    tranType   = "nmos"
    oxide      = "thin"

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
        od2          = ( "LVTIMP",     "drawing"),
    )

    encLayers  = [ "implant", "well", "od2"]
    envLayers  = [ "implant", "well", "od2"]

########################################################################
class NmosH( RowMosfetTemplate):
    """NmosH class implements row-stacking high voltage NMOS transistors.
        """
    tranType   = "nmos"
    oxide      = "thick"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        metal2       = ( "M2",  "drawing"),
        poly         = ( "PO",   "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
        od2          = ( "DIFF_18",     "drawing"),
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
        wf               = "wf",
        lf               = "lf",
        fr               = "fr",
        rw               = "rw",

        diffLeftStyle    = "diffLeftStyle",
        diffRightStyle   = "diffRightStyle",

        diffContactCov   = "diffContactCov",
        ruleset          = "ruleset",

        cgSpacingAdd     = "cgSpacingAdd",
        wireWidthAdd     = "wireWidthAdd",
        leftDiffAdd      = "leftDiffAdd",
        rightDiffAdd     = "rightDiffAdd",

        guardRing        = "guardRing",
    )

    def makeInstances(
        dlogen,
        masters,
        widths,
        lengths,
        nf,
        rows,
        diffLeftStyles,
        diffRightStyles,
        coverages,
        cgSpacingAdds,
        wireWidthAdds,
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

            listWidths  = [ params["wf"]]
            listWidths.extend( widths)

            listLengths = [ params["lf"]]
            listLengths.extend( lengths)
            inst.destroy()

            for rw in rows:
                for diffContactCov in coverages:
                    for wf in listWidths:
                        for lf in listLengths:
                            for fr in nf:
                                for diffLeftStyle in diffLeftStyles:
                                    for diffRightStyle in diffRightStyles:
                                        for cgSpacingAdd in cgSpacingAdds:
                                            for wireWidthAdd in wireWidthAdds:
                                                for leftDiffAdd in leftDiffAdds:
                                                    for rightDiffAdd in rightDiffAdds:
                                                        for guardRing in guardRings:
                                                            params = ParamArray(
                                                                wf = wf,
                                                                lf = lf,
                                                                fr = fr,
                                                                rw = rw,

                                                                diffLeftStyle  = diffLeftStyle,
                                                                diffRightStyle = diffRightStyle,
                                                                diffContactCov = diffContactCov,

                                                                cgSpacingAdd   = cgSpacingAdd,
                                                                wireWidthAdd   = wireWidthAdd,
                                                                leftDiffAdd    = leftDiffAdd,
                                                                rightDiffAdd   = rightDiffAdd,
                                                                guardRing      = guardRing,
                                                            )
                                                            paramSets.append( [ master, params])

        createInstances( paramSets, paramNames, minColWidth=30, minRowHeight=30)



    def tinytest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters         = ( "Pmos1", "Nmos1", ),
            widths          = ( 1.3, ),
            lengths         = ( 0.5, ),
            nf              = ( 1, 2, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "ContactEdge1", ),
            diffRightStyles = ( "ContactEdge1", ),
            coverages       = ( 1.0, ),
            cgSpacingAdds   = ( 0.0, ),
            wireWidthAdds   = ( 0.0, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "", ),
        )
        self.save()



    def smalltest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters         = ( "Pmos1", ),
            widths          = ( 1.3, ),
            lengths         = ( 0.5, ),
            nf              = ( 1, 2, 3, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "ContactEdgeAbut1", "DiffAbut", "DiffEdgeAbut", "DiffHalf", "MosDummy1", ),
            diffRightStyles = ( "ContactEdge1", "ContactEdgeAbut1", "DiffAbut", "DiffEdgeAbut", "DiffHalf", "MosDummy1", ),
            coverages       = ( 1.0, ),
            cgSpacingAdds   = ( 0.0, ),
            wireWidthAdds   = ( 0.0, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "top,bottom", "", ),
        )
        self.save()



    def bigtest1( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "Pmos1", ),
            widths          = ( 1.5, ),
            lengths         = ( 0.3, ),
            nf              = ( 1, 2, 3, ),
            rows            = ( 1, 2, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles = ( "ContactEdge1", "MosDummy1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.0, ),
            wireWidthAdds   = ( 0.0, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "top,bottom,left,right", "", ),
        )
        self.save()



    def bigtest2( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "Nmos1", ),
            widths          = ( 2.0, ),
            lengths         = ( 0.5, ),
            nf              = ( 1, 2, 3, ),
            rows            = ( 1, 2, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles = ( "ContactEdge1", "MosDummy1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.2, ),
            wireWidthAdds   = ( 0.2, ),
            leftDiffAdds    = ( 0.2, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "top,left", "", ),
        )
        self.save()



    def bigtest3( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "PmosH1", ),
            widths          = ( 2.5, ),
            lengths         = ( 0.8, ),
            nf              = ( 1, 2, 3, ),
            rows            = ( 1, 2, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles = ( "ContactEdge1", "MosDummy1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.1, ),
            wireWidthAdds   = ( 0.1, ),
            leftDiffAdds    = ( 0.1, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "top,bottom,", "", ),
        )
        self.save()



    def bigtest4( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "NmosH1", ),
            widths          = ( 3.0, ),
            lengths         = ( 1.0, ),
            nf              = ( 1, 2, 3, ),
            rows            = ( 1, 2, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles = ( "ContactEdge1", "MosDummy1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.0, ),
            wireWidthAdds   = ( 0.0, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "left,right", "", ),
        )
        self.save()



    def bigtest5( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "Pmos1", "Nmos1", ),
            widths          = ( 3.0, ),
            lengths         = ( 1.0, ),
            nf              = ( 1, 2, ),
            rows            = ( 1, 2, ),
            diffLeftStyles  = ( "ContactEdgeAbut1", "DiffAbut", "DiffEdgeAbut", "DiffHalf", ),
            diffRightStyles = ( "ContactEdgeAbut1", "DiffAbut", "DiffEdgeAbut", "DiffHalf", ),
            coverages       = ( 1.0, ),
            cgSpacingAdds   = ( 0.0, ),
            wireWidthAdds   = ( 0.0, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "",  ),
        )
        self.save()



    # TEST is defined externally from this file.
    # For building the test cases, invoke like this:
    # cnpy -c "TEST='SMALL';LIB='MyPyCellLib_cni180';execfile('Mosfet1.py')"
    if "TEST" in vars():
        if   vars()["TEST"] == "SMALL":
            DloGen.withNewDlo( tinytest,  vars()["LIB"], "TINYTEST_Mosfet1",  "layout")
            DloGen.withNewDlo( smalltest, vars()["LIB"], "SMALLTEST_Mosfet1", "layout")
        elif vars()["TEST"] == "BIG":
            DloGen.withNewDlo( bigtest1,  vars()["LIB"], "BIGTEST1_Mosfet1",  "layout")
            DloGen.withNewDlo( bigtest2,  vars()["LIB"], "BIGTEST2_Mosfet1",  "layout")
            DloGen.withNewDlo( bigtest3,  vars()["LIB"], "BIGTEST3_Mosfet1",  "layout")
            DloGen.withNewDlo( bigtest4,  vars()["LIB"], "BIGTEST4_Mosfet1",  "layout")
            DloGen.withNewDlo( bigtest5,  vars()["LIB"], "BIGTEST5_Mosfet1",  "layout")

# end
