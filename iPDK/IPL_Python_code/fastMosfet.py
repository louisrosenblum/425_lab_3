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
# FastMosfet.py
########################################################################
# FastMosfet device demonstrating fast pycell evaluation 

__version__  = "$Revision: #2 $"

import cni
from cni.dlo import (
    Box,
    CompoundComponent,
    Direction,
    DloGen,
    GapStyle,
    Grid,
    Grouping,
    Instance,
    Layer,
    Net,
    Orientation,
    ParamArray,
    ParamSpecArray,
    Pin,
    Point,
    Range,
    Rect,
    RoutePath,
    Ruleset,
    SnapType,
    Term,
    TermType,
)

from cni.integ.common import (Dictionary)
cni.utils.importConstants(Direction)

########################################################################
# Utility method and classes.
# TODO, consolidate with MosUtils.py?
########################################################################
class LayerDict(object):
    """
Dictionary of Layer objects.  None is a valid value for a key.
    """
    def __init__(
        self,
        technology,
        layerMapping):

        for (key, value) in layerMapping.iteritems():
            setattr(self, key, technology.getLayer(*value) if value else None)

########################################################################
class RulesDict(object):
    """
Rule Dictionary using native Python object for fast caching of design rules.
Values are not restricted to single float values. I.e.
rulesDict.ruleName = value
    """

########################################################################
class SDCenter(CompoundComponent):
    """
Source/Drain Center contact between 2 Gate fingers.
    """
    def __init__(
        self,
        dlogen,
        leftCoord,  # location of adjacent Gate channel on left of this SDCenter
        orient, # Orientation is R0 for right edge or MY for left edge
        contFormat = None,  # Contact format
        genContact = True,  # Generate upper layer Contact
        ):
        CompoundComponent.__init__(self)

        # SDCenter has 1 diffusion Rect and 1 optional metal1Rect.
        # Contact cuts are always centered on diff Rect.
        # In case of dogbone, diffusion Rect will represent the part
        # connecting to the contact cut.

        # Use dirMult to handle orientation
        dirMult = 1 if orient == Orientation.R0 else -1
        topo = dlogen.topo
        rules = dlogen.rules
        layers = dlogen.layers

        # Left box edge for diffusion.
        # Diffusion rect will align with gate for non-dogbone,
        # and will detach from gate for dogbone.
        diffBoxLeft = leftCoord
        # Bottom and top box edges for diffusion
        diffBoxBottom = 0
        diffBoxTop = diffBoxBottom + topo.wf
        isDogbone = topo.isDogbone

        if isDogbone:
            diffBoxLeft += dirMult*(topo.dogboneSDHorzOffset + 0.5*topo.gateSpacingAdd)
            diffBoxBottom = topo.dogboneSDBottom
            diffBoxTop = topo.dogboneSDTop
            diffBoxRight = diffBoxLeft + dirMult*rules.minWidthDiffEncContact
        else:
            diffBoxRight = diffBoxLeft + dirMult*topo.gateSpace

        # Create diff Rect
        diffBox = Box(diffBoxLeft, diffBoxBottom, diffBoxRight, diffBoxTop).fix()
        self.diffRect = diffRect = Rect(layers.diffusion, diffBox)
        self.add(diffRect)

        if genContact:
            # Calculate via and metal boxes
            diffBoxCenterX = diffBox.getCenterX()
            viaFillBox = Box(diffBoxCenterX, diffBoxBottom, diffBoxCenterX, diffBoxTop)
            diffExtContact = rules.diffExtContact
            viaWidth = rules.contactWidth
            viaSpace = rules.contactSpace
            viaFillBox.expand(NORTH_SOUTH, -diffExtContact)
            viaFillBox.expand(EAST_WEST, 0.5*viaWidth)
            metalBox = Box(viaFillBox)
            metalBox.expand(NORTH_SOUTH, rules.metal1EndExtContact)
            metalBox.expand(EAST_WEST, rules.metal1ExtContact)
            # Generate via fills
            Rect.fillBBoxWithRects(layers.contact, viaFillBox,
                viaWidth, viaWidth, viaSpace, viaSpace, GapStyle.DISTRIBUTE,
                self)
            # Generate metal Rect
            self.metal1Rect = metal1Rect = Rect(layers.metal1, metalBox)
            self.add(metal1Rect)
        else:
            self.metal1Rect = None

