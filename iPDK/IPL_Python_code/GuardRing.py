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
# GuardRing.py                                                         #
#                                                                      #
########################################################################
"""Module: GuardRing

This module implements a GuardRingTemplate class for creating guardRings
with stretch handles.



GuardRingTemplate provides the following capabilities:
    - (float  )  width
    - (float  )  height

    - (string )  Design rule set
    - (string )  Guard ring locations.

    - Electrical connectivity, i.e. nets, pins, terminals.



Class variables:
    - (tuple  )  contact,    layer & purpose name
    - (tuple  )  diffusion,  layer & purpose name
    - (tuple  )  implant,    layer & purpose name
    - (tuple  )  metal1,     layer & purpose name
    - (tuple  )  tapImplant, layer & purpose name
    - (tuple  )  well,       layer & purpose name



Technology file requirements:
    - (minWidth      contact             )
    - (minSpacing    contact             )
    - (minEnclosure  metal1     contact  )
    - (minEnclosure  diffusion  contact  )
    - (minEnclosure  tapImplant diffusion)
    - (minEnclosure  well       diffusion)



Module dependencies:
    - cni.dlo,      Ciranova PyCell APIs.



Exceptions:
    - ValueError, for incorrect parameter values.



Other notes:
    [1]
    """
from __future__ import with_statement

__version__  = "$Revision: 1.9 $"
__fileinfo__ = "$Id: GuardRing.py,v 1.9 2008/03/03 19:11:03 lyndon Exp lyndon $"
__author__   = "Lyndon C. Lim"

import math
import traceback

from cni.dlo import(
    Box,
    ChoiceConstraint,
    DeviceContext,
    Direction,
    DloGen,
    FailAction,
    Grid,
    Grouping,
    Instance,
    Location,
    ParamArray,
    ParamSpecArray,
    Rect,
    Ruleset,
    SnapType,
    StepConstraint,
    Term,
    TermType,
    Unique,
)

from MosUtils import (
    getCompsSorted,
    getDesignRule,
    orderedRuleset,
    rulesmgr,
    GuardRing,
    LayerDict,
)

from cni.integ.common import (
    createInstances,
    isEven,
    isOdd,
    renameParams,
    reverseDict,
    stretchHandle,
    Compare,
    Dictionary,
)

########################################################################

class GuardRingTemplate( DloGen):
    """Defines a GuardRingTemplate class.
        """
    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
    )

    guardringContext = None

    paramNames = dict(
        width          = "width",
        height         = "height",
        ruleset        = "ruleset",
        sides          = "sides",
    )

    default = dict()

    ####################################################################

    @classmethod
    def defineParamSpecs(cls, specs):
        """Define the PyCell parameters.  The order of invocation of
        specs() becomes the order on the form.

        Arguments:
        specs - (ParamSpecArray)  PyCell parameters
            """
        mySpecs    = ParamSpecArray()

        maskgrid   = specs.tech.getGridResolution()
        grid       = Grid( maskgrid, snapType=SnapType.CEIL)
        resolution = specs.tech.uu2dbu(1) * 10

        # Convert to process layer names
        layer   = LayerDict( specs.tech, cls.layerMapping)

        minSize = grid.snap(
            specs.tech.getPhysicalRule( "minWidth", layer.diffusion)
        )

        width  = max( cls.default.get( "width",  minSize), minSize)
        stepConstraint = StepConstraint( maskgrid, start=width, resolution=resolution, action=FailAction.REJECT)
        mySpecs( "width",   width, constraint = stepConstraint)

        height = max( cls.default.get( "height", minSize), minSize)
        stepConstraint = StepConstraint( maskgrid, start=height, resolution=resolution, action=FailAction.REJECT)
        mySpecs( "height", height, constraint = stepConstraint)

        # Design ruleset.
        ruleset = cls.default.get( "ruleset", "construction")
        mySpecs( "ruleset",  ruleset, constraint=ChoiceConstraint([ "recommended", "construction"]))

        sides = cls.default.get( "sides", "top,bottom,left,right")
        mySpecs( "sides", sides)

        # Parameter renaming
        renameParams( mySpecs, specs, cls.paramNames)

    ####################################################################

    def setupParams(self, params):
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
        self.sides = GuardRing.convertStringToList( self.sides)

        # Convert to process layer names
        self.layer = LayerDict( self.tech, self.layerMapping)

        # Design ruleset
        rulesets = [ "construction", "default"]
        if self.ruleset == "recommended":
            rulesets.insert( 0, "recommended")
        self.ruleset = orderedRuleset( self.tech, rulesets)

        self.maskgrid = self.tech.getGridResolution()

    ####################################################################

    def genTopology( self):
        """Build the layout.  Use "construction" ruleset if available.
            """
        Term("B", TermType.INPUT_OUTPUT)

    ####################################################################

    def genLayout( self):
        """Build the layout.  Use "construction" ruleset if available.
            """
        with rulesmgr( self.tech, Ruleset, self.ruleset):
            with rulesmgr( self.tech, DeviceContext, self.guardringContext):
                box = Box( 0, 0, self.width, self.height)
                g0  = Grouping()

                for key in ( "diffusion", "implant", "well"):
                    if self.layer[ key]:
                        g0.add(
                            Rect( self.layer[ key], box),
                        )

                if self.layer.well:
                    encLayers = [ self.layer.well]
                else:
                    encLayers = None

                gr = GuardRing(
                    comps        = [ g0],
                    locations    = self.sides,
                    lowerLayer   = self.layer.tapDiffusion,
                    upperLayer   = self.layer.metal1,
                    implantLayer = self.layer.tapImplant,
                    encLayers    = encLayers,
                )
                gr.setPin("B", "B")

                g0.destroy()

        self.addStretchProperties()

    ####################################################################

    def addStretchProperties(
        self):
        """Add stretch handle information for layout editors.
            """
        gr = self.getComps()[0]

        comps   = getCompsSorted(
            gr,
            objType      = Rect,
            sortFunction = Compare.cmpCenterXAscend,
        )

        rect = comps[-1]
        sname = Unique.Name()
        stretchHandle(
            name        = sname,
            shape       = rect,
            parameter   = self.paramNames["width"],
            location    = Location.CENTER_RIGHT,
            direction   = Direction.EAST_WEST,
            stretchType = "relative",
            minVal      = 0,
            userSnap    = "%f" % (self.maskgrid),
        )



        comps   = getCompsSorted(
            gr,
            objType      = Rect,
            layer        = self.layer.metal1,
            sortFunction = Compare.cmpCenterYAscend,
        )

        rect = comps[-1]
        sname = Unique.Name()
        stretchHandle(
            name        = sname,
            shape       = rect,
            parameter   = self.paramNames["height"],
            location    = Location.UPPER_CENTER,
            direction   = Direction.NORTH_SOUTH,
            stretchType = "relative",
            minVal      = 0,
            userSnap    = "%f" % (self.maskgrid),
        )

