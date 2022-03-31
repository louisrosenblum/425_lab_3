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
#
# DiffPair.py
#
########################################################################
"""Module: DiffPair

This module implements a DiffPairTemplate class for creating MOS
transistor differential pair PyCells.

A transistor is defined as a single gate.

A device is defined as the sum of all connected gates over each
row, over all rows.

DiffPairTemplate provides the following capabilities:
    - (float  )  Transistor width  per finger
    - (float  )  Transistor length per finger

    - (integer)  Fingers per row, per device
                 Total fingers per row is 2x this value,
                 given this is a differential pair.
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
    - (list   )  envLayers,  list of tuples of layer & pur
    pose name

    - (tuple  )  tapImplant, layer & purpose name



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
__fileinfo__ = "$Id: //depot/deviceKits_4.2.5/baseKit/DiffPair.py#1 $"
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
    ContactCenter,
    ContactEdge,
    ContactGate,
    DiffAbut,
    DiffEdge,
    EnclosingRects,
    EnclosingRectsAbut,
    EnclosingRectsBBox,
    GuardRing,
    LayerDict,
    MosBody,
    MosBody1,
    MosDummy,
    MosDummy1,
    MosStack2,
    Pattern,
    RulesDict,
    ViaX,
)

from cni.integ.common import (
    createInstances,
    renameParams,
    reverseDict,
    Compare,
)

########################################################################

class DiffPairTemplate( DloGen):
    """Defines a DiffPairTemplate class.
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
        mySpecs( "wf", wf, constraint = stepConstraint)

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
        mySpecs( "lf", lf, constraint = stepConstraint)

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
        choiceConstraint = ChoiceConstraint(["ContactEdge1", "MosDummy1"])
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

        for key in params:
            setattr( self, key, params[ key])

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
        self.wf = self.grid.snap( self.wf)
        if self.wf < minW:
            raise ValueError, "wf (%f) is less than minimum (%f)." % ( self.wf, minW)

        minL    = calculateDeviceParameter(
            self.tech, self.tranType, self.oxide, "minLength", [ self.layer.poly],
            ruleset=self.ruleset,
            deviceContext=self.transistorContext,
        )
        minL    = self.gridX2.snap( minL)
        self.lf = self.gridX2.snap( self.lf)
        if self.lf < minL:
            raise ValueError, "lf (%f) is less than minimum (%f)." % ( self.lf, minL)

        self.cPattern  = Pattern.diffPairContact( self.fr)

        # RuleDict for parameter to rule mapping.
        self.rules = RulesDict()
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.contact, Direction.EAST,     )] = self.rightDiffAdd
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.contact, Direction.WEST,     )] = self.leftDiffAdd
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.poly,    Direction.EAST,     )] = self.rightDiffAdd
        self.rules[ ( "minExtension", self.layer.diffusion, self.layer.poly,    Direction.WEST,     )] = self.leftDiffAdd
        self.rules[ ( "minClearance", self.layer.contact,   self.layer.poly,    Direction.EAST_WEST,)] = self.cgSpacingAdd

        via1Layer = self.tech.getIntermediateLayers( self.layer.metal1, self.layer.metal2)[1][0]
        self.rules[ ("minExtension", self.layer.metal1, via1Layer, Direction.EAST_WEST)] = self.grid.snap( self.wireWidthAdd / 2.0)

    ####################################################################

    def genTopology( self):
        """Define topology (connectivity) for multi-device circuit PyCells.
            """
        # Base terminals, on row 0.
        d0 = Term( "D0", TermType.INPUT_OUTPUT)
        g0 = Term( "G0", TermType.INPUT       )

        d1 = Term( "D1", TermType.INPUT_OUTPUT)
        g1 = Term( "G1", TermType.INPUT       )

        s  = Term( "S",  TermType.INPUT_OUTPUT)
        b  = Term( "B",  TermType.INPUT_OUTPUT)

        termObjs = dict(
            D0 = ( d0, d0.getTermType()),
            G0 = ( g0, g0.getTermType()),
            D1 = ( d1, d1.getTermType()),
            G1 = ( g1, g1.getTermType()),
             S = (  s,  s.getTermType()),
        )

        # Create terminals on other rows and fingers.
        # Terminals are must-join, because rows are not connected
        #
        # Some terminals will be destroyed later, since row0/finger0
        # is same as the base terminal.
        for row in range( 0, self.rw):
            # Terminals are must-join between rows.
            for term in ( "G0", "G1", "S"):
                finger   = 0
                termName = "%s_%d_%d" % ( term, row, finger)
                termObj  = Term( termName, termObjs[ term][1])
                termObj.setMustJoin( termObjs[ term][0])

            # Terminals are must-join between rows and fingers.
            for term in ( "D0", "D1"):
                for finger in range( ( self.fr + 1) / 2):
                    termName = "%s_%d_%d" % (term, row, finger)
                    termObj  = Term( termName, termObjs[ term][1])
                    termObj.setMustJoin( termObjs[ term][0])

    ####################################################################

    def sizeDevices( self):
        """Define device sizes within multi-device circuit PyCells.
            """
        pass

    ####################################################################

    def genLayout( self):
        """Main body of geometric construction code.  Build rows, then
        add implants, etc.
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
        mosBody = MosBody1(
            diffLayer      = self.layer.diffusion,
            gateLayer      = self.layer.poly,
            metal1Layer    = self.layer.metal1,
            metal2Layer    = self.layer.metal2,
            contactLayer   = self.layer.contact,
            fingers        = self.fr * 2,
            gateWidth      = self.wf,
            gateLength     = self.lf,
            coverage       = self.diffContactCov,
            diffLeftStyle  = "ContactEdge1",
            diffRightStyle = "ContactEdge1",
            envLayers      = self.envLayers,
            justify        = Direction.NORTH_SOUTH,
            addRules       = self.rules,
        )
        mosBody.unlock()
        env = EnclosingRects( mosBody, self.envLayers, grid=self.grid)

        # Define order of routing device terminal S.
        if self.fr % 2 == 0:
            direction = ( Direction.NORTH, Direction.SOUTH)
        else:
            direction = ( Direction.SOUTH, Direction.NORTH)

        # Add connector for device terminal S.
        diffConn = []
        for i in range( len( self.cPattern.c2) - 1):
            diffConn.append(
                mosBody.addDiffConn(
                    direction    = direction[ i % 2],
                    pattern      = self.cPattern.c2[ i: i+2],
                    env          = env
                )
            )

        # Add connector for device terminals G0, G1.
        gPattern = Pattern.diffPairGate( self.fr)
        gc0 = mosBody.addGateConn(
            direction   = Direction.SOUTH,
            pattern     = gPattern.g0,
            withContact = False,
            pitchMatch  = True,
            env         = env
        )
        gc1 = mosBody.addGateConn(
            direction   = Direction.NORTH,
            pattern     = gPattern.g1,
            withContact = False,
            pitchMatch  = True,
            env         = env
        )

        # Wire transistor gates to connector.
        mosBody.wireGateConn( gc0, gPattern.g0)
        mosBody.wireGateConn( gc1, gPattern.g1)

        # Wire diffusion contacts to connector.
        for i in range( len( self.cPattern.c2) - 1):
            mosBody.wireDiffConn( diffConn[i], direction[ i % 2], self.cPattern.c2[ i: i+2])

        mosBody.changeEndStyle( self.diffLeftStyle, self.diffRightStyle)

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
            row0 = rowN.clone()
            rowN.place( Direction.NORTH, row0, 0)

            rows = BorrowGrouping( components=[ row0, rowN])
            env  = EnclosingRectsBBox( rows, self.envLayers)

            rowN.ggPlace( Direction.NORTH, row0, env=env, grid=self.grid)

            env.destroy()
            rows.ungroup()

            spacing = rowN.getBBox().getBottom() - row0.getBBox().getTop()
            pitch   = rowN.getBBox().getBottom() - row0.getBBox().getBottom()

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

        for gate in row.getCompsSorted( objType=( MosDummy)):
            box = gate.getBBox( polyFilter)
            box.setTop( topEdge)
            box.setBottom( botEdge)
            Rect( self.layer.poly, box)

    ####################################################################

    def setPinsOneRow(
        self,
        rowObj,
        row):
        """Model electrical connectivity for one row.
        Gate   - single pin per device per row.
        Source - single pin per device per row.
        Drains - multiple pins per device must be externally connected.
            """
        diffContacts = rowObj.getCompsSorted( objType=( ContactEdge, ContactCenter, MosDummy))

        finger = 0
        suffix = "_%d_%d" % ( row, finger)

        # Gate connections, 1 per device per row.
        gateContacts = rowObj.getCompsSorted( objType=ContactGate, sortFunction=Compare.cmpCenterYAscend)

        termName = "G0%s" % suffix
        gateContacts[0].setPin( termName, termName)

        termName = "G1%s" % suffix
        gateContacts[1].setPin( termName, termName)



        # Source connections, 1 per row.
        termName = "S%s" % suffix

        for finger in range( len( self.cPattern.c2)):
            diffContacts[ self.cPattern.c2[ finger]].setPin( termName, termName, layer=[ self.layer.diffusion, self.layer.metal1])

        wires = rowObj.getCompsSorted( objType=ViaX)
        for wire in wires:
            wire.setPin( termName, termName)





        # Diffusion connections, 1 per 2 fingers, per device, per row.
        for finger in range( len( self.cPattern.c0)):
            termName = "D0_%d_%d" % ( row, finger)
            diffContacts[ self.cPattern.c0[ finger]].setPin( termName, termName, layer=[ self.layer.diffusion, self.layer.metal1])

        for finger in range( len( self.cPattern.c1)):
            termName = "D1_%d_%d" % ( row, finger)
            diffContacts[ self.cPattern.c1[ finger]].setPin( termName, termName, layer=[ self.layer.diffusion, self.layer.metal1])

    ####################################################################

    def setPins(
        self):
        """Model electrical connectivity.
        Gate, source, and drain contain multiple pins which must be externally
        connected between rows.
            """
        guardRing = getComp( self, GuardRing)
        if guardRing:
            guardRing.setPin(
                pinName  = "B",
                termName = "B",
            )



        rows = getCompsSorted( self, objType=MosBody, sortFunction=Compare.cmpCenterYAscend)

        for i in range( len( rows)):
            self.setPinsOneRow( rows[ i], i)

        # Remove redundant terminals for row0/finger0, and reassign
        # pins to base terminals.
        rename = dict(
            G0_0_0 = "G0",
            G1_0_0 = "G1",
            D0_0_0 = "D0",
            D1_0_0 = "D1",
            S_0_0  = "S",
        )

        for old in rename:
            new     = rename[ old]
            oldPin  = Pin.find( old)
            newPin  = Pin.find( new)

            if oldPin and not newPin:
                oldPin.setName( new)
                oldPin.setTerm( Term.find( new))

                term = Term.find( old)
                if term:
                    term.destroy()

                net = Net.find( old)
                if net:
                    net.destroy()

########################################################################

class PmosDiffPair( DiffPairTemplate):
    """PmosDiffPair class implements a row-stacking PMOS differential pair.
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