########################################################################
class SDEdge(CompoundComponent):
    """
Source/Drain Edge contact at left or right side of Mos body.
    """
    def __init__(
        self,
        dlogen,
        leftCoord,  # location of adjacent Gate channel on left of this SDEdge
        orient, # Orientation is R0 for right edge or MY for left edge
        abutStyle,   # Abutment style
        abutStyleIsDiff,    # Is Abutment style diffusion type?
        diffInc = 0,    # Diffusion increment
        gaCoSpaceInc = 0,   # Gate to Co cut increment
        contFormat = None,  # Contact format
        abutWellTap = False,    # Abutting to well tap?
        genContact = True,  # Generate upper layer Contact
        ):
        CompoundComponent.__init__(self)

        # SDEdge has 1 diffusion Rect and 1 optional metal1Rect.
        # Contact cuts are always centered on diff Rect.
        # In case of dogbone, diffusion Rect will represent the part
        # connecting to the contact cut.

        # Use dirMult to handle orientation
        orientationR0 = Orientation.R0
        dirMult = 1 if orient == orientationR0 else -1
        topo = dlogen.topo
        rules = dlogen.rules
        rulesDiffExtContact = rules.diffExtContact
        layers = dlogen.layers
        maskGrid = dlogen.maskGrid

        #print "leftCoord=", leftCoord
        # Left box edge for diffusion.
        # For diffusion abutment, diffusion shape must align to gate.
        # For contact edge abutment, diffusion is generated for only contact.
        diffBoxLeft = leftCoord
        # Bottom and top box edges for diffusion
        diffBoxBottom = 0
        diffBoxTop = diffBoxBottom + topo.wf

        # Get data for dogbone
        isDogbone = topo.isDogbone
        if isDogbone:
            dogboneSDHorzOffset = topo.dogboneSDHorzOffset

        if abutStyleIsDiff:
            genContact = False
        else:
            # offsetting contact diff box for gaCoSpaceInc
            if isDogbone:
                diffBoxLeft += dirMult*(gaCoSpaceInc + dogboneSDHorzOffset)
                diffBoxBottom = topo.dogboneSDBottom
                diffBoxTop = topo.dogboneSDTop
                viaFillBoxLeft = diffBoxLeft + dirMult*rulesDiffExtContact
            else:
                viaFillBoxLeft = diffBoxLeft + dirMult*(gaCoSpaceInc + rules.contactClrGate)

        # Find diffusion edge for different abutment style
        if abutStyle == "ContactEdge" or abutStyle == "ContactEdgeAbut":
            # Contact edge
            if isDogbone:
                diffWidth = rules.minWidthDiffEncContact
                diffWidth += diffInc - gaCoSpaceInc
            else:
                diffWidth = rules.contactClrGate + rules.contactWidth + rulesDiffExtContact
                diffWidth += diffInc
        elif abutStyle == "DiffAbut":
            # Diffusion Abutting to same width ContactEdge partner
            if isDogbone:
                diffWidth = dogboneSDHorzOffset
            else:
                contactDiffGateAndTrenchDelta = rules.contactClrGate - rulesDiffExtContact
                diffWidth = max(dlogen.gridResolution, contactDiffGateAndTrenchDelta)
            diffWidth += diffInc
        elif abutStyle == "DiffEdgeAbut":
            # Diffusion abuting to larger width ContactEdge partner
            diffWidth = rules.polyClrDiff
            diffWidth += diffInc
        elif abutStyle == "DiffHalf":
            # Half Diffusion Abutting to same Half Diffusion
            diffWidth = rules.gateSpace*0.5
            diffWidth += diffInc
        else:
            raise RuntimeError("Invalid abutStyle '%s'. Must be one of 'ContactEdge', 'ContactEdgeAbut', 'DiffAbut', 'DiffEdgeAbut', or 'DiffHalf'" % abutStyle)

        # Handle abutting well tap
        if abutWellTap and abutStyle == "ContactEdge":
            abutWellTapDiffInc = max(0, rules.implantExtContact - rulesDiffExtContact)
            diffWidth += abutWellTapDiffInc

        diffBoxRight = diffBoxLeft + dirMult*diffWidth

        # Create diff Rect
        diffBox = Box(diffBoxLeft, diffBoxBottom, diffBoxRight, diffBoxTop).fix()
        #print "diffBox=", diffBox
        self.diffRect = diffRect = Rect(layers.diffusion, diffBox)
        self.add(diffRect)

        if genContact:
            # Calculate via and metal boxes
            viaFillBox = Box(diffBox)
            viaWidth = rules.contactWidth
            viaSpace = rules.contactSpace
            viaFillBox.expand(NORTH_SOUTH, -rulesDiffExtContact)
            viaFillBox.setLeft(viaFillBoxLeft)
            viaFillBox.setRight(viaFillBoxLeft + dirMult*viaWidth)
            viaFillBox.fix()
            metalBox = Box(viaFillBox)
            metalBox.expand(NORTH_SOUTH, rules.metal1EndExtContact)
            metalBox.expand(EAST_WEST, rules.metal1ExtContact)
            # Generate via fills
            Rect.fillBBoxWithRects(layers.contact, viaFillBox,
                viaWidth, viaWidth, viaSpace, viaSpace, GapStyle.DISTRIBUTE,
                self)
            # Generate metal Rect
            self.metal1Rect = metal1Rect = Rect(layers.metal1, metalBox)
            self.add(metal1Rect)
        else:
            self.metal1Rect = None

########################################################################
class Gate(CompoundComponent):
    """
Gate contains 3 poly Shapes: channel, top finger pin, and bottom finger pin.
    """
    def __init__(
        self,
        leftCoord,  # Left Coord of gate
        layer,  # gate layer
        length, # gate length
        width,  # gate width
        pinHeight,  # Top and bottom pin height
        ):
        CompoundComponent.__init__(self)

        rightCoord = leftCoord + length
        selfAdd = self.add
        # Finger channel, index 0
        selfAdd(Rect(layer, Box(leftCoord, 0, rightCoord, width)))
        # Finger bottom pin, index 1
        selfAdd(Rect(layer, Box(leftCoord, -pinHeight, rightCoord, 0)))
        # Finger top pin, index 2
        selfAdd(Rect(layer, Box(leftCoord, width, rightCoord, width + pinHeight)))

########################################################################
class GateContact(CompoundComponent):
    """
GateContact contains 2 main Shapes: poly and metal1.
Contact cuts are filled in.
    """
    def __init__(
        self,
        dlogen,
        box,  # Box for poly layer, lowerLeft point is Contact origin point.
        ):
        CompoundComponent.__init__(self)
        rules = dlogen.rules
        layers = dlogen.layers
        polyLayer = layers.poly
        metal1Layer = layers.metal1
        contactLayer = layers.contact

        boxWidth = box.getWidth()
        dirMult = 1 if boxWidth > 0 else -1
        # Expand and center width to fit at least 1 cut
        minWidthPolyEncContact = rules.minWidthPolyEncContact
        if abs(boxWidth) < minWidthPolyEncContact:
            newBox = Box(box)
            newBox.setRight(newBox.getLeft() + dirMult*minWidthPolyEncContact)
            newBox.alignEdge(EAST_WEST, box)
            newBox.snapTowards(dlogen.maskGrid, EAST)
            box = newBox

        # Generate poly Rect
        self.polyRect = polyRect = Rect(polyLayer, box.fix())
        self.add(polyRect)

        # Generate via fill
        viaFillBox = Box(box)
        viaFillBox.expand(-dirMult*rules.polyExtContact)
        viaWidth = rules.contactWidth
        viaSpace = rules.contactSpace
        Rect.fillBBoxWithRects(layers.contact, viaFillBox,
            viaWidth, viaWidth, viaSpace, viaSpace, GapStyle.DISTRIBUTE, self)

        # Generate metal Rect
        metalBox = Box(viaFillBox)
        metalBox.expand(NORTH_SOUTH, rules.metal1ExtContact)
        metalBox.expand(EAST_WEST, rules.metal1EndExtContact)
        self.metal1Rect = metal1Rect = Rect(metal1Layer, metalBox)
        self.add(metal1Rect)