########################################################################

class PGuardRing( GuardRingTemplate):
    """PGuardRing class implements a ptap guard ring.
        """
    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = None,
    )

########################################################################

class NGuardRing( GuardRingTemplate):
    """NGuardRing class implements a ntap guard ring.
        """
    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        tapDiffusion = ( "DIFF",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
    )

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
        width    = "width",
        height   = "height",
        ruleset  = "ruleset",
        sides    = "sides",
    )

    def makeInstances(
        dlogen,
        masters,
        widths,
        heights,
        sides):
        """Create layout instances for quick development debugging.
            """
        paramSets = []
        for master in masters:
            # Assume the default parameters are minimum dimensions.
            inst   = Instance(("%s" % master))
            params = inst.getParams()

            listWidths  = [ params["width"]]
            listWidths.extend( widths)

            listHeights = [ params["height"]]
            listHeights.extend( heights)
            inst.destroy()

            for side in sides:
                for width in listWidths:
                    for height in listHeights:
                        params = ParamArray(
                            width  = width,
                            height = height,
                            sides  = side,
                        )
                        paramSets.append( [ master, params])

        createInstances( paramSets, paramNames, minColWidth=30, minRowHeight=30)



    def tinytest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters  = ( "PGuardRing", "NGuardRing", ),
            widths   = ( 1.0, 4.0, ),
            heights  = ( 1.0, 5.0, ),
            sides    = ( "top,left", "top,bottom,left,right", ),
        )
        self.save()



    def smalltest( self):
        """Create layout instances for quick development debugging.
            """
        makeInstances(
            self,
            masters  = ( "PGuardRing", "NGuardRing"),
            widths   = ( 1.0, 2.0, 4.0, 8.0),
            heights  = ( 1.0, 2.4, 5.0, 9.0),
            sides    = ( "top,bottom", "top,left", "top,bottom,left,right", ),
        )
        self.save()



    def bigtest1( self):
        """Create layout instances for comprehensive testing, such as DRC or
        regression testing.
            """
        makeInstances(
            self,
            masters  = ( "PGuardRing", "NGuardRing"),
            widths   = ( 1.0, 2.0, 4.0, 8.0),
            heights  = ( 1.0, 2.4, 5.0, 9.0),
            sides    = ( "top", "bottom", "left", "right", "top,bottom", "top,left", "left,right", "top,bottom,left,right", ),
        )
        self.save()



    # TEST is defined externally from this file.
    # For building the test cases, invoke like this:
    # cnpy -c "TEST='SMALL';LIB='MyPyCellLib_cni180';execfile('GuardRing.py')"
    if "TEST" in vars():
        if   vars()["TEST"] == "SMALL":
            DloGen.withNewDlo( tinytest,  vars()["LIB"], "TINYTEST_GuardRing",  "layout")
            DloGen.withNewDlo( smalltest, vars()["LIB"], "SMALLTEST_GuardRing", "layout")
        elif vars()["TEST"] == "BIG":
            DloGen.withNewDlo( bigtest1,  vars()["LIB"], "BIGTEST1_GuardRing",  "layout")

# end