class NmosDiffPair( DiffPairTemplate):
    """NmosDiffPair class implements a row-stacking NMOS differential pair.
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

class PmosHDiffPair( DiffPairTemplate):
    """PmosHDiffPair class implements a row-stacking high voltage PMOS
    differential pair.
        """
    tranType  = "pmos"
    oxide     = "thick"

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

class NmosHDiffPair( DiffPairTemplate):
    """NmosHDiffPair class implements a row-stacking high voltage NMOS
    differential pair.
        """
    tranType  = "nmos"
    oxide     = "thick"

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
        fingers,
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
                            for fr in fingers:
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
            masters         = ( "PmosDiffPair", "NmosHDiffPair", ),
            widths          = ( 1.3, ),
            lengths         = ( 0.6, ),
            fingers         = ( 1, 3, ),
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
            masters         = ( "PmosDiffPair", "NmosHDiffPair", ),
            widths          = ( 1.3, ),
            lengths         = ( 0.6, ),
            fingers         = ( 1, 2, 3, 4, 5, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles = ( "ContactEdge1", "MosDummy1", ),
            coverages       = ( 1.0, ),
            cgSpacingAdds   = ( 0.0, ),
            wireWidthAdds   = ( 0.0, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, ),
            guardRings      = ( "top,bottom,left,right", "", ),
        )
        self.save()



    def bigtest1( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "PmosDiffPair", ),
            widths          = ( 0.7, 1.3, ),
            lengths         = ( 0.3, ),
            fingers         = ( 1, 2, 3, 4, 5, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "ContactEdge1", ),
            diffRightStyles = ( "ContactEdge1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.0, 0.2, ),
            wireWidthAdds   = ( 0.0, 0.2, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, 0.2, ),
            guardRings      = ( "top,bottom,left,right", "", ),
        )
        self.save()



    def bigtest2( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "NmosDiffPair", ),
            widths          = ( 0.8, 2.5, ),
            lengths         = ( 0.5, ),
            fingers         = ( 1, 2, 3, 4, 5, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "MosDummy1", ),
            diffRightStyles = ( "ContactEdge1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.0, 0.2, ),
            wireWidthAdds   = ( 0.0, 0.2, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, 0.2, ),
            guardRings      = ( "top,left", "", ),
        )
        self.save()



    def bigtest3( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "PmosHDiffPair", ),
            widths          = ( 0.6, 1.7, ),
            lengths         = ( 0.8, ),
            fingers         = ( 1, 2, 3, 4, 5, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "ContactEdge1", ),
            diffRightStyles = ( "ContactEdge1", "MosDummy1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.0, 0.2, ),
            wireWidthAdds   = ( 0.0, 0.2, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, 0.2, ),
            guardRings      = ( "top,bottom,", "", ),
        )
        self.save()



    def bigtest4( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters         = ( "NmosHDiffPair", ),
            widths          = ( 1.0, 3.0, ),
            lengths         = ( 1.0, ),
            fingers         = ( 1, 2, 3, 4, 5, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "MosDummy1", ),
            diffRightStyles = ( "MosDummy1", ),
            coverages       = ( 0.5, 1.0, ),
            cgSpacingAdds   = ( 0.0, 0.2, ),
            wireWidthAdds   = ( 0.0, 0.2, ),
            leftDiffAdds    = ( 0.0, ),
            rightDiffAdds   = ( 0.0, 0.2, ),
            guardRings      = ( "left,right", "", ),
        )
        self.save()



    # TEST is defined externally from this file.
    # For building the test cases, invoke like this:
    # cnpy -c "TEST='SMALL';LIB='MyPyCellLib_cni180';execfile('DiffPair.py')"
    if "TEST" in vars():
        if   vars()["TEST"]   == "SMALL":
            DloGen.withNewDlo( tinytest,  vars()["LIB"], "TINYTEST_DiffPair",  "layout")
            DloGen.withNewDlo( smalltest, vars()["LIB"], "SMALLTEST_DiffPair", "layout")
        elif vars()["TEST"]   == "BIG":
            DloGen.withNewDlo( bigtest1,  vars()["LIB"], "BIGTEST1_DiffPair",  "layout")
            DloGen.withNewDlo( bigtest2,  vars()["LIB"], "BIGTEST2_DiffPair",  "layout")
            DloGen.withNewDlo( bigtest3,  vars()["LIB"], "BIGTEST3_DiffPair",  "layout")
            DloGen.withNewDlo( bigtest4,  vars()["LIB"], "BIGTEST4_DiffPair",  "layout")

# end