########################################################################
class BulkContact(CompoundComponent):
    """
BulkContat contains 3 main Shapes: diffusion, metal1, and tap implant.
Contact cuts are filled in.
    """
    def __init__(self,
        dlogen,
        sdContact,  # Adjacent SD Contact
        orient,     # Orientation is R0 for right, MY for left
        tapStyle,   # tap style is Integrated to sdContact
                    # or Detached from sdContact.
        ):
        CompoundComponent.__init__(self)

        rules = dlogen.rules
        layers = dlogen.layers
        maskGrid = dlogen.maskGrid

        if orient == Orientation.R0:
            dirToSD = WEST
            dirToTap = EAST
            dirMult = 1
        else:
            dirToSD = EAST
            dirToTap = WEST
            dirMult = -1

        # Tap diffusion are vertically aligned with sdContact diffusion
        sdContDiffBox = sdContact.diffRect.getBBox()
        diffBox = Box(sdContDiffBox)

        diffBoxLeft = sdContDiffBox.getCoord(dirToTap)
        diffWidth = rules.minWidthTapEncContact

        # Detached contact needs room for implant
        if tapStyle == "Detached":
            diffBoxLeft += dirMult*(rules.implantExtDiff + rules.tapImplantExtTap)
        # TODO, Enable "Integrated" choice for tap when Tech file supports it
        #elif tapStyle != "Integrated":
        #    raise RuntimeError("Invalid tap style '%s'. Must be one of 'Integrated', or 'Detached'" % tapStyle)
        else:
            raise RuntimeError("Invalid tap style '%s'. Must be 'Detached'" % tapStyle)

        diffBox.setLeft(diffBoxLeft)
        diffBox.setRight(diffBoxLeft + dirMult*diffWidth)
        diffBox.fix()

        # Detached contact needs to meet min area rule
        if tapStyle == "Detached":
            diffBox.expandForMinArea(dirToTap, rules.diffMinArea, maskGrid)

        # Create diff Rect
        self.diffRect = diffRect = Rect(layers.diffusion, diffBox)
        selfAdd = self.add
        selfAdd(diffRect)

        # Create implant
        tapImpBox = Box(diffBox)
        tapImpExtTap = rules.tapImplantExtTap
        tapImpBox.expand(tapImpExtTap)
        if tapStyle == "Integrated":
            tapImpBox.setCoord(dirToSD, diffBox.getCoord(dirToSD))
        self.implantRect = tapImpRect = Rect(layers.tapImplant, tapImpBox)
        selfAdd(tapImpRect)

        # Create via fill
        viaFillBox = Box(diffBox)
        viaFillBox.expand(-rules.diffExtContact)
        viaWidth = rules.contactWidth
        viaSpace = rules.contactSpace
        Rect.fillBBoxWithRects(layers.contact, viaFillBox,
            viaWidth, viaWidth, viaSpace, viaSpace, GapStyle.DISTRIBUTE,
            self)

        # Generate metal Rect
        metal1Layer = layers.metal1
        metalBox = Box(viaFillBox)
        metalBox.expand(NORTH_SOUTH, rules.metal1EndExtContact)
        metalBox.expand(EAST_WEST, rules.metal1ExtContact)
        self.metal1Rect = metal1Rect = Rect(metal1Layer, metalBox)
        selfAdd(metal1Rect)

        # Join metal for integrated tap
        self.joinMetal1Rect = None
        if tapStyle == "Integrated":
            joinMetalBox = Box(metalBox)
            sdMetalRangeX = sdContact.metal1Rect.getBBox().getRangeX()
            joinMetalRangeX = joinMetalBox.getRangeX()
            if joinMetalRangeX.intersect(sdMetalRangeX).isInverted():
                joinMetalRangeX.fix()
                joinMetalBox.setRangeX(joinMetalRangeX)
                self.joinMetal1Rect = joinMetal1Rect = Rect(metal1Layer, joinMetalBox)
                selfAdd(joinMetal1Rect)

