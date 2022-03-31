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
# DiffPair1.py
#
########################################################################
"""Module: DiffPair1

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


    - (float  )  Additional diffusion contact to gate spacing
    - (float  )  Additional left  diffusion extension
    - (float  )  Additional right diffusion extension

    - (string )  Guard ring locations.

    - Electrical connectivity, i.e. nets, pins, terminals.



Class variables:
    - (tuple  )  contact,   layer & purpose name
    - (tuple  )  diffusion, layer & purpose name
    - (tuple  )  metal1,    layer & purpose name
    - (tuple  )  metal2,    layer & purpose name
    - (tuple  )  poly,      layer & purpose name

    - (string )  tranType,  "pmos" or "nmos" transistor
    - (string )  oxide,     "thin" or "thick" oxide

    - (list   )  encLayers, list of tuples of layer & purpose name
    - (list   )  envLayers, list of tuples of layer & purpose name

    - (tuple  )  tapImplant, layer & purpose name

    - (Direction) diffContactJustify



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
__fileinfo__ = "$Id: //depot/deviceKits_4.2.5/baseKit/DiffPair1.py#1 $"
__author__   = "Lyndon C. Lim"

import traceback

from cni.dlo import (
    Bar,
    Box,
    ChoiceConstraint,
    CompoundComponent,
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
    getCompsSorted,
    getComp,
    orderedRuleset,
    rulesmgr,
    ContactCenter,
    ContactEdge,
    ContactGate,
    ContactGate1,
    DiffAbut,
    DiffEdge,
    GuardRing,
    LayerDict,
    MosBody,
    MosBody1,
    MosGate,
    MosStack2,
    Pattern,
    RouteRect,
    ViaX,
)

from cni.integ.common import (
    createInstances,
    isEven,
    renameParams,
    reverseDict,
    Compare,
)

from Mosfet1 import (
    RowMosfetTemplate,
)

########################################################################

class DiffPairTemplate( RowMosfetTemplate):
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

    default    = dict()

    ####################################################################

    @classmethod
    def defineParamSpecs( cls, specs):
        """Define the PyCell parameters.  The order of invocation of
        specs() becomes the order on the form.

        Arguments:
        specs - (ParamSpecArray)  PyCell parameters
            """
        mySpecs = ParamSpecArray()
        myNames = reverseDict( super( DiffPairTemplate, cls).paramNames)

        super( DiffPairTemplate, cls).defineParamSpecs( mySpecs)

        for key in mySpecs:
            if myNames[ key] not in ( "diffLeftStyle", "diffRightStyle"):
                specs[ key] = mySpecs[ key]

        # Left & right S/D end styles.
        mySpecs    = ParamSpecArray()
        parameters = (
            ("diffLeftStyle",  "ContactEdge1" ),
            ("diffRightStyle", "ContactEdge1" ),
        )
        choiceConstraint = ChoiceConstraint(["ContactEdge1", "MosDummy1"])
        for parameter in parameters:
            mySpecs( parameter[0], cls.default.get( parameter[0], parameter[1]), constraint=choiceConstraint)

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    ####################################################################

    def setupParams( self, params):
        """Define the PyCell parameters.  The order of invocation of
        specs() becomes the order on the form.

        Arguments:
        specs - (ParamSpecArray)  PyCell parameters
            """
        super( DiffPairTemplate, self).setupParams( params)

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

    def createOneRow(
        self):
        """Create single row of transistors.
            """
        # Create template for the base row.
        fingers  = self.fr
        self.fr *= 2
        super( DiffPairTemplate, self).createOneRow()
        self.fr  = fingers



        #
        # Change the base row to a differential pair.
        #
        mosBody = getComp( self, MosBody)
        mosBody.unlock()

        # Center justify diffusion contacts.
        mosBody.justifyDiffContacts(
            direction = Direction.NORTH_SOUTH,
        )

        # Rewire gate configuration.
        pattern  = Pattern.diffPairGate( self.fr)
        contacts = mosBody.getCompsSorted( objType=ContactGate, sortFunction=Compare.cmpCenterYAscend)
        self.rewireGates( mosBody, contacts[0], pattern.g0)
        self.rewireGates( mosBody, contacts[1], pattern.g1)



        # Remove unused geometries.
        for contact in contacts:
            contact.destroy()

        for comp in mosBody.getCompsSorted( objType=( RouteRect, ViaX)):
            comp.destroy()

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
            gcTop = conts[-1]

            pitch = gcTop.getBBox().getBottom() - gcBot.getBBox().getBottom() 

            row0  = rowN.clone()
            conts = row0.getCompsSorted( objType=ContactGate, sortFunction=Compare.cmpCenterYAscend)
            gcTop = conts[1]

            rowN.moveTowards( Direction.NORTH, pitch)

        if self.rw > 2:
            nrows = row0.makeArray( 0, pitch, self.rw - 2, 1) 
            row0.moveTowards( Direction.NORTH, (self.rw - 2) * pitch)
            rowN.moveTowards( Direction.NORTH, (self.rw - 2) * pitch)
            nrows.ungroup()



        # Flip alternate rows.
        rows = getCompsSorted( self, objType=MosBody, sortFunction=Compare.cmpCenterYAscend)
        for i in range( len(rows)):
            if isEven( i):
                box = rows[i].getBBox()
                pt  = box.lowerLeft()
                rows[i].mirrorX( yCoord=pt.y)
                rows[i].alignEdgeToPoint( Direction.SOUTH, pt)

    ####################################################################

    def rewireGates(
        self,
        mosBody,
        contact,
        pattern):
        """Replace left/right source/drain diffusion contacts which were
        built for pitch matching requirements with user requested style.
            """
        polyFilter = ShapeFilter( self.layer.poly  )
        met1Filter = ShapeFilter( self.layer.metal1)

        y     = contact.getBBox( polyFilter).getBottom()
        gates = mosBody.getCompsSorted( objType=MosGate)

        i = 0
        l = len( pattern)
        contacts = []
        while i < l:
            if ( i + 1) < l and ( pattern[ i] + 1) == pattern[ i+1]:
                right = gates[ pattern[ i+1]].getBBox( polyFilter).getRight()
                left  = gates[ pattern[ i  ]].getBBox( polyFilter).getLeft()
                cont = ContactGate1(
                    lowerLayer = self.layer.poly,
                    upperLayer = self.layer.metal1,
                    width      = right - left,
                )
                cont.alignLocationToPoint( Location.LOWER_LEFT, Point( left, y), filter=polyFilter)
                i += 2
            else:
                right = gates[ pattern[ i]].getBBox( polyFilter).getRight()
                left  = gates[ pattern[ i]].getBBox( polyFilter).getLeft()
                cont = ContactGate1(
                    lowerLayer = self.layer.poly,
                    upperLayer = self.layer.metal1,
                    width      = right - left,
                )
                cont.alignLocationToPoint( Location.LOWER_CENTER, Point( (left + right)/2.0, y), filter=polyFilter)
                cont.snapTowards( self.grid, Direction.EAST)
                i += 1

            contacts.append( cont)


        contacts = Grouping( components=contacts)
        mosBody.add( Rect( self.layer.metal1, contacts.getBBox( met1Filter)))
        contacts.ungroup( owner=mosBody)

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
        diffContacts = rowObj.getCompsSorted( objType=( ContactEdge, ContactCenter))

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

    def setPins( self):
        pass

    def setPins1(
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
        od2          = ( "DIFF_25",     "drawing"),
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
            masters         = ( "PmosDiffPair1", "NmosHDiffPair1", ),
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
            masters         = ( "PmosDiffPair1", "NmosHDiffPair1", ),
            widths          = ( 1.3, ),
            lengths         = ( 0.6, ),
            fingers         = ( 1, 2, 3, 4, 5, ),
            rows            = ( 1, 3, ),
            diffLeftStyles  = ( "ContactEdge1", "MosDummy1"),
            diffRightStyles = ( "ContactEdge1", "MosDummy1"),
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
            masters         = ( "PmosDiffPair1", ),
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
            masters         = ( "NmosDiffPair1", ),
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
            masters         = ( "PmosHDiffPair1", ),
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
            masters         = ( "NmosHDiffPair1", ),
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
    # cnpy -c "TEST='SMALL';LIB='MyPyCellLib_cni180';execfile('DiffPair1.py')"
    if "TEST" in vars():
        if   vars()["TEST"] == "SMALL":
            DloGen.withNewDlo( tinytest,  vars()["LIB"], "TINYTEST_DiffPair1",  "layout")
            DloGen.withNewDlo( smalltest, vars()["LIB"], "SMALLTEST_DiffPair1", "layout")
        elif vars()["TEST"] == "BIG":
            DloGen.withNewDlo( bigtest1,  vars()["LIB"], "BIGTEST1_DiffPair1",  "layout")
            DloGen.withNewDlo( bigtest2,  vars()["LIB"], "BIGTEST2_DiffPair1",  "layout")
            DloGen.withNewDlo( bigtest3,  vars()["LIB"], "BIGTEST3_DiffPair1",  "layout")
            DloGen.withNewDlo( bigtest4,  vars()["LIB"], "BIGTEST4_DiffPair1",  "layout")

# end