########################################################################
class FastMosfetTemplate(DloGen):
    """
Fast Mosfet template base class.
    """
    tranType   = "nmos"
    oxide      = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        active       = ( "NACT",    "drawing"),
        tapDiffusion = ( "PTAP",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = None,
    )

    ####################################################################
    @classmethod
    def defineParamSpecs(cls, specs):
        """
Define Mosfet PyCell parameters.
        """
        tech = specs.tech
        techGetMosfetParams = tech.getMosfetParams
        tranType = cls.tranType
        oxide = cls.oxide
        # Length of finger 
        minLength = techGetMosfetParams(tranType, oxide, "minLength")
        specs("lf", minLength)
        # Width of finger
        minWidth = techGetMosfetParams(tranType, oxide, "minWidth")
        specs("wf", minWidth)
        # Number of fingers
        specs("fr", 1)
        # Left Abutment style, ["ContactEdge", "ContactEdgeAbut", "DiffAbut",
        #                       "DiffEdgeAbut", "DiffHalf"]
        # ContactEdge is normal, non-abutment case.
        # It has non-zero implant enclose diff.
        # ContactEdgeAbut is ContactEdge abutment to DiffAbut partner.
        # It has implant align with diff.
        # DiffAbut is Diffusion abutment to ContactEdgeAbut partner.
        # It has only diffusion, with implant align with diff.
        # DiffEdgeAbut is Diffusion abutment to ContactEdgeAbut partner,
        # with the partner having wider finger width.
        # It has only diffusion with length adequate for polyClrDiff,
        # andwith implant align with diff.
        specs("diffLeftStyle", "ContactEdge")
        # Right Abutment style, options same as diffLeftStyle
        specs("diffRightStyle", "ContactEdge")
        # Generate left Contact?
        specs("leftCont", True)
        # Generate right Contact?
        specs("rightCont", True)
        # Generate inter center Contacts?
        specs("centerCont", True)
        # Route Source contacts, ["None", "Top", "Bottom"]
        specs("routeSrc", "Bottom")
        # Route Drain contacts, options same as routeSrc
        specs("routeDrn", "Top")
        # Route Gate fingers, ["None", "Top", "Bottom", "Both"]
        specs("routeGate", "Both")
        # Drain is larger than source?
        specs("largeDrn", False)
        # Left dummy finger
        specs("leftDummy", False)
        # Right dummy finger
        specs("rightDummy", False)
        # Left tap, ["None", "Detached"]
        # TODO, Add "Integrated" choice to leftTap when Tech file supports it.
        specs("leftTap", "None")
        # Right tap, options same as leftTap
        specs("rightTap", "None")

        # Parameters supporting manual layout editing
        # Increase finger to finger spacing
        specs("gateSpacingAdd", 0.0)
        # Increase gate to contact cut spacing
        specs("cgSpacingAdd", 0.0)
        # Increase left side diffusion width
        specs("leftDiffAdd", 0.0)
        # Increase right side diffusion width
        specs("rightDiffAdd", 0.0)
        # Increase left gate to left contact cut spacing
        specs("leftCgSpacingAdd", 0.0)
        # Increase right gate to right contact cut spacing
        specs("rightCgSpacingAdd", 0.0)

        # Turn on for super master testing
        #cls.defineParamSpecsTest(specs)

    ####################################################################
    # Define ParamSpecArray for super-master testing
    @classmethod
    def defineParamSpecsTest( cls, specs):
        specs.remove("wf", "fr",
            "diffLeftStyle", "diffRightStyle",
            "routeSrc", "routeDrn",
            "routeGate",
            "leftDummy", "rightDummy",
            "leftTap", "rightTap",
            "leftDiffAdd", "rightDiffAdd",
        )
        specs("wf", 0.2)
        specs("fr", 3)
        specs("diffLeftStyle", "ContactEdge")
        specs("diffRightStyle", "ContactEdge")
        specs("routeSrc", "Bottom")
        specs("routeDrn", "Top")
        specs("routeGate", "Both")
        specs("leftDummy", False)
        specs("rightDummy", False)
        specs("leftTap", "Detached")
        specs("rightTap", "Integrated")
        specs("leftDiffAdd", 0.0)
        specs("rightDiffAdd", 0.0)

    ####################################################################
    def setupParams(self, params):
        """
Process PyCell parameters, prior to geometric construction.
Decide process rules and PyCell-specific behaviors.
        """
        self.params = params
        tech = self.tech
        # Convert to process layer names.
        self.layers = layers = LayerDict(tech, self.layerMapping)

        # Process grid
        self.gridResolution = tech.getGridResolution()
        self.maskGrid = maskGrid = Grid(self.gridResolution)

        # Dictionary of topology info
        self.topo = topo = Dictionary()
        # Obtain parameters
        topo.lf = params["lf"]
        topo.fr = params["fr"]
        topo.wf = params["wf"]
        topo.diffLeftStyle = params["diffLeftStyle"]
        topo.diffRightStyle = params["diffRightStyle"]
        topo.leftCont = params["leftCont"]
        topo.rightCont = params["rightCont"]
        topo.centerCont = params["centerCont"]
        topo.routeSrc = params["routeSrc"]
        topo.routeDrn = params["routeDrn"]
        topo.routeGate = params["routeGate"]
        topo.largeDrn = params["largeDrn"]
        topo.leftDummy = params["leftDummy"]
        topo.rightDummy = params["rightDummy"]
        topo.leftTap = params["leftTap"]
        topo.rightTap = params["rightTap"]

        # Parameters supporting manual layout editing
        topo.gateSpacingAdd = maskGrid.snap(params["gateSpacingAdd"], mult=2)
        topo.cgSpacingAdd = params["cgSpacingAdd"]
        topo.leftDiffAdd = params["leftDiffAdd"]
        topo.rightDiffAdd = params["rightDiffAdd"]
        topo.leftCgSpacingAdd = params["leftCgSpacingAdd"]
        topo.rightCgSpacingAdd = params["rightCgSpacingAdd"]
        
        # Check param consistency
        # S/D routing is provided only when all S/D contacts are available.
        if topo.leftCont is False or topo.rightCont is False or topo.centerCont is False:
            topo.routeSrc = topo.routeDrn = "None"
        # Dummy and tap are provided only when abutStyle is normal ContactEdge.
        if topo.diffLeftStyle != "ContactEdge":
            topo.leftDummy = False
            topo.leftTap = "None"
        if topo.diffRightStyle != "ContactEdge":
            topo.rightDummy = False
            topo.rightTap = "None"
        # Edge DIFF_INC must be adequate for edge cgSpacingAdd
        topo.leftDiffAdd = max(topo.leftDiffAdd, topo.leftCgSpacingAdd)
        topo.rightDiffAdd = max(topo.rightDiffAdd, topo.rightCgSpacingAdd)

        # Obtain rules
        self.setupRules()
        rules = self.rules

        # Compute topology data
        # gateSpace is spacing between gate fingers
        # gatePitch is pitch between gate fingers
        minWidthDiffEncContact = rules.minWidthDiffEncContact
        topo.isDogbone = isDogbone = self.uu2dbu(topo.wf) < self.uu2dbu(minWidthDiffEncContact)
        if isDogbone:
            topo.gateSpace = minWidthDiffEncContact + 2*rules.polyClrDiff
            # dogboneSDBottom is bottom edge of dogbone SD Diffusion
            topo.dogboneSDBottom = dogboneSDBottom = maskGrid.snap(-0.5*(minWidthDiffEncContact - topo.wf))
            topo.dogboneSDTop = dogboneSDBottom + minWidthDiffEncContact
            # dogboneSDHorzOffset is left/right offset of SD Diffusion
            # from gate's left/right.
            topo.dogboneSDHorzOffset = rules.polyClrDiff
        else:
            topo.gateSpace = rules.contactWidth + 2*rules.contactClrGate
        topo.gateSpace += topo.gateSpacingAdd
        topo.gatePitch = topo.gateSpace + topo.lf

        # Determine abutment types
        diffAbutmentStyle = ["DiffAbut", "DiffEdgeAbut", "DiffHalf"]
        topo.leftAbutmentIsDiff = topo.diffLeftStyle in diffAbutmentStyle
        topo.rightAbutmentIsDiff = topo.diffRightStyle in diffAbutmentStyle

        #print "topo=", topo

    ####################################################################
    def setupRules(self):
        """
Setup rules by loading from Tech into RulesDict cache.
Use caching for speed.
        """
        # Create fast rule cache of generic rules
        self.rules = rules = RulesDict()
        tech = self.tech
        layers = self.layers
        wellLayer = layers.well
        diffLayer = layers.diffusion
        activeLayer = layers.active
        tapDiffLayer = layers.tapDiffusion
        polyLayer = layers.poly
        implantLayer = layers.implant
        tapImplantLayer = layers.tapImplant
        contactLayer = layers.contact
        metal1Layer = layers.metal1

        techGetRule = tech.getPhysicalRule
        minArea = "minArea"
        minClearance = "minClearance"
        minExtension = "minExtension"
        minSpacing = "minSpacing"
        minWidth = "minWidth"
        # Well layer
        if wellLayer:
            rules.wellMinWidth = techGetRule(minWidth, wellLayer)
            rules.wellExtDiff = techGetRule(minExtension, wellLayer, diffLayer)
        # Diff layer
        rules.diffExtContact = techGetRule(minExtension, diffLayer, contactLayer)
        rules.diffMinArea = techGetRule(minArea, diffLayer)
        # Tap diffusion layer
        rules.tapExtContact = techGetRule(minExtension, tapImplantLayer, contactLayer)
        # Poly layer
        rules.polyClrDiff = techGetRule(minClearance, polyLayer, diffLayer)
        rules.polyExtContact = techGetRule(minExtension, polyLayer, contactLayer)
        rules.polyExtDiff = techGetRule(minExtension, polyLayer, diffLayer)
        # Derived gate layer
        # TODO, Get precise value for min gate to gate spacing
        rules.gateSpace = 2*techGetRule(minSpacing, polyLayer)
        # Implant layer
        rules.implantExtDiff = techGetRule(minExtension, implantLayer, diffLayer)
        rules.implantExtPoly = techGetRule(minExtension, implantLayer, polyLayer)
        rules.implantClrTap = techGetRule(minClearance, implantLayer, tapDiffLayer)
        rules.implantExtContact = techGetRule(minExtension, implantLayer, contactLayer)
        # Tap implant layer
        rules.tapImplantExtTap = techGetRule(minExtension, tapImplantLayer, tapDiffLayer)
        rules.tapImplantClrDiff = techGetRule(minClearance, tapImplantLayer, activeLayer)
        # Contact layer
        rules.contactWidth = techGetRule(minWidth, contactLayer)
        rules.contactSpace = techGetRule(minSpacing, contactLayer)
        rules.contactClrGate = techGetRule(minClearance, contactLayer, polyLayer)
        # Metal1 layer
        rules.metal1Space = techGetRule(minSpacing, metal1Layer)
        metal1ContactExts = cni.utils.getMinExtensions(tech, metal1Layer, contactLayer)
        rules.metal1ExtContact = metal1ContactExts[0]
        rules.metal1EndExtContact = metal1ContactExts[1]

        # N implant and P implant should be abuttable
        rules.implantExtDiff = rules.tapImplantClrDiff = max(rules.implantExtDiff, rules.tapImplantClrDiff)
        rules.tapImplantExtTap = rules.implantClrTap = max(rules.tapImplantExtTap, rules.implantClrTap)

        # Update for rule increment
        topo = self.topo
        rules.contactClrGate += topo.cgSpacingAdd
        rules.gateSpace += topo.gateSpacingAdd

        # Prepare derived rules
        contactWidth = rules.contactWidth
        rules.minWidthDiffEncContact = 2*rules.diffExtContact + contactWidth
        rules.minWidthTapEncContact = 2*rules.tapExtContact + contactWidth
        rules.minWidthPolyEncContact = 2*rules.polyExtContact + contactWidth
        rules.minWidthMetal1EncContact = 2*rules.metal1ExtContact + contactWidth
        rules.minWidthMetal1EndEncContact = 2*rules.metal1EndExtContact + contactWidth

    ####################################################################
    def genLayout(self):
        """
Generate layout objects and their geometries.
        """
        # Create transistor SDG fingers
        self.createTransistor()
        # Route Source Drain
        self.routeSD()
        # Route Gate
        self.routeGate()

        # Generate shared layers
        self.genSharedLayers()

        # Generate connectivity
        self.genConnectivity()

    ####################################################################
    def createTransistor(self):
        """
Create transistor Src and Drn body.
        """
        # Dictionary of layout objects
        self.layout = layout = Dictionary()
        # List of SD contacts on each side of non-dummy fingers
        layout.sdContacts = sdContacts = list()

        rules = self.rules

        layers = self.layers
        polyLayer = layers.poly

        topo = self.topo
        numFingers = topo.fr
        fingerLength = topo.lf
        fingerWidth = topo.wf
        gatePitch = topo.gatePitch
        gateSpace = topo.gateSpace
        gatePinHeight = rules.polyExtDiff
        curLocation = 0

        # Generate left side of finger stacks
        orientationMY = Orientation.MY
        if topo.leftDummy:
            # Create SD for first gate
            sdContact = SDCenter(self, curLocation, orientationMY,
                None, topo.centerCont)
            sdContacts.append(sdContact)
            # Create dummy finger
            curLocation -= gatePitch
            layout.leftDummy = Gate(curLocation, polyLayer, fingerLength,
                fingerWidth, gatePinHeight)

        # Create leftSD
        abutWellTap = topo.leftTap == "Integrated"
        layout.leftSD = leftSD = SDEdge(self, curLocation, orientationMY,
            topo.diffLeftStyle, topo.leftAbutmentIsDiff,
            topo.leftDiffAdd, topo.leftCgSpacingAdd,
            None, abutWellTap, topo.leftCont)
        if not topo.leftDummy:
            sdContacts.append(leftSD)

        # Create Gates 
        layout.gates = gates = list()
        # Each gate finger is a CompoundComponent with 3 Shapes
        # for finger channel, bottom pin, and top pin.
        gateLeft = 0
        for i in xrange(numFingers):
            gate = Gate(gateLeft, polyLayer, fingerLength, fingerWidth,
                gatePinHeight)
            gates.append(gate)
            gateLeft += gatePitch

        # Create center SD
        orientationR0 = Orientation.R0
        # Each center SD is a CompoundComponent implented by SDCenter
        centerSDLeft = fingerLength
        for i in xrange(numFingers-1):
            centerSD = SDCenter(self, centerSDLeft, orientationR0,
                None, topo.centerCont)
            sdContacts.append(centerSD)
            centerSDLeft += gatePitch

        # Generate right side of finger stacks
        curLocation = gateLeft - gateSpace
        if topo.rightDummy:
            # Create SD for last gate
            sdContact = SDCenter(self, curLocation, orientationR0,
                None, topo.centerCont)
            sdContacts.append(sdContact)
            # Create dummy finger
            curLocation += gateSpace
            layout.rightDummy = Gate(curLocation, polyLayer, fingerLength,
                fingerWidth, gatePinHeight)
            curLocation += fingerLength

        # Create rightSD
        abutWellTap = topo.rightTap == "Integrated"
        layout.rightSD = rightSD = SDEdge(self, curLocation, orientationR0,
            topo.diffRightStyle, topo.rightAbutmentIsDiff,
            topo.rightDiffAdd, topo.rightCgSpacingAdd,
            None, abutWellTap, topo.rightCont)
        if not topo.rightDummy:
            sdContacts.append(rightSD)

        # Create diffusion under fingers
        diffRectLeft = leftSD.diffRect.getLeft()
        diffRectRight = rightSD.diffRect.getRight()
        diffRectBox = Box(diffRectLeft, 0, diffRectRight, fingerWidth)
        layout.sdDiffRect = Rect(layers.diffusion, diffRectBox)

        # Create left tap
        leftTapStyle = topo.leftTap
        if leftTapStyle != "None":
            layout.leftTap = BulkContact(self, leftSD, orientationMY,
                leftTapStyle)
        else:
            layout.leftTap = None

        # Create right tap
        rightTapStyle = topo.rightTap
        if rightTapStyle != "None":
            layout.rightTap = BulkContact(self, rightSD, orientationR0,
                rightTapStyle)
        else:
            layout.rightTap = None

    ####################################################################
    def routeSD(self):
        """
Route Source and Drain fingers
        """
        topo = self.topo
        rules = self.rules
        layout = self.layout
        layers = self.layers
        metal1Layer = layers.metal1

        # Source and Drain routing bars
        layout.srcBar = layout.drnBar = None

        # Provide space for SD routing when parameter requested SD routing
        # even if no SD fingers can be routed.
        topo.topSDBarRange = topo.bottomSDBarRange = None

        # evenRouteDir, oddRouteDir are routing direction of even/odd SD fingers
        # Default is Source finger outside (large Source).
        # Default source fingers are even fingers.

        # Route Source finger info
        topoRouteSrc = topo.routeSrc
        if topoRouteSrc == "None":
            evenRouteDir = None
        else:
            if topoRouteSrc == "Top":
                evenRouteDir = NORTH
            elif topoRouteSrc == "Bottom":
                evenRouteDir = SOUTH
            else:
                raise RuntimeError("Invalid routeSrc '%s'. Must be one of 'None', 'Top', or 'Bottom'" % topoRouteSrc)

        # Route Drain finger info
        topoRouteDrn = topo.routeDrn
        if topoRouteDrn == "None":
            oddRouteDir = None
        else:
            if topoRouteDrn == "Top":
                oddRouteDir = NORTH
            elif topoRouteDrn == "Bottom":
                oddRouteDir = SOUTH
            else:
                raise RuntimeError("Invalid routeDrn '%s'. Must be one of 'None', 'Top', or 'Bottom'" % topoRouteDrn)
            if evenRouteDir == oddRouteDir:
                raise RuntimeError("Invalid routeDrn and routeSrc in same direction '%s'" % topoRouteDrn)

        #print "evenRouteDir=", evenRouteDir, "oddRouteDir=", oddRouteDir
        # No SD routing
        if (evenRouteDir is None) and (oddRouteDir is None):
            return

        # Switch routeDir for large Drain
        topoLargeDrn = topo.largeDrn
        if topoLargeDrn:
            [evenRouteDir, oddRouteDir] = [oddRouteDir, evenRouteDir]

        # Find SD routeBar vertical edges
        diffBottomEdge = 0
        diffTopEdge = topo.wf
        if topo.isDogbone:
            diffBottomEdge = topo.dogboneSDBottom
            diffTopEdge = topo.dogboneSDTop
        metalSpacingFromDiff = rules.metal1Space + (rules.metal1EndExtContact - rules.diffExtContact)
        
        topSDBarBottom = diffTopEdge + metalSpacingFromDiff
        bottomSDBarTop = diffBottomEdge - metalSpacingFromDiff
        # Choose sdBarWidth to be minWidthMetal1EncContact
        sdBarWidth = rules.minWidthMetal1EncContact
        if evenRouteDir == SOUTH or oddRouteDir == NORTH:
            evenSDBarEdge = bottomSDBarTop
            evenSDBarFarEdge = evenSDBarEdge - sdBarWidth
            oddSDBarEdge = topSDBarBottom
            oddSDBarFarEdge = oddSDBarEdge + sdBarWidth
        else:
            evenSDBarEdge = topSDBarBottom
            evenSDBarFarEdge = evenSDBarEdge + sdBarWidth
            oddSDBarEdge = bottomSDBarTop
            oddSDBarFarEdge = oddSDBarEdge - sdBarWidth
        # Save top and bottom SD Bar Range
        for routeDir in [evenRouteDir, oddRouteDir]:
            if routeDir == NORTH:
                topo.topSDBarRange = Range(topSDBarBottom, topSDBarBottom+sdBarWidth)
            elif routeDir == SOUTH:
                topo.bottomSDBarRange = Range(bottomSDBarTop, bottomSDBarTop-sdBarWidth)

        # Route SD contacts
        numSDContacts = topo.fr + 1
        sdContacts = layout.sdContacts
        evenRouteRects = list()
        # Route even SD contacts
        if evenRouteDir:
            for i in xrange(0, numSDContacts, 2):
                sdContactMetalRect = sdContacts[i].metal1Rect
                if sdContactMetalRect:
                    routeBox = sdContactMetalRect.getBBox()
                    routeBox.setBottom(routeBox.getCoord(evenRouteDir))
                    routeBox.setTop(evenSDBarEdge)
                    routeRect = Rect(metal1Layer, routeBox.fix())
                    evenRouteRects.append(routeRect)
        # Route even SD bar
        sdDiffRectBox = layout.sdDiffRect.getBBox()
        if len(evenRouteRects):
            if topo.diffLeftStyle != "ContactEdge":
                barLeft = sdDiffRectBox.getLeft()
            else:
                barLeft = evenRouteRects[0].getLeft()
            if (numSDContacts % 2 == 1) and (topo.diffRightStyle != "ContactEdge"):
                barRight = sdDiffRectBox.getRight()
            else:
                barRight = evenRouteRects[-1].getRight()
            evenSDBarBox = Box(barLeft, evenSDBarEdge, barRight, evenSDBarFarEdge).fix()
            evenSDBar = Rect(metal1Layer, evenSDBarBox)
        else:
            evenSDBar = None

        # Route odd SD contacts
        oddRouteRects = list()
        if oddRouteDir:
            for i in xrange(1, numSDContacts, 2):
                sdContactMetalRect = sdContacts[i].metal1Rect
                if sdContactMetalRect:
                    routeBox = sdContactMetalRect.getBBox()
                    routeBox.setBottom(routeBox.getCoord(oddRouteDir))
                    routeBox.setTop(oddSDBarEdge)
                    routeRect = Rect(metal1Layer, routeBox.fix())
                    oddRouteRects.append(routeRect)
        # Route odd SD bar
        if len(oddRouteRects):
            barLeft = oddRouteRects[0].getLeft()
            if (numSDContacts % 2 == 0) and (topo.diffRightStyle != "ContactEdge"):
                barRight = sdDiffRectBox.getRight()
            else:
                barRight = oddRouteRects[-1].getRight()
            oddSDBarBox = Box(barLeft, oddSDBarEdge, barRight, oddSDBarFarEdge).fix()
            oddSDBar = Rect(metal1Layer, oddSDBarBox)
        else:
            oddSDBar = None

        # Assign source and drain bars
        if topoLargeDrn:
            layout.srcBar = oddSDBar
            layout.drnBar = evenSDBar
        else:
            layout.srcBar = evenSDBar
            layout.drnBar = oddSDBar

    ####################################################################
    def routeGate(self):
        """
Route Gate fingers
        """
        topo = self.topo
        rules = self.rules
        layout = self.layout
        layers = self.layers
        polyLayer = layers.poly
        metal1Layer = layers.metal1
        
        # Top and bottom Gate routing contact
        layout.topGateContact = layout.bottomGateContact = None

        # Route top and bottom pins of gate fingers?
        routeGateTop = routeGateBottom = False
        # Extend top and bottom gate pins to top and bottom gate bars?
        extendGateTopPin = extendGateBottomPin = False
        topoRouteGate = topo.routeGate
        if topoRouteGate == "Both":
            routeGateTop = routeGateBottom = True
        elif topoRouteGate == "Top":
            routeGateTop = True
        elif topoRouteGate == "Bottom":
            routeGateBottom = True
        elif topoRouteGate != "None":
            raise RuntimeError("Invalid routeGate '%s'. Must be one of 'None', 'Top', 'Bottom', or 'Both'")

        # No gate routing
        if (routeGateTop is None) and (routeGateBottom is None):
            return

        # Find Gate route Poly vertical edges
        diffBottomEdge = 0
        diffTopEdge = topo.wf
        if topo.isDogbone:
            diffBottomEdge = topo.dogboneSDBottom
            diffTopEdge = topo.dogboneSDTop

        # Route poly can be spaced from channel diffussion or from SD metal bar
        polySpacingFromDiff = rules.polyClrDiff
        polySpacingFromMetal = rules.metal1Space + (rules.metal1ExtContact - rules.polyExtContact)

        # Gate bottom and top pin edges
        bottomPinEdge = -rules.polyExtDiff
        topPinEdge = topo.wf - bottomPinEdge

        # Nearest edge of top gate route
        if routeGateTop:
            topSDBarRange = topo.topSDBarRange
            if topSDBarRange:
                topPolyBarBottom = topSDBarRange.getRight() + polySpacingFromMetal
            else:
                topPolyBarBottom = diffTopEdge + polySpacingFromDiff
            routeTopPinRangeY = Range(topPinEdge, topPolyBarBottom)
            # Extend top gate pins to top gate bar?
            if routeTopPinRangeY.getWidth() > 0:
                extendGateTopPin = True

        # Nearest edge of bottom gate route
        if routeGateBottom:
            bottomSDBarRange = topo.bottomSDBarRange
            if bottomSDBarRange:
                bottomPolyBarTop = bottomSDBarRange.getRight() - polySpacingFromMetal
            else:
                bottomPolyBarTop = diffBottomEdge - polySpacingFromDiff
            routeBottomPinRangeY = Range(bottomPinEdge, bottomPolyBarTop)
            # Extend bottom gate pins to bottom gate bar?
            if routeBottomPinRangeY.getWidth() < 0:
                extendGateBottomPin = True
                routeBottomPinRangeY.fix()

        # Route fingers
        gates = layout.gates
        routeGateTopBox = Box()
        routeGateBottomBox = Box()
        numFingers = topo.fr
        for i in xrange(numFingers):
            gate = gates[i]
            channelBox = gate.getComp(0).getBBox()
            if extendGateTopPin:
                routeGateTopBox.set(channelBox)
                routeGateTopBox.setRangeY(routeTopPinRangeY)
                Rect(polyLayer, routeGateTopBox)
            if extendGateBottomPin:
                routeGateBottomBox.set(channelBox)
                routeGateBottomBox.setRangeY(routeBottomPinRangeY)
                Rect(polyLayer, routeGateBottomBox)

        # Create poly metal Contact
        gateBarLeft = gates[0].getComp(0).getBBox().getLeft()
        gateBarRight = channelBox.getRight()
        gateBarWidth = rules.minWidthPolyEncContact
        
        # Top gate routing contact bar
        if routeGateTop:
            box = Box(gateBarLeft, topPolyBarBottom, gateBarRight,
                    topPolyBarBottom + gateBarWidth)
            layout.topGateContact = GateContact(self, box)

        # Bottom gate routing contact bar
        if routeGateBottom:
            box = Box(gateBarLeft, bottomPolyBarTop, gateBarRight,
                    bottomPolyBarTop - gateBarWidth)
            layout.bottomGateContact = GateContact(self, box)

    ####################################################################
    def genSharedLayers(self):
        """
Generate shared layers such as implant, well.
        """

        topo = self.topo
        layers = self.layers
        rules = self.rules
        layout = self.layout
        diffLeftStyle = topo.diffLeftStyle
        diffRightStyle = topo.diffRightStyle
        ContactEdge = "ContactEdge"

        # Create implant box
        diffLayer = layers.diffusion
        diffBox = self.getBBox(diffLayer)
        diffExtByImpBox = Box(diffBox)
        implantExtDiff = rules.implantExtDiff

        # Align implant to abutting diffusion.
        diffExtByImpBox.expand(NORTH_SOUTH, implantExtDiff)
        if diffLeftStyle == ContactEdge:
            diffExtByImpBox.expand(WEST, implantExtDiff)
        if diffRightStyle == ContactEdge:
            diffExtByImpBox.expand(EAST, implantExtDiff)
        # Or use code below to get uniform implant extension
        #diffExtByImpBox.expand(implantExtDiff)

        polyLayer = layers.poly
        polyExtByImpBox = self.getBBox(polyLayer)
        polyExtByImpBox.expand(NORTH_SOUTH, rules.implantExtPoly)
        implantBox = Box(diffExtByImpBox).merge(polyExtByImpBox)

        # Align implant with tapImplant
        leftTap = layout.leftTap
        if leftTap:
            implantBox.setLeft(leftTap.implantRect.getRight())
        rightTap = layout.rightTap
        if rightTap:
            implantBox.setRight(rightTap.implantRect.getLeft())
        Rect(layers.implant, implantBox)

        # Create well box
        wellLayer = layers.well
        if wellLayer:
            maskGrid = self.maskGrid
            diffExtByWellBox = Box(diffBox)
            wellExtDiff = rules.wellExtDiff
            diffExtByWellBox.expand(NORTH_SOUTH, wellExtDiff)
            diffExtByWellHeight = diffExtByWellBox.getHeight()
            wellMinWidth = rules.wellMinWidth
            if diffExtByWellHeight < wellMinWidth:
                diffExtByWellBox.expand(NORTH_SOUTH, maskGrid.snap(0.5*(wellMinWidth-diffExtByWellHeight)))

            # Align well to abutting diffusion.
            if diffLeftStyle == ContactEdge:
                diffExtByWellBox.expand(WEST, wellExtDiff)
            if diffRightStyle == ContactEdge:
                diffExtByWellBox.expand(EAST, wellExtDiff)
                if diffLeftStyle == ContactEdge:
                # Satisfy min well width for non abutting left and right sides
                    diffExtByWellWidth = diffExtByWellBox.getWidth()
                    if diffExtByWellWidth < wellMinWidth:
                        diffExtByWellBox.expand(EAST_WEST, maskGrid.snap(0.5*(wellMinWidth-diffExtByWellWidth)))
            # Or use code below to get uniform well extension
            # diffExtByWellBox.expand(EAST_WEST, wellExtDiff)

            Rect(wellLayer, diffExtByWellBox)

    ####################################################################
    def genConnectivity(self):
        """
Generate connectivity info.
        """
        topo = self.topo
        layout = self.layout
        numFingers = topo.fr

        # Prepare connectivity
        self.connectivity = connectivity = Dictionary()
        connectivity.termD = termD = Term("D")
        connectivity.termS = termS = Term("S")
        connectivity.termG = termG = Term("G")
        connectivity.termB = termB = Term("B")

        # Create Gate pins
        topGateContact = layout.topGateContact
        bottomGateContact = layout.bottomGateContact
        if bottomGateContact:
            Pin("G_B", "G", bottomGateContact.metal1Rect)
        if topGateContact:
            Pin("G_T", "G", topGateContact.metal1Rect)
        CCgetComp = CompoundComponent.getComp
        if not (topGateContact or bottomGateContact):
            gates = layout.gates
            gate0 = gates[0]
            Pin("G_B", "G", CCgetComp(gate0, 1))
            Pin("G_T", "G", CCgetComp(gate0, 2))
            for i in xrange(1, numFingers):
                gate = gates[i]
                termName = "G_%d" % i
                Pin("G_%d_B"%i, termName, CCgetComp(gate, 1)).getTerm().setMustJoin(termG)
                Pin("G_%d_T"%i, termName, CCgetComp(gate, 2))

        sdContacts = layout.sdContacts
        numSDContacts = numFingers + 1
        # Create Source pins
        srcBar = layout.srcBar
        if srcBar:
            Pin("S", "S", srcBar)
        else:
            startIndex = 1 if topo.largeDrn else 0
            pinIndex = 0
            for i in xrange(startIndex, numSDContacts, 2):
                sdContact = sdContacts[i]
                pinShape = sdContact.metal1Rect
                if not pinShape:
                    pinShape = sdContact.diffRect
                termName = "S_%d" % pinIndex if pinIndex else "S"
                pin = Pin(termName, termName, pinShape)
                if pinIndex:
                    pin.getTerm().setMustJoin(termS)
                pinIndex += 1

        # Create Drain pins
        drnBar = layout.drnBar
        if drnBar:
            Pin("D", "D", drnBar)
        else:
            startIndex = 0 if topo.largeDrn else 1
            pinIndex = 0
            for i in xrange(startIndex, numSDContacts, 2):
                sdContact = sdContacts[i]
                pinShape = sdContact.metal1Rect
                if not pinShape:
                    pinShape = sdContact.diffRect
                termName = "D_%d" % pinIndex if pinIndex else "D"
                pin = Pin(termName, termName, pinShape)
                if pinIndex:
                    pin.getTerm().setMustJoin(termD)
                pinIndex += 1
        # Create Bulk pins


########################################################################
class FastPmos(FastMosfetTemplate):
    """
Fast Pmos class.
    """
    tranType   = "pmos"
    oxide      = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "PIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        active       = ( "PACT",    "drawing"),
        tapDiffusion = ( "NTAP",    "drawing"),
        tapImplant   = ( "NIMP",    "drawing"),
        well         = ( "NWELL",   "drawing"),
    )

########################################################################
class FastNmos(FastMosfetTemplate):
    """
Fast Nmos class.
    """
    tranType   = "nmos"
    oxide      = "thin"

    layerMapping = dict(
        contact      = ( "CO", "drawing"),
        diffusion    = ( "DIFF",    "drawing"),
        implant      = ( "NIMP",    "drawing"),
        metal1       = ( "M1",  "drawing"),
        poly         = ( "PO",   "drawing"),
        active       = ( "NACT",    "drawing"),
        tapDiffusion = ( "PTAP",    "drawing"),
        tapImplant   = ( "PIMP",    "drawing"),
        well         = None,
    )

########################################################################
def definePcells( lib):
    """
Define the cells to be created in the OpenAccess library.
    """
    cells = [
        [FastPmos,        "FastPmos"],
        [FastNmos,        "FastNmos"],
    ]
    for cell in cells:
        lib.definePcell( cell[0], cell[1])
