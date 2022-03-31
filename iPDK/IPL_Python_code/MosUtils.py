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
# MosUtils.py                                                          #
#                                                                      #
########################################################################
"""Module: MosUtils

This module implements a utility classes for creating stacked
MOS transistors.

MosUtil classes are building blocks which can be used for creating
MOS device PyCells, or groups of devices as used in standard
cells.

Class Hierarchy
-----------------------------------------------------------------------
def calculateDeviceParameter
def flattenGrouping
def getComp
def getCompsSorted
def getDesignRule
def ggPlace
def orderedRuleset
def rulesmgr
def stack
def trim

class BorrowGrouping
    def __init__
    def add
    def remove
    def ungroup

class EnclosingRectangles
    def ungroupAsList

    class EnclosingRects
        def __init__

    class EnclosingRectsAbut
        def __init__

    class EnclosingRectsBBox
        def __init__

class LayerDict

class MosGrid

class Pattern
    def all
    def even
    def diffPairContact
    def diffPairGate
    def odd
    def repeat

class MosCC
    def __init__
    def clone
    def getComp
    def getCompsSorted
    def ggPlace

    class ContactCC
        def __init__
        def construct
        def construct1
        def construct2
        def getDesignRules
        def setPin

    class MosContact
        def construct
        def edgeExtend
        def getViaLayer
        def justify
        def locate
        def makeLowerRect
        def setPin

        class ContactGate
            def makeLowerRect
            def updateRules

            class ContactGate1
                implement = "construct1"
                def __init__

            class ContactGate2
                implement = "construct2"
                def __init__

            class ContactGate4
                implement = "construct2"
                def __init__

        class ViaX
            def makeLowerRect
            def updateRules

            class ViaX1
                implement = "construct1"
                def __init__

            class ViaX2
                implement = "construct2"
                def __init__

            class ViaX4
                implement = "construct2"
                def __init__

        class ContactCenter
            def makeLowerRect
            def updateRules

            class ContactCenter1
                implement  = "construct1"
                isAbutable = False
                def __init__

            class ContactCenter2
                implement  = "construct2"
                isAbutable = False
                def __init__

            class ContactCenter4
                implement  = "construct2"
                isAbutable = False
                def __init__

        class ContactEdge
            def makeLowerRect
            def updateRules

            class ContactEdge1
                implement  = "construct1"
                isAbutable = False
                def __init__

                class ContactEdgeAbut1
                    isAbutable = True

            class ContactEdge2
                implement  = "construct2"
                isAbutable = False
                def __init__

                class ContactEdgeAbut2
                    isAbutable = True

            class ContactEdge4
                implement  = "construct2"
                isAbutable = False
                def __init__

                class ContactEdgeAbut4
                    isAbutable = True

        class ContactSubstrate
            def makeLowerRect
            def updateRules

            class ContactSubstrate1
                implement  = "construct1"
                isAbutable = False
                def __init__

            class ContactSubstrate2
                implement  = "construct2"
                isAbutable = False
                def __init__

            class ContactSubstrate4
                implement  = "construct2"
                isAbutable = False
                def __init__

    class ContactSubstrateAbut
        def __init__
        def checkEdge
        def constructAbuttingContacts
        def makeContact
        def matchEdge

    class MosGate
        def __init__
        def construct
        def setPin
        def updateRules

    class MosDiffusion
        def __init__
        def setPin

        class DiffAbut
            isAbutable = True
            def construct

        class DiffCenter
            isAbutable = False
            def construct

        class DiffEdge
            isAbutable = False
            def construct

            class DiffEdgeAbut
                isAbutable = True

        class DiffHalf
            isAbutable = True
            def construct

        class DiffHalf2
            isAbutable = True
            def construct

    class MosBody
        def addDiffConn
        def addGateConn
        def alignDogboneContacts
        def justifyDiffContacts
        def unwire
        def wireDiffConn
        def wireGateConn

        class MosBody1
            def __init__
            def changeEndStyle

        class MosBody2
            def __init__

        class MosDummy
            def setPin
            def tieOff

            class MosDummy1

            class MosDummy2

    class MosStack1

    class MosStack2

class GuardRing



Class Descriptions
-----------------------------------------------------------------------
BorrowGrouping
    Specialized Grouping which does not allow modification of member
    PhysicalComponents, such as moving.  Use paradigm is a temporary
    reference Grouping.  For example, used as refComp for fgPlace().

EnclosingRectangles
    Parent class for creating enclosing rectangles.

EnclosingRects
    Create enclosing rectangles, based on fgAddEnclosingRects().

EnclosingRectsAbut
    Create enclosing rectangles.  Trim left and right for abutment.
    comps must be members of DloGen.

EnclosingRectsBBox
    Add enclosing rectangles, based on bounding box.
    comps must be members of DloGen.

GuardRing
    Custom guard ring, which can result in smaller area than ContactRing
    in some situations, because of more sophisticated, but
    compute-intensive, well calculation.

LayerDict
    Dictionary of Layer objects.  None is a valid value for a key.

MosGrid
    A set of methods for snapping numbers to resolution.

Pattern
    A set of methods for generating patterns useful in wiring Mosfets
    in configurations such as a differential pair.



MosCC
    Parent class for all CompoundComponent derived classes.
    Manages instance attributes for technology.

ContactCC
    Parent class for a single column Contact.

MosContact
    Device contact consisting of a lower level rectangle, such
    as diffusion or poly layer, and a composite contact object,
    either a CompoundComponent or PyCell.

ContactGate
    Parent class for gate contacts.  Consists of contact composite
    object and poly rectangle.  Contacts are arranged in a single
    row.

    width is size of lower level rectangle.  coverage determines how
    much of poly rectangle is covered with contacts.

ContactGate1
    Create a ContactGate using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.

ContactGate2
    Create a ContactGate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on left and right offsets.

ContactGate4
    Create a ContactGate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.

ViaX
    Parent class for a metal via.  Consists of via composite object
    and a metal rectangle.  Contacts are arranged in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.

ViaX1
    Create a ViaX using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.

ViaX2
    Create a ViaX using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.

ViaX4
    Create a ViaX using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.

ContactCenter
    Parent class for center source/drain diffusion contact.  Consists
    of a composite contact object and a diffusion rectangle.  Contacts
    are arranged in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.

ContactCenter1
    Create a ContactCenter using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.

ContactCenter2
    Create a ContactCenter using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.

ContactCenter4
    Create a ContactCenter using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.

ContactEdge
    Parent class for right/left edge source/drain diffusion contact.
    Consists of contact composite object and a diffusion rectangle.
    Contacts are arranged in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.

ContactEdge1
    Create a ContactEdge using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.

ContactEdgeAbut1
    Creates same layout as ContactEdge1, but is tagged as isAbutable.

ContactEdge2
    Create a ContactEdge using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.

ContactEdgeAbut2
    Creates same layout as ContactEdge2, but is tagged as isAbutable.

ContactEdge4
    Create a ContactEdge using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.

ContactEdgeAbut4
    Creates same layout as ContactEdge4, but is tagged as isAbutable.

ContactSubstrate
    Parent class for a substrate contact.  Consists of contact
    composite object and a diffusion rectangle.  Contacts are arranged
    in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.

ContactSubstrate1
    Create a ContactSubstrate using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.

ContactSubstrate2
    Create a ContactSubstrate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.

ContactSubstrate4
    Create a ContactSubstrate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.



MosGate
    Transistor gate poly and underlying channel diffusion.



MosDiffusion
    Parent class for source/drain diffusion consisting of a single
    diffusion rectangle.

DiffAbut
    Sliver of source/drain diffusion, needed for auto-abutment with
    contact.

DiffCenter
    Center source/drain diffusion, defined by gate-to-gate spacing.

DiffEdge
    Minimum right/left source/drain diffusion width.

DiffEdgeAbut
    Creates same layout as DiffEdge, but is tagged as isAbutable.

DiffHalf
    Half width of center source/drain diffusion, DiffCenter, as
    needed for auto-abutment without contact.

DiffHalf2
    Diffusion with size of half width of ContactCenter, as
    needed for auto-abutment without contact, and alignment with
    fingers that have center contact.



MosBody
    Parent class for MOS transistor.

MosBody1
    MOS transistor with contact coverage parameter.

    Build a stack of MOS transistors.  Options:
    * Connect gates with a poly contact,
    * Connect source/drain contacts.
    * Wire width for connecting source/drain.
    * Source/drain contact coverage.

MosBody2
    MOS transistor with contact offset parameters.

MosStack1
    Build a stack of MOS transistors based on a symbolMap, which
    defines a mapping of building blocks. and a sequence, which
    defines the placement order.

MosStack2
    Build a stack of MOS transistors based on a symbolMap, which
    defines a mapping of building blocks. and a sequence, which
    defines the placement order.

    Differs from MosStack1 by *not* cloning leftmost and rightmost
    element, for increased efficiency.



MosStackBase
    Lowest level class for building MOS stacks.

MosStack
    Create a sequence of MosSD and MosGate objects to implement a
    stack of transistors.

MosStackSequence
    Simplified version of MosStack, which presumes same coverage
    and justification for all source/drain contacts.  Option
    string sequence to selectively choose center contacts.

MosStackSimple
    Simplified version of MosStack, which presumes same coverage
    and justification for all source/drain contacts.  Option to
    enable/disable all center contacts.



Module dependencies:
    - cni.dlo            Ciranova PyCell APIs.
    - cni.integ.common   Ciranova integration APIs.
    - copy               Python copy
    """
from __future__ import with_statement

__version__  = "$Revision: #1 $"
__fileinfo__ = "$Id: //depot/deviceKits_4.2.5/baseKit/MosUtils.py#1 $"
__author__   = "Lyndon C. Lim"

########################################################################
#                                                                      #
# Packages                                                             #
#                                                                      #
########################################################################

from cni.dlo import (
    AbutContact,
    Bar,
    Box,
    CompoundComponent,
    Contact,
    DeviceContext,
    DeviceContextManager,
    Direction,
    DloGen,
    Grid,
    Grouping,
    Instance,
    Layer,
    LayerMaterial,
    Location,
    ParamArray,
    Path,
    PhysicalComponent,
    Pin,
    Point,
    Rect,
    RouteTarget,
    Ruleset,
    RulesetManager,
    ShapeFilter,
    SnapType,
    Term,
    Unique,
    ulist,
)

from cni.utils import (
    getMinExtensions
)

from cni.integ.common import (
    Compare,
    Dictionary,
    isEven,
    isOdd,
    renameParams,
)

import copy
import math

SCRATCHPAD = ( -5, -5)

########################################################################
#                                                                      #
# Utility Classes and Methods                                          #
#                                                                      #
########################################################################

def calculateDeviceParameter(
    tech,
    transistorType,
    oxideType,
    dimension,
    layers,
    ruleset         = None,
    deviceContext   = None):
    """Calculate transistor parameters for range checking, such as
    minimum width or length.  When dogbone transistors are not
    supported, the device minimums may not be the process minimum.
        """
    layer = Dictionary()

    for l in layers:
        if l.getMaterial() == LayerMaterial.POLY:
            layer.poly = l
        elif l.getMaterial() in ( LayerMaterial.DIFF, LayerMaterial.PDIFF, LayerMaterial.NDIFF):
            layer.diff = l
        elif l.getMaterial() == LayerMaterial.CUT:
            layer.contact = l
        else:
            raise ValueError, "Wrong layer argument - %s" % l



    with rulesmgr( tech, Ruleset, ruleset):
        with rulesmgr( tech, DeviceContext, deviceContext):

            if dimension in ( "minLength", "minWidth", "maxLength", "maxWidth"):
                value = tech.getMosfetParams( transistorType, oxideType, dimension)
            else:
                raise ValueError, "Unrecognized dimension - %s." % dimension



            if dimension == "minLength":
                if tech.physicalRuleExists( "minWidth", layer.poly):
                    value2 = tech.getPhysicalRule( "minWidth", layer.poly)
                else:
                    value2 = -1

                value = max( value, value2)
                if value < 0:
                    raise ValueError, "Unable to calculate %s dimension." % dimension

            elif dimension == "minWidth":
                if tech.physicalRuleExists( "minWidth", layer.contact) and \
                   ( tech.physicalRuleExists( "minExtension",     layer.diff, layer.contact) or \
                     tech.physicalRuleExists( "minDualExtension", layer.diff, layer.contact)    ):
                    values = getMinExtensions( tech, layer.diff, layer.contact)
                    values = [ v for v in values if v ]
                    val2 = tech.getPhysicalRule( "minWidth", layer.contact) + 2.0 * max( values)

                    value = max( value, val2)
                    if value < 0:
                        raise ValueError, "Unable to calculate %s dimension." % dimension

            elif dimension in ( "maxLength", "maxWidth"):
                if value < 0:
                    raise ValueError, "Unable to calculate %s dimension." % dimension

    return( value)

####################################################################

def flattenGrouping(
    grouping,
    newOwner):
    """Recursively flatten a lower levels of a Grouping.  The ungrouped
    members are assigned to newOwner.
        """
    groupings = [ comp for comp in grouping.getComps() if isinstance( comp, Grouping)]

    for g in groupings:
        flattenGrouping( g, newOwner)
        g.ungroup()

####################################################################

def getComp(
    comp,
    objType):
    """Return any component of matching type.
        """
    # Considered using instance attribute to store members during
    #     creation, but clone() would incorrectly point to members
    #     of original.
    for c in comp.getComps():
        if isinstance( c, objType):
            return( c)
    return( None)

####################################################################

def getCompsSorted(
    comp,
    objType      = None,
    layer        = None,
    sortFunction = None,
    negated      = False):
    """Return sorted and filtered list of member components.
    Default is by x-coordinate, left to right.
        """
    # Considered using instance attribute to store members during
    #     creation, but clone() would incorrectly point to members
    #     of original.
    comps = comp.getComps()

    if objType:
        comps = [ x for x in comps if isinstance(x, objType)]

    if layer:
        filter = ShapeFilter(layer)
        comps = [ x for x in comps if not x.getBBox( filter).isInverted()]

    if negated:
        notComps = comps
        comps = [ x for x in self.getComps() if not x in notComps]

    if not sortFunction:
        sortFunction = Compare.cmpCenterXAscend

    comps.sort( sortFunction)

    return( comps)

########################################################################

def getDesignRule( tech, *args, **kwargs):
    """Return design rule value.  Optional default value if no rule
    is defined.
        """
    defaultValue = kwargs.pop( "defaultValue", 0)
    if tech.physicalRuleExists( *args, **kwargs):
        return( tech.getPhysicalRule( *args, **kwargs))
    else:
        return( defaultValue)

########################################################################

def ggPlace(
    *args,
    **kwargs):
    """Place instance with fgPlace(), then snap results to grid.
        """
    if "Direction" in kwargs:
        direction = kwargs[ "Direction"]
    else:
        direction = args[1]

    if "grid" in kwargs:
        grid = kwargs.pop( "grid")
    else:
        grid = Grid( DloGen.currentDloGen().tech.getGridResolution())

    comp = args[0]
    args = args[1:]
    comp.fgPlace( *args, **kwargs)

    comp.snapTowards( grid, direction)

    return( comp)

########################################################################

def orderedRuleset(
    tech,
    rulesets):
    """Return name of first ruleset in an ordered list which exists
    in the technology file.
        """
    techRulesets = [ ruleset.name for ruleset in tech.getRulesets()]

    for name in rulesets:
        if name in techRulesets:
            return( name)

    raise ValueError, "No supported ruleset found."

########################################################################

class NoManager( object):
    """An empty class which acts as a stub when no valid Ruleset or
    DeviceContext is found in the technology file.
        """
    def __enter__( self):
        pass

    def __exit__( self, unknown1, unknown2, unknown3):
        pass

def rulesmgr(
    tech,
    context,
    namesGiven):
    """Return first ruleset or device context found which exists in the
    technology file.
        """
    search = {
        Ruleset       : ("getRulesets",       RulesetManager      ),
        DeviceContext : ("getDeviceContexts", DeviceContextManager),
    }

    mgr = NoManager()

    if namesGiven:
        if not isinstance( namesGiven, list):
            namesGiven = [ namesGiven]

        # Find the matching ruleset or device context.
        namesFound = [ item.name for item in getattr( tech, search[ context][0])()]
        for name in namesGiven:
            if name in namesFound:
                mgr = search[ context][1]( tech, name)
                break

        if context == Ruleset:
            # Valid condition to request a ruleset which does not exist.
            pass
        elif context == DeviceContext:
            # Error condition to request a device context which does not exist.
            if isinstance( mgr, NoManager):
                raise ValueError, "No valid device context - %s" % namesGiven
        else:
            raise ValueError, "Illegal technology context - %s" % context

    return( mgr)

########################################################################

def stack( comps, env, grid):
    """Place components according to design rule information.
    Management of process rules separated from code and design.
        """
    ref = comps[0]
    for comp in comps[1:]:
        ggPlace( comp, Direction.EAST, ref, env=env, align=False, grid=grid)
        ref = comp

########################################################################

def trim( diffRect, polyShapes):
    """Adjust left/right side of diffusion to minimum dimensions.
        """
    # Sort, rightmost position is first
    polyShapes.sort( Compare.cmpCenterXDescend)

    # Adjust rightmost edge of diffusion rectangle.
    box = diffRect.getBBox()
    box.setRight( polyShapes[0].getBBox().getLeft())

    # Adjust leftmost edge of diffusion rectangle.
    if len( polyShapes) == 2:
        box.setLeft( polyShapes[1].getBBox().getRight())

    diffRect.setBBox( box)
    return( diffRect)

########################################################################

class BorrowGrouping( Grouping):
    """Specialized Grouping which does not allow modification of member
    PhysicalComponents, such as moving.  Use paradigm is a temporary
    reference Grouping.  For example, used as refComp for fgPlace().
        """

    ####################################################################

    def __init__(
        self,
        *args,
        **kwargs):

        if "components" in kwargs:
            components = kwargs["components"]
        else:
            components = ulist[PhysicalComponent]()
        kwargs["components"] = None

        super( BorrowGrouping, self).__init__( *args, **kwargs)

        self.i = 0
        self.owner = []
        self.comps = ulist[ PhysicalComponent]()

        self.add( components)

    ####################################################################

    def add(
        self,
        components):
        """Add member component to BorrowGrouping, keeping track of
        original owner.
            """
        if isinstance( components, PhysicalComponent):
            components = [ components]
        elif not isinstance( components, list):
            raise TypeError, "Unsupported type for components."

        for comp in components:
            self.i += 1
            owner = comp.getCompOwner()

            if isinstance( owner, CompoundComponent):
                wasLocked = owner.isLocked()
                if wasLocked:
                    owner.unlock()

                owner.remove( comp)

                if wasLocked:
                    owner.lock()
            elif isinstance( owner, Grouping):
                owner.remove( comp)
            super( BorrowGrouping, self).add( comp)

            self.owner.append( owner)
            self.comps.append( comp )

    ####################################################################

    def remove(
        self,
        components):
        """Return member component of BorrowGrouping to original owner.
            """
        if isinstance( components, PhysicalComponent):
            components = [ components]
        elif not isinstance( components, ulist[PhysicalComponent]):
            raise TypeError, "Unsupported type for components."

        deleted = []
        for comp in components:
            if comp in self.comps:
                super( BorrowGrouping, self).remove( comp)

                j = self.comps.index( comp)
                if isinstance( self.owner[ j], CompoundComponent):
                    wasLocked = self.owner[ j].isLocked()
                    if wasLocked:
                        self.owner[ j].unlock()

                    self.owner[ j].add( comp)

                    if wasLocked:
                        self.owner[ j].lock()
                elif isinstance( self.owner[ j], Grouping):
                    self.owner[ j].add( comp)

                deleted.append( j)
                self.i -= 1

        deleted.reverse()
        for j in deleted:
            del self.owner[ j]
            del self.comps[ j]

    ####################################################################

    def ungroup(
        self):
        self.remove( self.comps)

        if self.getComps():
            raise IndexError, "Components remain in BorrowGrouping."

        super( BorrowGrouping, self).ungroup()

    ####################################################################

    def destroy(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def mirrorX(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def mirrorY(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def moveBy(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def moveTo(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def moveTowards(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def rotate180(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def rotate270(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def rotate90(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def transform(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def makeArray(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def snap(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def snapTowards(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def snapX(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

    def snapY(*args, **kwargs):
        raise NotImplementedError, "BorrowGrouping does not support this method."

########################################################################

class EnclosingRectangles( Grouping):
    """Parent class for creating enclosing rectangles.
        """

    ####################################################################

    def ungroupAsList(
        self):
        """Ungroup.  Return results as list.
            """
        members = self.getComps()
        self.ungroup()
        return( members)

########################################################################

class EnclosingRects( EnclosingRectangles):
    """Create enclosing rectangles, based on fgAddEnclosingRects.
        """

    ####################################################################

    def __init__(
        self,
        *args,
        **kwargs):
        """Create enclosing rectangles with fgAddEnclosingRects(), then
        snap results to grid.
            """
        if "grid" in kwargs:
            grid = kwargs.pop( "grid")
        else:
            grid = Grid( DloGen.currentDloGen().tech.getGridResolution())

        comp   = args[0]
        args   = args[1:]
        result = comp.fgAddEnclosingRects( *args, **kwargs)

        for rect in result.getComps():
            box = rect.getBBox()
            rect.setBBox(
                Box(
                    box.lowerLeft().snapTowards(  grid, Direction.SOUTH_WEST),
                    box.upperRight().snapTowards( grid, Direction.NORTH_EAST),
                )
            )

        super( EnclosingRects, self).__init__()
        result.ungroup( owner=self)

########################################################################

class EnclosingRectsAbut( EnclosingRectangles):
    """Create enclosing rectangles.  Trim left and right for abutment.
    comps must include an instance of MosBody.
        """

    ####################################################################

    def __init__(
        self,
        comp,
        encLayers):

        # Create enclosing layers.
        rects  = EnclosingRects( comp, encLayers).ungroupAsList()

        row   = [ i for i in comp.getComps() if isinstance( i, MosBody)][0]
        comps = row.getCompsSorted( objType=( MosDiffusion, ContactEdge, MosDummy ))

        # Left edge adjustment for abutment.
        if comps[0].isAbutable:
            edge = comps[0].getBBox().getLeft()

            for rect in rects:
                box = rect.getBBox()
                box.setLeft( edge)
                rect.setBBox( box)

        # Right edge adjustment for abutment.
        if comps[-1].isAbutable:
            edge = comps[-1].getBBox().getRight()

            for rect in rects:
                box = rect.getBBox()
                box.setRight( edge)
                rect.setBBox( box)

        super( EnclosingRectsAbut, self).__init__()
        self.add( rects)

########################################################################

class EnclosingRectsBBox( EnclosingRectangles):
    """Add enclosing rectangles, based on bounding box.
    comps must be members of DloGen.
        """

    ####################################################################

    def __init__(
        self,
        comp,
        encLayers):

        # Create enclosing layers.
        box   = comp.getBBox()
        rects = []
        for layer in encLayers:
            rects.append( Rect( layer, box))

        super( EnclosingRectsBBox, self).__init__()
        self.add( rects)

########################################################################

class LayerDict( Dictionary):
    """Dictionary of Layer objects.  None is a valid value for a key.
        """

    ####################################################################

    def __init__(
        self,
        technology,
        layerMapping):

        super( LayerDict, self).__init__()

        for (key, value) in layerMapping.iteritems():
            if value:
                self[ key] = technology.getLayer( *value)
            else:
                self[ key] = value

########################################################################

class MosGrid( object):
    """A set of methods for snapping numbers to resolution.
        """

    ####################################################################

    @staticmethod
    def ceil(
        value,
        resolution):
        return( math.ceil( float( value) / float( resolution)) * float( resolution))

    ####################################################################

    @staticmethod
    def floor(
        value,
        resolution):
        return( math.floor( float( value) / float( resolution)) * float( resolution))

    ####################################################################

    @staticmethod
    def round(
        value,
        resolution):
        return( round( float( value) / float( resolution)) * float( resolution))

########################################################################

class Pattern( object):
    """A set of methods for generating patterns useful in wiring Mosfets
    in configurations such as a differential pair.
        """

    ####################################################################

    @staticmethod
    def all(
        limit):
        """Return list integers, 0 <= i < limit.
            """
        return( range( 0, limit))

    ####################################################################

    @staticmethod
    def even(
        limit):
        """Return list of even-valued integers, 0 <= i < limit.
            """
        return( range( 0, limit, 2))

    ####################################################################

    @staticmethod
    def diffPairContact(
        fingersPerRow):
        """Return a dictionary of lists.  Each list is a sequence
        describing how contacts are assigned for each device in a
        differential pair.
            """
        pattern = Dictionary(
            c0 = [],    # Contact for device0
            c1 = [],    # Contact for device1
            c2 = [],    # Contact for shared node
            c  = [],    # All contacts
        )
        contacts = (2 * fingersPerRow) + 1



        # Assignment for shared node
        if isEven( fingersPerRow):
            i = 0
        else:
            i = 1

        for x in range( i, contacts, 2):
            pattern.c2.append( x)



        # Assignment for device0 contact
        if isEven( fingersPerRow):
            i = 1
        else:
            i = 0

        for x in range( i, contacts, 4):
            pattern.c0.append( x)



        # Assignment for device1 contact
        if isEven( fingersPerRow):
            i = 3
        else:
            i = 2

        for x in range( i, contacts, 4):
            pattern.c1.append( x)



        # Summary pattern
        pattern.c.extend( [ 0 for i in range( contacts)])

        for i in pattern.c1:
            pattern.c[ i] = 1

        for i in pattern.c2:
            pattern.c[ i] = 2

        return( pattern)

    ####################################################################

    @staticmethod
    def diffPairGate(
        fingersPerRow):
        """Return a dictionary of lists.  Each list is a sequence
        describing how gates are assigned for each device in a
        differential pair.
            """
        pattern = Dictionary(
            g0 = [],    # Gates for device0
            g1 = [],    # Gates for device1
            g  = [],    # All gates
        )
        gates = 2 * fingersPerRow



        # Assignment for device0
        i  = 0
        pattern.g0.append( i)
        i  += 1

        if isEven( fingersPerRow):
            pattern.g0.append( i)
            i += 1

        i += 2
        for x in range( i, gates, 4):
            pattern.g0.extend( [x, x+1])



        # Assignment for device1
        i  = gates
        i  -= 1
        pattern.g1.append( i)

        if isEven( fingersPerRow):
            i -= 1
            pattern.g1.append( i)

        i -= 3
        for x in range( i, 0, -4):
            pattern.g1.extend( [x, x-1])
        pattern.g1.reverse()



        # Summary pattern
        pattern.g.extend( [ 0 for i in range( gates)])
        for i in pattern.g1:
            pattern.g[ i] = 1

        return( pattern)

    ####################################################################

    @staticmethod
    def odd(
        limit):
        """Return list of odd-valued integers, 0 <= i < limit.
            """
        return( range( 1, limit, 2))

    ####################################################################

    @staticmethod
    def repeat(
        subpattern,
        count):
        """Return list of repeating pattern.  list length = count.
            """
        length  = len( subpattern) - 1
        pattern = []

        i = 0
        j = 0
        while ( i < count):
            pattern.append( subpattern[ j])
            i += 1
            if j < length:
                j += 1
            else:
                j = 0

        return( pattern)

########################################################################

class RouteRect( Rect):
    """Create a connecting rectangle between 2 RouteTargets which are
    restricted to being single layer rectangles.  This class is not
    functionally equivalent to RoutePath.  RoutePath is more full
    featured, but resulted in a restriction that the RouteTarget width
    must be an even multiple of the layout grid.

    fromTarg bounding box sets the width of the rectangle.
        """

    ####################################################################

    def __init__(
        self,
        fromTarg,
        toTarg,
        layer,
        direction):
        """Create a connecting RouteRect.
            """
        fromTarg = RouteTarget( fromTarg)
        toTarg   = RouteTarget( toTarg  )
        filter   = ShapeFilter( layer   )

        if direction in ( Direction.NORTH, Direction.SOUTH):
            if direction == Direction.NORTH:
                ( lowerTarg, upperTarg) = ( fromTarg, toTarg)
            else:
                ( lowerTarg, upperTarg) = ( toTarg, fromTarg)

            bottomEdge = lowerTarg.getBBox( filter).getTop()
            topEdge    = upperTarg.getBBox( filter).getBottom()
            leftEdge   =  fromTarg.getBBox( filter).getLeft()
            rightEdge  =  fromTarg.getBBox( filter).getRight()

        elif direction in ( Direction.EAST, Direction.WEST):
            if direction == Direction.EAST:
                ( leftTarg, rightTarg) = ( fromTarg, toTarg)
            else:
                ( leftTarg, rightTarg) = ( toTarg, fromTarg)

            leftEdge   =  leftTarg.getBBox( filter).getRight()
            rightEdge  = rightTarg.getBBox( filter).getLeft()
            bottomEdge =  fromTarg.getBBox( filter).getTop()
            topEdge    =  fromTarg.getBBox( filter).getBottom()

        else:
            raise ValueError, "direction must be one of Direction.(North,South,East,West)"

        super( RouteRect, self).__init__( layer, Box( leftEdge, bottomEdge, rightEdge, topEdge))

########################################################################

class RulesDict( dict):
    """Class defines a dictionary for storing design rule information.
    The rules have an additional qualifier, direction, since the rules
    are specifically used to modify layout of MosUtils objects.

    Key format:
        ( ruleName, Layer, Layer, direction)

    Example keys:
        ( minSpacing,   Layer("metal1"), None, Direction.ANY)
        ( minExtension, Layer("metal1"), Layer("contact"), Direction.NORTH)
        ( minClearance, Layer("metal1", "drawing"), Layer("metal1", "drawing1"), Direction.ANY)

    Values are not restricted to single float values.
        """

    ####################################################################

    @staticmethod
    def makeKey(
        ruleName,
        layer1,
        layer2 = None,
        dir    = Direction.ANY):
        """Method to create a valid key for a Python dictionary key when
        some members are not immutable types.
            """
        if layer2:
            return(
                ( ruleName, layer1.getLayerName(), layer1.getPurposeName(), layer2.getLayerName(), layer2.getPurposeName(), dir)
            )
        else:
            return(
                ( ruleName, layer1.getLayerName(), layer1.getPurposeName(), None, None, dir)
            )

    ####################################################################

    def update(
        self,
        addRules):
        """Method updates values in a RulesDict object, based on another
        RulesDict object.  Some heuristics apply regarding when an update
        rule should be applied.

        Restriction:  Only updates rules whose value is a single float.
            """

        matchingDirections = {
            Direction.ANY         : ( Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST, Direction.NORTH_SOUTH, Direction.EAST_WEST, Direction.ANY),
            Direction.NORTH_SOUTH : ( Direction.NORTH, Direction.SOUTH, Direction.NORTH_SOUTH, ),
            Direction.EAST_WEST   : ( Direction.EAST,  Direction.WEST,  Direction.EAST_WEST,   ),
            Direction.NORTH       : ( Direction.NORTH, ),
            Direction.SOUTH       : ( Direction.SOUTH, ),
            Direction.EAST        : ( Direction.EAST,  ),
            Direction.WEST        : ( Direction.WEST,  ),
        }

        for key in addRules:
            subkey = key[ :-1]

            for direction in matchingDirections[ key[-1]]:
                newkey = subkey + ( direction,)
                if newkey in self:
                    self[ newkey] = self[ newkey] + addRules[ key]

    ####################################################################

    def __setitem__(
        self,
        key,
        value):
        """Redefine method to pre-process key since Layer() is not supported
        for keys in Python dictionaries.
            """
        if isinstance( key[1], Layer):
            key = RulesDict.makeKey( *key)
        return( super( RulesDict, self).__setitem__( key, value))

    ####################################################################

    def __getitem__(
        self,
        key):
        """Redefine method to pre-process key since Layer() is not supported
        for keys in Python dictionaries.
            """
        if isinstance( key[1], Layer):
            key = RulesDict.makeKey( *key)
        return( super( RulesDict, self).__getitem__( key))

    ####################################################################

    def get(
        self,
        key,
        default = None):
        """Redefine method to pre-process key since Layer() is not supported
        for keys in Python dictionaries.
            """
        if isinstance( key[1], Layer):
            key = RulesDict.makeKey( *key)
        return( super( RulesDict, self).get( key, default))

    ####################################################################

    def pop(
        self,
        key,
        default = None):
        """Redefine method to pre-process key since Layer() is not supported
        for keys in Python dictionaries.
            """
        if isinstance( key[1], Layer):
            key = RulesDict.makeKey( *key)
        return( super( RulesDict, self).pop( key, default))

    ####################################################################

    def setdefault(
        self,
        key,
        default = None):
        """Redefine method to pre-process key since Layer() is not supported
        for keys in Python dictionaries.
            """
        if isinstance( key[1], Layer):
            key = RulesDict.makeKey( *key)
        return( super( RulesDict, self).setdefault( key, default))

########################################################################
#                                                                      #
# Classes of Transistor Parts                                          #
#                                                                      #
########################################################################

class MosCC( CompoundComponent):
    """Parent class for other MosUtils CompoundComponents.
        """

    ####################################################################

    def __init__(
        self,
        params):
        """Manage instance attributes for technology.
            """
        super( MosCC, self).__init__( Unique.Name( "%s_" % self.__class__.__name__))
        self.tech   = self.getCompOwner().tech
        self.grid   = Grid( self.tech.getGridResolution(), snapType=SnapType.ROUND)

        del params["self"]
        self.params = Dictionary( **params)

    ####################################################################

    def clone(
        self,
        nameMap = '',
        netMap  = ''):
        """Copy physical shapes.  Copy instance attributes.
            """
        newSelf        = super( MosCC, self).clone( nameMap, netMap)
        newSelf.tech   = self.tech
        newSelf.grid   = self.grid

        if hasattr( self, "params"):
            newSelf.params = copy.copy( self.params)

        return( newSelf)

    ####################################################################

    def getComp(
        self,
        *args,
        **kwargs):
        """Return any component of matching type.
            """
        return( getComp( self, *args, **kwargs))

    ####################################################################

    def getCompsSorted(
        self,
        *args,
        **kwargs):
        """Return sorted and filtered list of member components.
            """
        return( getCompsSorted( self, *args, **kwargs))

    ####################################################################

    def ggPlace(
        self,
        *args,
        **kwargs):
        """Return sorted and filtered list of member components.
            """
        return( ggPlace( self, *args, **kwargs))

########################################################################

class ContactCC( MosCC):
    """Parent class for a single column Contact.
        """

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        viaLayer,
        width,
        implement,
        addRules = RulesDict()):
        """Create self.params instance attribute to store constructor
        arguments.  Create layout.
            """
        super( ContactCC, self).__init__( locals())

        self.getDesignRules()
        self.construct()
        self.lock()

    ####################################################################

    def construct(
        self):
        """Make the layout based on the requested implementation method.
            """
        getattr(self, self.params.implement)()

    ####################################################################

    def construct1(
        self):
        """Build single column contact, containing rectangles.
        Placement of cuts is minimally spaced,
            """
        rules = Dictionary()

        rules.viaWidth  = self.rules[ ( "minWidth",   self.params.viaLayer)]
        rules.viaSpace  = self.rules[ ( "minSpacing", self.params.viaLayer)]
        rules.viaPitch  = rules.viaWidth + rules.viaSpace

        rules.lowerEncN = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.NORTH)]
        rules.lowerEncS = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.SOUTH)]
        rules.lowerEncE = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.EAST) ]
        rules.lowerEncW = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.WEST) ]

        rules.upperEncN = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.NORTH)]
        rules.upperEncS = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.SOUTH)]
        rules.upperEncE = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.EAST) ]
        rules.upperEncW = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.WEST) ]



        size = self.params.width - ( rules.lowerEncS + rules.viaWidth + rules.lowerEncN)
        rows = self.tech.uu2dbu( size) / self.tech.uu2dbu( rules.viaPitch)

        # Create contacts.
        r0   = Rect( self.params.viaLayer, Box( 0, 0, rules.viaWidth, rules.viaWidth))
        self.add( r0)

        if rows > 0:
            g0   = r0.makeArray( rules.viaPitch, rules.viaPitch, rows, 1)
            cTop = g0.getBBox().getTop()

            r0.moveTo(
                Point( 0, cTop + rules.viaSpace),
                loc = Location.LOWER_LEFT,
            )
            g0.ungroup( owner=self)

        # Create lower layer rectangle.
        cTop = r0.getBBox().getTop()
        self.add(
            Rect(
                self.params.lowerLayer,
                Box(
                    -rules.lowerEncW, -rules.lowerEncS,
                    rules.viaWidth + rules.lowerEncE, cTop + rules.lowerEncN,
                ),
            )
        )

        # Create upper layer rectangle
        self.add(
            Rect( self.params.upperLayer,
                Box(
                    -rules.upperEncW, -rules.upperEncS,
                    rules.viaWidth + rules.upperEncE, cTop + rules.upperEncN,
                ),
            )
        )

    ####################################################################

    def construct2(
        self):
        """Build single column contact, containing rectangles.
        Placement of cuts is equally spaced,
            """
        rules = Dictionary()

        rules.viaWidth = self.rules[ ( "minWidth",   self.params.viaLayer)]
        rules.viaSpace = self.rules[ ( "minSpacing", self.params.viaLayer)]
        rules.viaPitch = rules.viaWidth + rules.viaSpace

        rules.lowerEncN = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.NORTH)]
        rules.lowerEncS = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.SOUTH)]
        rules.lowerEncE = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.EAST) ]
        rules.lowerEncW = self.rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.WEST) ]

        rules.upperEncN = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.NORTH)]
        rules.upperEncS = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.SOUTH)]
        rules.upperEncE = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.EAST) ]
        rules.upperEncW = self.rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.WEST) ]



        # Construction algorithm designed to place topmost cut aligned
        # with top of overlap layers.
        #
        # Do not try to optimize to be like construct1 algorithm.

        # Minimum acceptable height fits one contact.
        lowerTop = max( -rules.lowerEncS + self.params.width, rules.viaWidth + rules.lowerEncN)

        # Convert calculations to integer to avoid floating point
        # rounding errors.
        width      = self.tech.uu2dbu( self.params.width  )
        height     = self.tech.uu2dbu( rules.lowerEncS + rules.viaWidth + rules.lowerEncN)
        pitch      = self.tech.uu2dbu( rules.viaPitch)
        grid       = self.tech.uu2dbu( self.grid.getSize())

        size       = width - height
        rows       = size / pitch

        # Create contacts.
        r0    = Rect( self.params.viaLayer, Box( 0, 0, rules.viaWidth, rules.viaWidth))
        self.add( r0)

        if rows > 0:
            pitch = (( size / rows) / grid) * grid
            rows  = size / pitch
            pitch = self.tech.dbu2uu( pitch)
            g0    = r0.makeArray( pitch, pitch, rows, 1)

            r0.moveTo(
                Point( 0, lowerTop - rules.lowerEncN),
                loc = Location.UPPER_LEFT,
            )
            g0.ungroup( owner=self)

        # Create lower layer rectangle.
        self.add(
            Rect( self.params.lowerLayer,
                Box(
                    -rules.lowerEncW, -rules.lowerEncS,
                    rules.viaWidth + rules.lowerEncE, lowerTop,
                )
            )
        )

        # Create upper layer rectangle
        self.add(
            Rect( self.params.upperLayer,
                Box(
                    -rules.upperEncW, -rules.upperEncS,
                    rules.viaWidth + rules.upperEncE, lowerTop - rules.lowerEncN + rules.upperEncN
                )
            )
        )

    ####################################################################

    def getDesignRules(
        self):
        """Get design rule information.  Could be overridden to
        use traditional technology file query.
            """
        contact = Contact(
            self.params.lowerLayer,
            self.params.upperLayer,
            None,
            routeDir1 = Direction.NORTH_SOUTH,
            routeDir2 = Direction.NORTH_SOUTH,
        )
        contact.moveTo( Point(0,0), loc=Location.LOWER_LEFT, filter=ShapeFilter( self.params.lowerLayer))



        # Get design rule information.  This is more complex than directly
        # querying the rule, but more immune to changes in rules syntax.
        viaFilter = ShapeFilter( self.params.viaLayer)
        viaBox    = contact.getBBox( viaFilter)
        lowerBox  = contact.getBBox( ShapeFilter( self.params.lowerLayer))
        upperBox  = contact.getBBox( ShapeFilter( self.params.upperLayer))

        rules = RulesDict()
        rules[ ( "minWidth",     self.params.viaLayer)] = viaBox.getWidth()

        value = viaBox.getBottom() - lowerBox.getBottom()
        rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.NORTH)] = value
        rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.SOUTH)] = value

        value = viaBox.getLeft()   - lowerBox.getLeft()
        rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.EAST) ] = value
        rules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer, Direction.WEST) ] = value

        value = viaBox.getBottom() - upperBox.getBottom()
        rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.NORTH)] = value
        rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.SOUTH)] = value

        value = viaBox.getLeft()   - upperBox.getLeft()
        rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.EAST)  ] = value
        rules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer, Direction.WEST)  ] = value

        contact.setMinCuts(2)
        rules[ ( "minSpacing",   self.params.viaLayer)] = contact.getBBox( viaFilter).getHeight() - \
            rules[ ( "minWidth", self.params.viaLayer)] - rules[ ( "minWidth", self.params.viaLayer)]

        contact.destroy()



        rules.update( self.params.addRules)
        self.rules = rules

    ####################################################################

    def setPin(
        self,
        pinName,
        termName,
        layer=None):
        """Create pins for upper and lower rectangles.
            """
        rects = self.getCompsSorted( layer=layer)
        pin   = Pin.find( pinName)

        if pin:
            # Different shapes on same pin => strong connect
            pin.addShape( rects)
        else:
            Pin( pinName, termName).addShape( rects)

########################################################################

class MosContact( MosCC):
    """Device contact consisting of a lower level rectangle, such
    as diffusion or poly layer, and a composite contact object,
    either a CompoundComponent or PyCell.
        """

    ####################################################################

    def construct(
        self):
        """Build the layout.
            """
        self.contact = ContactCC(
            lowerLayer = self.params.lowerLayer,
            upperLayer = self.params.upperLayer,
            viaLayer   = self.params.viaLayer,
            width      = self.params.width * self.params.coverage,
            implement  = self.implement,
            addRules   = self.params.addRules,
        )
        self.add( self.contact)

        self.makeLowerRect()

    ####################################################################

    def edgeExtend(
        self,
        direction,
        extension):
        """Extend one edge of the lower layer rectangle.
            """
        rect = self.getComp( Rect)
        box  = rect.getBBox()

        if direction == Direction.NORTH:
            box.setTop( box.getTop()       + extension)
        elif direction == Direction.SOUTH:
            box.setBottom( box.getBottom() - extension)
        elif direction == Direction.EAST:
            box.setRight( box.getRight()   + extension)
        elif direction == Direction.WEST:
            box.setLeft( box.getLeft()     - extension)
        else:
            pass

        rect.setBBox( box)

    ####################################################################

    def justify(
        self):
        """Justify contact within the larger lower layer rectangle.
        Align edges or center.
            """
        lowerFilter = ShapeFilter( self.params.lowerLayer)
        self.contact.alignEdge( self.params.justify, self.lowerRect, filter=lowerFilter)
        self.contact.snapY( self.grid)

    ####################################################################

    def getViaLayer(
        self):
        """Get via layer between two conducting layers.
            """
        return( self.tech.getIntermediateLayers( self.params.lowerLayer, self.params.upperLayer)[1][0])

    ####################################################################

    def locate(
        self):
        """Locate contact within the larger lower layer rectangles.
        Offset contact edge from lower layer rectangle edge.
            """
        lowerFilter = ShapeFilter( self.params.lowerLayer)

        if hasattr( self.params, "leftOffset"):
            self.contact.alignEdge( Direction.WEST, self.lowerRect, filter=lowerFilter)
            self.contact.moveTowards( Direction.EAST, self.params.leftOffset)
            if self.contact.getBBox( lowerFilter).getRight() > self.lowerRect.getBBox().getRight():
                self.contact.alignEdge( Direction.EAST, self.lowerRect, filter=lowerFilter)
        elif hasattr( self.params, "bottomOffset"):
            self.contact.alignEdge( Direction.SOUTH, self.lowerRect, filter=lowerFilter)
            self.contact.moveTowards( Direction.NORTH, self.params.bottomOffset)
            if self.contact.getBBox( lowerFilter).getTop() > self.lowerRect.getBBox().getTop():
                self.contact.alignEdge( Direction.NORTH, self.lowerRect, filter=lowerFilter)

    ####################################################################

    def makeLowerRect(
        self):
        """Override this virtual method to define how the lower
        layer rectangle should be built.
            """
        pass

    ####################################################################

    def setPin(
        self,
        pinName,
        termName,
        layer=None):
        """Create pins for lower layer rectangle and contact.
            """
        pin = Pin.find( pinName)

        rect = self.getCompsSorted( objType=Rect, layer=layer)
        if rect:
            rect = rect[0]
            if pin:
                # Different shapes on same pin => strong connect
                pin.addShape( rect)
            else:
                Pin( pinName, termName, rect)

        cont = self.getCompsSorted( objType=ContactCC)
        if cont:
            cont = cont[0]
            cont.setPin(
                pinName   = pinName,
                termName  = termName,
                layer     = layer,
            )

########################################################################

class ContactGate( MosContact):
    """Parent class for gate contacts.  Consists of contact composite
    object and poly rectangle.  Contacts are arranged in a single
    row.

    width is size of lower level rectangle.  coverage determines how
    much of poly rectangle is covered with contacts.
        """

    ####################################################################

    def makeLowerRect(
        self):
        """Create poly rectangle which contours upper and lower
        poly rectangle edge of contact, but may be wider depending
        on width.
            """
        box = self.contact.getBBox( ShapeFilter( self.contact.params.lowerLayer))
        box.setTop( max( box.getBottom() + self.params.width, box.getTop()))
        self.lowerRect = Rect( self.contact.params.lowerLayer, box)
        self.add( self.lowerRect)

    ####################################################################

    def updateRules(
        self):
        """Update addRules according to only those rules which apply to a ContactGate.
        Re-orient rules to account for horizontal orientation.
            """
        newAddRules = RulesDict()
        newAddRules[ ( "minSpacing",   self.params.viaLayer)] = 0.0

        lowerEncN = RulesDict.makeKey( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.NORTH)
        lowerEncS = RulesDict.makeKey( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.SOUTH)
        lowerEncE = RulesDict.makeKey( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.EAST)
        lowerEncW = RulesDict.makeKey( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.WEST)

        upperEncN = RulesDict.makeKey( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.NORTH)
        upperEncS = RulesDict.makeKey( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.SOUTH)
        upperEncE = RulesDict.makeKey( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.EAST)
        upperEncW = RulesDict.makeKey( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.WEST)

        newAddRules[ lowerEncN] = 0.0
        newAddRules[ lowerEncS] = 0.0
        newAddRules[ lowerEncE] = 0.0
        newAddRules[ lowerEncW] = 0.0

        newAddRules[ upperEncN] = 0.0
        newAddRules[ upperEncS] = 0.0
        newAddRules[ upperEncE] = 0.0
        newAddRules[ upperEncW] = 0.0

        newAddRules.update( self.params.addRules)
        ( newAddRules[ lowerEncN], newAddRules[ lowerEncS], newAddRules[ lowerEncE], newAddRules[ lowerEncW]) = \
            ( newAddRules[ lowerEncW], newAddRules[ lowerEncE], newAddRules[ lowerEncS], newAddRules[ lowerEncN])
        ( newAddRules[ upperEncN], newAddRules[ upperEncS], newAddRules[ upperEncE], newAddRules[ upperEncW]) = \
            ( newAddRules[ upperEncW], newAddRules[ upperEncE], newAddRules[ upperEncS], newAddRules[ upperEncN])
        self.params.addRules = newAddRules

########################################################################

class ContactGate1( ContactGate):
    """Create a ContactGate using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.
        """
    implement = "construct1"

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        coverage  = 1.0,
        justify   = Direction.EAST_WEST,
        addRules  = RulesDict()):
        """Create the layout.  Rotate to horizontal orientation,
        with bottom == left.  Justify the contact.
            """
        super( ContactGate1, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.rotate270()
        self.justify()
        self.lock()

########################################################################

class ContactGate2( ContactGate):
    """Create a ContactGate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on left and right offsets.
        """
    implement = "construct2"

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        leftOffset  = 0.0,
        rightOffset = 0.0,
        addRules    = RulesDict()):
        """Create the layout.  Rotate to horizontal orientation,
        with bottom == left.  Locate the contact.
            """
        coverage = max( 0.0, (width - leftOffset - rightOffset) / width)
        super( ContactGate2, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.rotate270()
        self.locate()
        self.lock()

########################################################################

class ContactGate4( ContactGate):
    """Create a ContactGate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.
        """
    implement = "construct2"

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        coverage  = 1.0,
        justify   = Direction.EAST_WEST,
        addRules  = RulesDict()):
        """Create the layout.  Rotate to horizontal orientation,
        with bottom == left.  Locate the contact.
            """
        super( ContactGate4, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.rotate270()
        self.locate()
        self.lock()

########################################################################

class ViaX( MosContact):
    """ Parent class for a metal via.  Consists of via composite object
    and a metal rectangle.  Contacts are arranged in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.
        """

    ####################################################################

    def makeLowerRect(
        self):
        """Create metal rectangle which contours left and right metal
        rectangle edge of contact, but may be wider depending on width.
            """
        box = self.contact.getBBox( ShapeFilter( self.contact.params.lowerLayer))
        box.setTop( max( box.getBottom() + self.params.width, box.getTop()))
        self.lowerRect = Rect( self.contact.params.lowerLayer, box)
        self.add( self.lowerRect)

    ####################################################################

    def updateRules(
        self):
        """Update addRules according to only those rules which apply to a ViaX.
            """
        newAddRules = RulesDict()
        newAddRules[ ( "minSpacing",   self.params.viaLayer)] = 0.0

        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.NORTH)] = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.SOUTH)] = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.EAST) ] = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.WEST) ] = 0.0

        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.NORTH)] = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.SOUTH)] = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.EAST) ] = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.WEST) ] = 0.0

        newAddRules.update( self.params.addRules)
        self.params.addRules = newAddRules

########################################################################

class ViaX1( ViaX):
    """Create a ViaX using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.
        """
    implement = "construct1"

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        coverage  = 1.0,
        addRules  = RulesDict(),
        justify   = Direction.NORTH_SOUTH):
        """Create the layout.  Justify the contact.
            """
        super( ViaX1, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.justify()
        self.lock()

########################################################################

class ViaX2( ViaX):
    """Create a ViaX using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.
        """
    implement = "construct2"

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        bottomOffset = 0.0,
        topOffset    = 0.0,
        addRules     = RulesDict()):
        """Create the layout.  Rotate to horizontal orientation,
        with bottom == left.  Locate the contact.
            """
        coverage = max( 0.0, (width - bottomOffset - topOffset) / width)
        super( ViaX2, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ViaX4( ViaX):
    """Create a ViaX using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.
        """
    implement = "construct2"

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        coverage  = 1.0,
        addRules  = RulesDict(),
        justify   = Direction.NORTH_SOUTH):
        """Create the layout.  Rotate to horizontal orientation,
        with bottom == left.  Locate the contact.
            """
        super( ViaX4, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ContactCenter( MosContact):
    """Parent class for center source/drain diffusion contact.  Consists
    of a composite contact object and a diffusion rectangle.  Contacts
    are arranged in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.
        """

    ####################################################################

    def makeLowerRect(
        self):
        """Create lower layer rectangle by placing a sequence of
        gate poly rectangle, contact, gate poly rectangle, then
        trimming the lower layer rectangle.
            """
        # These are arbitrary numbers, chosen to be very large
        pt     = Point( SCRATCHPAD[0], SCRATCHPAD[1])
        endcap = 1.0
        diffw  = 10.0 * self.params.gateLength



        # Create diffusion rectangle and environment layers.
        # height = transistor width, width = large value.
        g0 = Grouping()

        lowerRect = Rect( self.params.lowerLayer, Box( 0, 0, diffw, self.params.width))
        lowerRect.moveTo( pt, loc=Location.LOWER_LEFT)

        g1 = EnclosingRects( lowerRect, self.params.envLayers, grid=self.grid)
        g0.add( [ lowerRect, g1])



        # Create gate poly.
        gateRect0 = Rect( self.params.gateLayer, Box( 0, 0, self.params.gateLength, self.params.width + ( 2.0 * endcap)))
        gateRect0.alignLocation( Location.CENTER_LEFT, lowerRect)
        gateRect1 = gateRect0.clone()

        # Need to consider the poly gate for fgPlace() environment,
        # in order to ensure that "wide poly" design rules are used.
        g0.add(gateRect0)


        # Place gate, contact, gate.  Trim diffusion.
        lowerFilter = ShapeFilter( self.params.lowerLayer)
        self.contact.alignLocation( Location.LOWER_CENTER, lowerRect, filter=lowerFilter)
        stack( [ gateRect0, self.contact, gateRect1], g0, self.grid)
        trim( lowerRect, [ gateRect0, gateRect1])



        # Clean-up.
        gateRect0.destroy()
        gateRect1.destroy()
        g0.ungroup()
        g1.destroy()

        self.add( lowerRect)
        self.lowerRect = lowerRect



        # Additional contact-to-gate spacing.
        addWidth = 0.0
        if self.params.withGateContact:
            gateContact = ContactGate2(
                lowerLayer = self.params.gateLayer,
                upperLayer = self.params.upperLayer,
                width      = self.params.gateLength,
                addRules   = self.params.addRules,
            )

            addWidth = max( 0,
                gateContact.fgMinSpacing( Direction.EAST, gateContact) +
                gateContact.getBBox().getWidth() -
                self.params.gateLength -
                lowerRect.getBBox().getWidth()
            )
            addWidth = MosGrid.ceil( ( addWidth / 2.0), self.grid.getSize())
            gateContact.destroy()

        self.edgeExtend(
            Direction.EAST,
            self.params.addRules[ ( "minSpacing", self.params.viaLayer, self.params.gateLayer, Direction.EAST_WEST)]
        )

        self.edgeExtend(
            Direction.WEST,
            self.params.addRules[ ( "minSpacing", self.params.viaLayer, self.params.gateLayer, Direction.EAST_WEST)]
        )

    ####################################################################

    def updateRules(
        self):
        """Update addRules according to only those rules which apply to a ContactCenter.
            """
        newAddRules = RulesDict()
        newAddRules[ ( "minSpacing",   self.params.viaLayer)] = 0.0
        newAddRules[ ( "minSpacing",   self.params.viaLayer,   self.params.gateLayer, Direction.EAST_WEST)] = 0.0

        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.NORTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.SOUTH)]     = 0.0

        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.NORTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.SOUTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.EAST )]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.WEST )]     = 0.0

        newAddRules.update( self.params.addRules)
        self.params.addRules = newAddRules

########################################################################

class ContactCenter1( ContactCenter):
    """Create a ContactCenter using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.
        """
    implement  = "construct1"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        gateLayer,
        width,
        gateLength,
        addContGateSpacing = 0.0,
        addRules           = RulesDict(),
        coverage           = 1.0,
        envLayers          = [],
        justify            = Direction.NORTH_SOUTH,
        withGateContact    = True):
        """Create the layout.  Justify the contact.
            """
        super( ContactCenter1, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.justify()
        self.lock()

########################################################################

class ContactCenter2( ContactCenter):
    """Create a ContactCenter using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.
        """
    implement  = "construct2"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        gateLayer,
        width,
        gateLength,
        bottomOffset       = 0.0,
        addContGateSpacing = 0.0,
        addRules           = RulesDict(),
        envLayers          = [],
        topOffset          = 0.0,
        withGateContact    = True):
        """Create the layout.  Locate the contact.
            """
        coverage = max( 0.0, (width - bottomOffset - topOffset) / width)
        super( ContactCenter2, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ContactCenter4( ContactCenter):
    """Create a ContactCenter using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.
        """
    implement  = "construct2"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        gateLayer,
        width,
        gateLength,
        addContGateSpacing = 0.0,
        addRules           = RulesDict(),
        coverage           = 1.0,
        envLayers          = [],
        justify            = Direction.NORTH_SOUTH,
        withGateContact    = True):
        """Create the layout.  Locate the contact.
            """
        super( ContactCenter4, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ContactEdge( MosContact):
    """Parent class for right/left edge source/drain diffusion contact.
    Consists of contact composite object and a diffusion rectangle.
    Contacts are arranged in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.
        """

    ####################################################################

    def makeLowerRect(
        self):
        """Create lower layer rectangle by placing a sequence of
        contact, gate poly rectangle, then trimming the lower layer
        rectangle.
            """
        # These are arbitrary numbers, chosen to be very large
        pt     = Point( SCRATCHPAD[0], SCRATCHPAD[1])
        endcap = 1.0
        diffw  = 10.0 * self.params.gateLength



        # Create diffusion rectangle and environment layers.
        # height = transistor width, width = large value.
        g0 = Grouping()

        lowerRect = Rect( self.params.lowerLayer, Box( 0, 0, diffw, self.params.width))
        lowerRect.moveTo( pt, loc=Location.LOWER_LEFT)

        g1 = EnclosingRects( lowerRect, self.params.envLayers, grid=self.grid)
        g0.add( [ lowerRect, g1])

        # Create gate poly.
        gateRect0 = Rect( self.params.gateLayer, Box( 0, 0, self.params.gateLength, self.params.width + ( 2.0 * endcap)))



        # Place contact, gate.  Trim diffusion.
        self.contact.alignLocation( Location.LOWER_LEFT, lowerRect, filter=ShapeFilter( self.params.lowerLayer))
        gateRect0.alignLocation( Location.CENTER_RIGHT, lowerRect)
        stack( [ self.contact, gateRect0], g0, self.grid)
        trim( lowerRect, [ gateRect0])

        # Adjust if diffusion extension beyond poly gate,
        # i.e. source/drain diffusion width is larger than trimmed diffusion.
        dRect = DiffEdge(
            lowerLayer      = self.params.lowerLayer,
            upperLayer      = self.params.upperLayer,
            gateLayer       = self.params.gateLayer,
            width           = self.params.width,
            gateLength      = self.params.gateLength,
            envLayers       = self.params.envLayers,
            withGateContact = False,
        )

        bbox = lowerRect.getBBox()
        w0   = bbox.getWidth()
        w1   = dRect.getBBox().getWidth()
        if w1 > w0:
            bbox.expand( Direction.WEST, w1 - w0)
            lowerRect.setBBox( bbox)
        dRect.destroy()



        # Clean-up.
        gateRect0.destroy()
        g0.ungroup()
        g1.destroy()

        self.add( lowerRect)
        self.lowerRect = lowerRect



        # Adjust if contact-to-gate spacing is larger.
        self.edgeExtend(
            Direction.EAST,
            self.params.addRules[ ( "minSpacing", self.contact.params.viaLayer, self.params.gateLayer, Direction.EAST_WEST)]
        )

    ####################################################################

    def updateRules(
        self):
        """Update addRules according to only those rules which apply to a ContactEdge.
            """
        newAddRules = RulesDict()
        newAddRules[ ( "minSpacing",   self.params.viaLayer)] = 0.0
        newAddRules[ ( "minSpacing",   self.params.viaLayer,   self.params.gateLayer, Direction.EAST_WEST)] = 0.0

        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.NORTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.SOUTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.WEST )]     = 0.0

        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.NORTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.SOUTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.EAST )]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.WEST )]     = 0.0
        newAddRules.update( self.params.addRules)
        self.params.addRules = newAddRules

########################################################################

class ContactEdge1( ContactEdge):
    """Create a ContactEdge using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.
        """
    implement  = "construct1"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        gateLayer,
        width,
        gateLength,
        addRules           = RulesDict(),
        coverage           = 1.0,
        envLayers          = [],
        justify            = Direction.NORTH_SOUTH):
        """Create the layout.  Justify the contact.
            """
        super( ContactEdge1, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.justify()
        self.lock()

########################################################################

class ContactEdgeAbut1( ContactEdge1):
    """Creates same layout as ContactEdge1, but is tagged as isAbutable.
        """
    isAbutable = True

########################################################################

class ContactEdge2( ContactEdge):
    """Create a ContactEdge using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.
        """
    implement  = "construct2"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        gateLayer,
        width,
        gateLength,
        bottomOffset       = 0.0,
        addContGateSpacing = 0.0,
        addRules           = RulesDict(),
        envLayers          = [],
        topOffset          = 0.0):
        """Create the layout.  Locate the contact.
            """
        coverage = max( 0.0, (width - bottomOffset - topOffset) / width)
        super( ContactEdge2, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ContactEdgeAbut2( ContactEdge2):
    """Creates same layout as ContactEdge2, but is tagged as isAbutable.
        """
    isAbutable = True

########################################################################

class ContactEdge4( ContactEdge):
    """Create a ContactEdge using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.
        """
    implement  = "construct2"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        gateLayer,
        width,
        gateLength,
        addContGateSpacing = 0.0,
        addRules           = RulesDict(),
        coverage           = 1.0,
        envLayers          = [],
        justify            = Direction.NORTH_SOUTH):
        """Create the layout.  Locate the contact.
            """
        super( ContactEdge4, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ContactEdgeAbut4( ContactEdge4):
    """Creates same layout as ContactEdge4, but is tagged as isAbutable.
        """
    isAbutable = True

########################################################################

class ContactSubstrate( MosContact):
    """Parent class for a substrate contact.  Consists of contact
    composite object and a diffusion rectangle.  Contacts are arranged
    in a single column.

    width is size of lower level rectangle.  coverage determines how
    much of diffusion rectangle is covered with contacts.
        """

    ####################################################################

    def makeLowerRect(
        self):
        """Create lower layer rectangle which matches left and right
        diffusion edge of diffusion contact.
            """
        # These are arbitrary numbers, chosen to be very large
        pt     = Point( SCRATCHPAD[0], SCRATCHPAD[1])

        # Create diffusion rectangle and environment layers.
        # height = transistor width, width = large value.
        g0  = Grouping()

        box = self.contact.getBBox( ShapeFilter( self.params.lowerLayer))
        box.setTop( box.getBottom() + self.params.width)
        lowerRect = Rect( self.params.lowerLayer, box)
        lowerRect.moveTo( pt, loc=Location.LOWER_LEFT)

        # Place contact.
        self.contact.alignLocation( Location.LOWER_LEFT, lowerRect, filter=ShapeFilter( self.params.lowerLayer))

        # Clean-up.
        self.add( lowerRect)
        self.lowerRect = lowerRect

    ####################################################################

    def updateRules(
        self):
        """Update addRules according to only those rules which apply to a ContactSubstrate.
            """
        newAddRules = RulesDict()
        newAddRules[ ( "minSpacing",   self.params.viaLayer)] = 0.0

        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.NORTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.SOUTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.EAST )]     = 0.0
        newAddRules[ ( "minExtension", self.params.lowerLayer, self.params.viaLayer,  Direction.WEST )]     = 0.0

        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.NORTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.SOUTH)]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.EAST )]     = 0.0
        newAddRules[ ( "minExtension", self.params.upperLayer, self.params.viaLayer,  Direction.WEST )]     = 0.0
        newAddRules.update( self.params.addRules)
        self.params.addRules = newAddRules

########################################################################

class ContactSubstrate1( ContactSubstrate):
    """Create a ContactSubstrate using ContactCC.construct1.  Minimize the
    upper layer dimension to surround the maximum number of minimum
    spaced contacts which can fit within the requested coverage.
        """
    implement  = "construct1"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        addRules           = RulesDict(),
        coverage           = 1.0,
        justify            = Direction.NORTH_SOUTH):
        """Create the layout.  Justify the contact.
            """
        super( ContactSubstrate1, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.justify()
        self.lock()

########################################################################

class ContactSubstrate2( ContactSubstrate):
    """Create a ContactSubstrate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on upper and lower offsets.
        """
    implement  = "construct2"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        bottomOffset       = 0.0,
        addRules           = RulesDict(),
        topOffset          = 0.0):
        """Create the layout.  Locate the contact.
            """
        coverage = max( 0.0, (width - bottomOffset - topOffset) / width)
        super( ContactSubstrate2, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ContactSubstrate4( ContactSubstrate):
    """Create a ContactSubstrate using ContactCC.construct2.  Upper layer
    dimension sized as requested, then filled the maximum number of
    equally spaced contacts.  Based on coverage.
        """
    implement  = "construct2"
    isAbutable = False

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        width,
        addRules           = RulesDict(),
        coverage           = 1.0,
        justify            = Direction.NORTH_SOUTH):
        """Create the layout.  Locate the contact.
            """
        super( ContactSubstrate4, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        self.updateRules()
        self.construct()
        self.locate()
        self.lock()

########################################################################

class ContactSubstrateAbut( MosContact):
    """Given a reference ContactEdge object, return a list containing
    a modified ContactEdge and a abutting substract contact.
        """
    isAbutable = True

    ####################################################################

    def __init__(
        self,
        substrateContact,
        lowerLayer,
        upperLayer,
        implantLayer,
        direction,
        wellLayer = None):
        """Given a MosContact object, subsume the object as a
        ContactSubstrateAbut.  Do not use this constructor to
        build the layout; rather use the static method
        constructAbuttingContacts().
            """

        super( ContactSubstrateAbut, self).__init__( locals())
        self.params.viaLayer = self.getViaLayer()

        del self.params["substrateContact"]
        substrateContact.ungroup( owner=self)
        self.lock()

    ####################################################################

    @staticmethod
    def checkEdge(
        comp,
        refComp,
        direction,
        refDirection=None):

        getEdge = {
            Direction.NORTH : "getTop",
            Direction.SOUTH : "getBottom",
            Direction.EAST  : "getRight",
            Direction.WEST  : "getLeft",
        }

        if not refDirection:
            refDirection = direction

        if getattr( comp.getBBox(), getEdge[ direction])() == getattr( refComp.getBBox(), getEdge[ refDirection])():
            raise ValueError, "Unable to determine spacing for butting implant edge to contact."

    ####################################################################

    @staticmethod
    def constructAbuttingContacts(
        contact,
        refImplantLayer,
        lowerLayer,
        upperLayer,
        implantLayer,
        direction,
        wellLayer = None):
        """Construct a ContactEdge and a substrate contact which will abut.
            """
        tech = DloGen.currentDloGen().tech
        grid = tech.getGridResolution()
        contactLayer  = tech.getIntermediateLayers( lowerLayer, upperLayer)[1][0]
        contactFilter = ShapeFilter( contactLayer)



        # Clone contact and make implant as starting objects.
        ( refContact, refImplant) = ContactSubstrateAbut.makeContact( contact, refImplantLayer, wellLayer)
        ( subContact, subImplant) = ContactSubstrateAbut.makeContact( contact, implantLayer,    wellLayer)

        g0 = Grouping( components=[ refContact, refImplant])
        g1 = Grouping( components=[ subContact, subImplant])
        g1.place( direction, g0, 0, align=False)

        g0.ungroup()
        g1.ungroup()

        # Create environment rectangles.
        box = subImplant.getBBox()
        box.merge( refImplant.getBBox())
        refEnv = Grouping( components=Rect( lowerLayer, box))
        
        if wellLayer:
            refEnv.add( Rect( wellLayer, box))



        # Calculate position for butting implants.
        # This algorithm is not robust, as it depends on fgPlace()
        # implementation of starting location is 1 grid from edge of
        # the reference component.
        box = refContact.getBBox( contactFilter)
        box.expand( direction, grid)
        ContactSubstrateAbut.matchEdge( refImplant, box, direction)

        contacts = [ i.clone() for i in refContact.getLeafComps() if i.getLayer() == contactLayer]
        contacts = Grouping( components=contacts)
        refEnv.add( [ refContact, refImplant, subContact])
        ggPlace( subImplant, direction, contacts, env=refEnv, align=False)

        ContactSubstrateAbut.checkEdge( subImplant, contacts, Direction.opposite( direction), direction)
        ContactSubstrateAbut.matchEdge( refImplant, subImplant, direction, Direction.opposite( direction))

        # Calculate position for contacts.
        refEnv.remove( subContact)
        refEnv.add( subImplant)
        ggPlace( contacts, direction, refImplant, align=False, env=refEnv)

        subContact.alignEdge( Direction.opposite( direction), contacts, filter=contactLayer)
        refEnv.remove( [ refContact, refImplant, subImplant])

        refEnv.destroy()
        contacts.destroy()



        # Adjust diffusion edges.
        diffRect = refContact.getComp( objType=Rect)
        ContactSubstrateAbut.matchEdge( diffRect, refImplant, direction)

        diffRect = subContact.getComp( objType=Rect)
        ContactSubstrateAbut.matchEdge( diffRect, subImplant, Direction.opposite( direction))



        refContact.isAbutable = True
        refImplant.destroy()
        subImplant.destroy()
        subContact = ContactSubstrateAbut(
            substrateContact = subContact,
            lowerLayer       = lowerLayer,
            upperLayer       = upperLayer,
            implantLayer     = implantLayer,
            direction        = direction,
            wellLayer        = wellLayer,
        )
        return( refContact, subContact)

    ####################################################################

    @staticmethod
    def makeContact(
        contact,
        implantLayer,
        wellLayer):

        contact = contact.clone()

        layers = [ implantLayer]
        if wellLayer:
            layers.insert( 0, wellLayer)

        rects = EnclosingRects( contact, layers).ungroupAsList()

        for rect in rects:
            if rect.getLayer() == implantLayer:
                implant = rect
            else:
                rect.destroy()

        return( contact, implant)

    ####################################################################

    @staticmethod
    def matchEdge(
        comp,
        refComp,
        direction,
        refDirection=None):

        getEdge = {
            Direction.NORTH : "getTop",
            Direction.SOUTH : "getBottom",
            Direction.EAST  : "getRight",
            Direction.WEST  : "getLeft",
        }

        setEdge = {
            Direction.NORTH : "setTop",
            Direction.SOUTH : "setBottom",
            Direction.EAST  : "setRight",
            Direction.WEST  : "setLeft",
        }

        if not refDirection:
            refDirection = direction

        getattr( comp, setEdge[ direction])(
            getattr( refComp, getEdge[ refDirection])()
        )

########################################################################

class MosGate( MosCC):
    """Transistor gate poly and underlying channel diffusion.
        """

    ####################################################################

    def __init__(
        self,
        diffLayer,
        gateLayer,
        gateWidth,
        gateLength,
        addRules  = RulesDict(),
        envLayers = []):
        """Create transistor gate poly and channel diffusion.
            """
        super( MosGate, self).__init__( locals())

        self.updateRules()
        self.construct()
        self.lock()

    ####################################################################

    def construct(
        self):
        """Build the layout.
            """
        # Create channel diffusion.
        pt0   = Point( SCRATCHPAD[0], SCRATCHPAD[1])
        dBox  = Box( pt0, pt0 + Point( self.params.gateLength, self.params.gateWidth))
        dRect = Rect( self.params.diffLayer, dBox)



        # Create enclosing poly rectangle.
        # Amount of overlap should be transistor endcap.
        encLayers = [ self.params.gateLayer]
        encLayers.extend( self.params.envLayers)
        rects     = EnclosingRects( dRect, encLayers, grid=self.grid).ungroupAsList()
        for rect in rects:
            if rect.getLayer() == self.params.gateLayer:
                pRect = rect
            else:
                rect.destroy()

        # Check for valid results
        if dRect.getBBox() == pRect.getBBox():
            raise ValueError, "Unable to determine correct value for transistor endcap."



        # Trim left and right edge of poly rectangle to match channel diffusion.
        # Adjust top and bottom edge per request.
        box    = pRect.getBBox()
        bottom = box.getBottom() - \
            self.params.addRules[ ("minExtension", self.params.gateLayer, self.params.diffLayer, Direction.SOUTH)]
        top    = box.getTop() + \
            self.params.addRules[ ("minExtension", self.params.gateLayer, self.params.diffLayer, Direction.NORTH)]
        box = Box( pt0.x, bottom, pt0.x + self.params.gateLength, top,)
        pRect.setBBox( box)

        self.add( [ dRect, pRect])



        # Create top and bottom poly rectangles for later use as pins.
        newBox = pRect.getBBox()
        newBox.setTop( dBox.getBottom())
        self.add(
            Rect( self.params.gateLayer, newBox)
        )

        newBox = pRect.getBBox()
        newBox.setBottom( dBox.getTop())
        self.add(
            Rect( self.params.gateLayer, newBox)
        )

    ####################################################################
        
    def setPin(
        self,
        pinNamePrefix,
        termName,
        layer=None):
        """Create upper and lower gate pins.
            """
        # Use area, not height, to avoid orientation effects.
        sortFunction = lambda a, b: cmp( a.getBBox().getArea(), b.getBBox().getArea())
        rects = self.getCompsSorted( layer=self.params.gateLayer, sortFunction=sortFunction)

        # Entire poly added to net.
        rects[2].setNet( Term.find( termName).getNet())

        # Drop the largest poly shape (gate), since only poly
        # endcaps become pins.  Order from lower to upper.
        rects = rects[0:2]
        rects.sort( Compare.cmpCenterYAscend)

        # Different pins, same terminal => weak connects
        i = 0
        for suffix in ( "_B", "_T"):
            pinName = "%s%s" % ( pinNamePrefix, suffix)
            pin = Pin.find( pinName)
            if pin:
                pin.addShape( rects[i])
            else:
                Pin( pinName, termName, rects[i])
            i += 1

    ####################################################################

    def updateRules(
        self):
        """Update addRules according to only those rules which apply to a MosGate.
            """
        newAddRules = RulesDict()
        newAddRules[ ( "minExtension", self.params.gateLayer, self.params.diffLayer,  Direction.NORTH)] = 0.0
        newAddRules[ ( "minExtension", self.params.gateLayer, self.params.diffLayer,  Direction.SOUTH)] = 0.0
        newAddRules.update( self.params.addRules)
        self.params.addRules = newAddRules

########################################################################

class MosDiffusion( MosCC):
    """Parent class for source/drain diffusion consisting of a
    single diffusion rectangle.
        """

    ####################################################################

    def __init__(
        self,
        lowerLayer,
        upperLayer,
        gateLayer,
        width,
        gateLength,
        addRules        = RulesDict(),
        envLayers       = [],
        withGateContact = True):
        """Build the layout.
            """
        super( MosDiffusion, self).__init__( locals())
        self.construct()
        self.lock()

    ####################################################################

    def setPin(
        self,
        pinName,
        termName,
        layer=None):
        """Create pin.
            """
        pin   = Pin.find( pinName)
        shape = self.getComps()[0]
        if pin:
            # Different shapes on same pin => strong connect
            pin.addShape( shape)
        else:
            Pin( pinName, termName, shape)

########################################################################

class DiffAbut( MosDiffusion):
    """Sliver of source/drain diffusion, needed for auto-abutment
    with contact.
        """
    isAbutable = True

    ####################################################################

    def construct(
        self):
        """Build the layout by creating a ContactCenter contact and an
        ContactEdge.  Use the difference in diffusion width to calculate
        the diffusion rectangle.
            """
        # Create the contacts.
        cCenter = ContactCenter2(
            lowerLayer      = self.params.lowerLayer,
            upperLayer      = self.params.upperLayer,
            gateLayer       = self.params.gateLayer,
            width           = self.params.width,
            gateLength      = self.params.gateLength,
            envLayers       = self.params.envLayers,
            withGateContact = self.params.withGateContact,
        )

        cEdge = ContactEdge2(
            lowerLayer      = self.params.lowerLayer,
            upperLayer      = self.params.upperLayer,
            gateLayer       = self.params.gateLayer,
            width           = self.params.width,
            gateLength      = self.params.gateLength,
            envLayers       = self.params.envLayers,
        )

        # Get the lower layer diffusion rectangle.
        (dRectC, contactC) = cCenter.getComps()
        cCenter.ungroup()
        if isinstance( dRectC, MosCC):
            (dRectC, contactC) = (contactC, dRectC)
        contactC.destroy()

        (dRectE, contactE) = cEdge.getComps()
        cEdge.ungroup()
        if isinstance( dRectE, MosCC):
            (dRectE, contactE) = (contactE, dRectE)
        contactE.destroy()

        # Set diffusion rectangle width to the difference in widths.
        # Minimum size diffusion rectangle is 2 layout grid, to avoid
        # error caused by zero width.
        boxC = dRectC.getBBox()
        boxE = dRectE.getBBox()
        boxE.setRight( boxE.getLeft() + 
            max( boxC.getWidth() - boxE.getWidth(), 2.0 * self.grid.getSize())
        )

        dRectE.setBBox( boxE)



        # Clean-up.
        dRectC.destroy()
        self.add( dRectE)

########################################################################

class DiffCenter( MosDiffusion):
    """Center source/drain diffusion, defined by gate-to-gate spacing.
        """
    isAbutable = False

    ####################################################################

    def construct(
        self):
        """Build the layout by creating a rectangle of diffusion, then
        placing two poly gates.  Trim diffusion edges under the poly gates.
            """
        # These are arbitrary numbers, chosen to be very large
        pt     = Point( SCRATCHPAD[0], SCRATCHPAD[1])
        endcap = 1.0
        diffw  = 10.0 * self.params.gateLength



        # Create diffusion rectangle and environment layers.
        # height = transistor width, width = large value.
        g0 = Grouping()

        lowerRect = Rect( self.params.lowerLayer, Box( 0, 0, diffw, self.params.width))
        lowerRect.moveTo( pt, loc=Location.LOWER_LEFT)

        g1 = EnclosingRects( lowerRect, self.params.envLayers, grid=self.grid)
        g0.add( [ lowerRect, g1])



        # Create gate poly.
        gate0 = Rect( self.params.gateLayer, Box( 0, 0, self.params.gateLength, self.params.width + ( 2.0 * endcap)))
        gate0.alignLocation( Location.CENTER_LEFT, lowerRect)
        gate1 = gate0.clone()



        # Place 2 parallel gates.  Trim diffusion.
        stack( [ gate0, gate1], g0, self.grid)
        trim( lowerRect, [ gate0, gate1])



        # Clean-up.
        gate0.destroy()
        gate1.destroy()
        g0.ungroup()
        g1.destroy()

        self.add( lowerRect)
        self.lowerRect = lowerRect



        # Adjust for gate contacts.
        addWidth = 0.0
        if self.params.withGateContact:
            gateContact = ContactGate2(
                lowerLayer = self.params.gateLayer,
                upperLayer = self.params.upperLayer,
                width      = self.params.gateLength,
            )

            addWidth = max( 0,
                gateContact.fgMinSpacing( Direction.EAST, gateContact) +
                gateContact.getBBox().getWidth() -
                self.params.gateLength - 
                lowerRect.getBBox().getWidth()
            )
            gateContact.destroy()

            box = lowerRect.getBBox()
            box.setRight( box.getRight() + addWidth)
            lowerRect.setBBox( box)

########################################################################

class DiffEdge( MosDiffusion):
    """Minimum right/left source/drain diffusion width.
        """
    isAbutable = False

    ####################################################################

    def construct(
        self):
        """Build the layout by generating a diffusion rectangle enclosing
        a poly rectangle.  Use the overlap as the minimum source/drain
        diffusion width.
            """
        # Create gate poly.
        pt        = Point( SCRATCHPAD[0], SCRATCHPAD[1])
        gateRect  = Rect( self.params.gateLayer, Box( 0, 0, self.params.gateLength, self.params.width))
        gateRect.moveTo( pt, loc=Location.LOWER_LEFT)



        # Create enclosing diffusion rectangle.
        # Amount of overlap should be source/drain diffusion width.
        encLayers = [ self.params.lowerLayer]
        encLayers.extend( self.params.envLayers)
        rects     = EnclosingRects( gateRect, encLayers, grid=self.grid).ungroupAsList()
        for rect in rects:
            if rect.getLayer() == self.params.lowerLayer:
                lowerRect = rect
            else:
                rect.destroy()

        # Check for valid results
        if gateRect.getBBox() == lowerRect.getBBox():
            raise ValueError, "Unable to determine correct value for transistor s/d diffusion width."

        # Trim top, bottom, and right edge of diffusion rectangle
        # to match gate
        gateBox  = gateRect.getBBox()
        lowerBox = lowerRect.getBBox()
        lowerBox.setTop( gateBox.getTop())
        lowerBox.setBottom( gateBox.getBottom())
        lowerBox.setRight( gateBox.getLeft())
        lowerRect.setBBox( lowerBox)



        # Clean-up.
        gateRect.destroy()
        self.add( lowerRect)

########################################################################

class DiffEdgeAbut( DiffEdge):
    """Creates same layout as DiffEdge, but is tagged as isAbutable.
        """
    isAbutable = True

########################################################################

class DiffHalf( MosDiffusion):
    """Half width of center source/drain diffusion, DiffCenter, as
    needed for auto-abutment without contact.
        """
    isAbutable = True

    ####################################################################

    def construct(
        self):
        """Build the layout by creating a DiffCenter object, then
        halving the width of the diffusion rectangle.
            """
        m0 = DiffCenter(
            lowerLayer      = self.params.lowerLayer,
            upperLayer      = self.params.upperLayer,
            gateLayer       = self.params.gateLayer,
            width           = self.params.width,
            gateLength      = self.params.gateLength,
            envLayers       = self.params.envLayers,
            withGateContact = self.params.withGateContact,
        )
        lowerRect = m0.getComps()[0]
        m0.ungroup()

        box   = lowerRect.getBBox()
        width = MosGrid.ceil( ( box.getWidth() / 2.0), self.grid.getSize())

        box.setRight( box.getLeft() + width)
        lowerRect.setBBox( box)

        self.add( lowerRect)
        self.lowerRect = lowerRect

########################################################################

class DiffHalf2( MosDiffusion):
    """Source/drain diffusion Rect needed for auto-abutment of two
    fingers without shared Contact.
    Resulting spacing between two fingers will be == 2*DiffHalf2.width
    == ContactCenter.width, to allow for aligning with other two fingers
    with shared Contact.
        """
    isAbutable = True

    ####################################################################

    def construct(
        self):
        """Build the layout by creating a ContactCenter and use halfWidth
        of ContactCenter to create Diff Rect.
            """
        # Create the contact.
        cCenter = ContactCenter1(
            lowerLayer      = self.params.lowerLayer,
            upperLayer      = self.params.upperLayer,
            gateLayer       = self.params.gateLayer,
            width           = self.params.width,
            gateLength      = self.params.gateLength,
            envLayers       = self.params.envLayers,
            withGateContact = False,
        )

        # Get the lower layer diffusion rectangle.
        (dRectC, contactC) = cCenter.getComps()
        cCenter.ungroup()
        if isinstance( dRectC, MosCC):
            (dRectC, contactC) = (contactC, dRectC)
        contactC.destroy()

        # Set diffusion rectangle width to half the ContactCenter
        # diffusion rectangle width.
        dRectCBox      = dRectC.getBBox()
        dRectCBoxWidth = dRectCBox.getWidth()

        dRectCBox.right = dRectCBox.getLeft() + \
            MosGrid.ceil( ( dRectCBox.getWidth() / 2.0), self.grid.getSize())
        dRectC.setBBox( dRectCBox)

        # Include DiffRect
        self.add( dRectC)

########################################################################
#                                                                      #
# Classes of Transistor Assembly                                       #
#                                                                      #
########################################################################

class MosBody( MosCC):
    """Parent class for MOS transistor.
        """

    ####################################################################

    def addDiffConn(
        self,
        direction,
        pattern,
        withVia      = False,
        diffConn     = None,
        env          = None):
        """Add a diffusion contact connection as close as possible.
            """
        # Separate contacts into those to avoid and those to connect.
        gc = BorrowGrouping()  # Grouping to connect.
        ga = BorrowGrouping()  # Grouping to avoid.

        comps = self.getCompsSorted( objType=( ContactEdge, ContactCenter, MosDiffusion))
        for i in pattern:
            gc.add( comps[i])
        gcRange = gc.getBBox().getRangeX()

        for comp in self.getComps():
            if gcRange.overlaps( comp.getBBox().getRangeX()):
                ga.add( comp)



        # Create the connecting object.  Use a ViaX1 object.
        # Metal2 & vias needed for proper placement.
        metal1Filter = ShapeFilter( self.params.metal1Layer)
        gaBox        = ga.getBBox( metal1Filter)
        gcBox        = gc.getBBox( metal1Filter)

        gcComps = gc.getComps()
        gcComps.sort( Compare.cmpCenterXAscend)

        if not diffConn:
            diffConn = ViaX1(
                lowerLayer = self.params.metal1Layer,
                upperLayer = self.params.metal2Layer,
                width      = gcBox.getWidth(),
                addRules   = self.params.addRules,
            )
            diffConn.rotate90()

        # Place ViaX1 object.
        diffConn.alignEdge( Direction.EAST_WEST, gc, filter=metal1Filter)
        gc.ungroup()
        if env:
            self.add( env)

        diffConn.ggPlace( direction, ga, env=self, align=False, filter=metal1Filter, grid=self.grid)
        if env:
            self.remove( env)

        # Remove contact & metal1 as needed.
        if not withVia:
            diffConn.unlock()
            diffConn.getComp( ContactCC).destroy()
            diffConn.lock()



        # Clean-up.
        self.add( diffConn)
        ga.ungroup()

        return( diffConn)

    ####################################################################

    def addGateConn(
        self,
        direction,
        pattern,
        withContact = True,
        pitchMatch  = True,
        gateConn    = None,
        env         = None):
        """Add a gate connection as close as possible.
            """
        # Separate gates into those to avoid and those to connect.
        gc = BorrowGrouping()  # Grouping to connect.
        ga = BorrowGrouping()  # Grouping to avoid.

        comps = self.getCompsSorted( objType=MosGate)
        for i in pattern:
            gc.add( comps[i])
        gcRange = gc.getBBox().getRangeX()

        for comp in self.getComps():
            if gcRange.overlaps( comp.getBBox().getRangeX()):
                ga.add( comp)



        # Create the connecting object.  Use a ContactGate1 object.
        # Metal1 & contact needed for proper placement.
        polyFilter = ShapeFilter( self.params.gateLayer)
        gaBox      = ga.getBBox( polyFilter)
        gcBox      = gc.getBBox( polyFilter)

        if not gateConn:
            gateConn = ContactGate1(
                lowerLayer = self.params.gateLayer,
                upperLayer = self.params.metal1Layer,
                width      = gcBox.getWidth(),
                addRules   = self.params.addRules,
            )

        # Place ContactGate1 object.
        gateConn.alignEdge( Direction.EAST_WEST, gc, filter=polyFilter)
        gc.ungroup()
        if env:
            self.add( env)

        gateConn.ggPlace( direction, ga, env=self, align=False, grid=self.grid)
        if env:
            self.remove( env)

        # Remove contact & metal1 as needed.
        if not withContact:
            gateConn.unlock()
            gateConn.getComp( ContactCC).destroy()
            gateConn.lock()



        # Clean-up.
        self.add( gateConn)
        ga.ungroup()

        return( gateConn)

    ####################################################################

    def alignDogboneContacts(
        self):
        """Center align dogbone contacts with gate diffusion.
            """
        diffConts = self.getCompsSorted( objType=(ContactCenter, ContactEdge))
        refGate   = self.getComp( objType=MosGate)
        filter    = ShapeFilter( self.params.diffLayer)

        if diffConts and (refGate.getBBox( filter).getHeight() < diffConts[0].getBBox( filter).getHeight()):
            for diffCont in diffConts:
                diffCont.unlock()
                rect = diffCont.getComp( objType=Rect)
                rect.alignEdge( Direction.SOUTH, refGate, filter=filter)
                diffCont.lock()

            self.justifyDiffContacts( Direction.NORTH_SOUTH)

    ####################################################################

    def justifyDiffContacts(
        self,
        direction):
        """Justify contacts.
            """
        diffConts = ( ContactCenter, ContactEdge)

        for diffCont in self.getCompsSorted( objType=diffConts):
            diffCont.unlock()

            (cont, rect) = diffCont.getComps()
            if not isinstance( rect, Rect):
                ( cont, rect) = ( rect, cont)

            diffCont.contact        = cont
            diffCont.lowerRect      = rect
            diffCont.params.justify = direction
            diffCont.justify()

            diffCont.lock()

        # Minor recursion, since MosDummy derives from MosBody.
        for dummy in self.getCompsSorted( objType=MosDummy):
            dummy.unlock()
            dummy.justifyDiffContacts( direction)
            dummy.lock()

    ####################################################################

    def unwire(
        self,
        conn,
        wireLayer):
        """Remove wires (RouteRect) objects on requested layer.
            """
        box = conn.getBBox( ShapeFilter( wireLayer))

        for route in self.getCompsSorted( objType=RouteRect, layer=wireLayer):
            if box.overlaps( route.getBBox()):
                self.remove( route)
                route.destroy()

    ####################################################################

    def wireDiffConn(
        self,
        diffConn,
        direction,
        pattern):
        """Connect diffusion contacts to a CompoundComponent or Grouping
        connecting object, typically a ViaX.
            """
        metal1Filter  = ShapeFilter( self.params.metal1Layer)

        # Calculate bounding boxes.
        contacts = self.getCompsSorted( objType=(ContactCenter, ContactEdge))
        ctBox  = Box()
        for i in pattern:
            ctBox.merge( contacts[i].getBBox( metal1Filter))
        upperCenter = ctBox.upperCenter()
        lowerCenter = ctBox.lowerCenter()

        dcRect = diffConn.getComp( Rect)



        # Determine whether a gap exists that needs to be filled.
        gapExists = False
        if direction == Direction.NORTH:
            if diffConn.getBBox( metal1Filter).getBottom() < ctBox.getBottom():
                diffConn.alignEdgeToPoint( Direction.SOUTH, lowerCenter, filter=metal1Filter)

            if diffConn.getBBox( metal1Filter).getTop()    < ctBox.getTop():
                diffConn.alignEdgeToPoint( Direction.NORTH, upperCenter, filter=metal1Filter)

            if diffConn.getBBox( metal1Filter).getBottom() > ctBox.getTop():
                gapExists = True

        elif direction == Direction.SOUTH:
            if diffConn.getBBox( metal1Filter).getTop()    > ctBox.getTop():
                diffConn.alignEdgeToPoint( Direction.NORTH, upperCenter, filter=metal1Filter)

            if diffConn.getBBox( metal1Filter).getBottom() > ctBox.getBottom():
                diffConn.alignEdgeToPoint( Direction.SOUTH, lowerCenter, filter=metal1Filter)

            if diffConn.getBBox( metal1Filter).getTop()    < ctBox.getBottom():
                gapExists = True
        else:
            raise ValueError, "Must be Direction.NORTH or Direction.SOUTH."



        # Connect diffusion contacts.
        if gapExists:
            for i in pattern:
                target = [ c for c in contacts[i].getLeafComps() if c.getLayer() == self.params.metal1Layer][0]
                self.add(
                    RouteRect(
                        fromTarg  = target,
                        toTarg    = dcRect,
                        layer     = self.params.metal1Layer,
                        direction = direction,
                    )
                )

    ####################################################################

    def wireGateConn(
        self,
        gateConn,
        pattern):
        """Connect connecting object to transistor gates.
            """
        polyFilter  = ShapeFilter( self.params.gateLayer)

        # Calculate bounding boxes.
        gates  = self.getCompsSorted( objType=MosGate)
        gtBox  = Box()
        for i in pattern:
            gtBox.merge( gates[i].getBBox( polyFilter))

        gcRect = gateConn.getComp( Rect)
        gcBox  = gcRect.getBBox( polyFilter)



        # Determine whether a gap exists that needs to be filled.
        gapExists = False
        if gtBox.getCenterY() > gcBox.getCenterY():
            # Gate contact below gates.
            direction = Direction.SOUTH
            if gcBox.getTop()    < gtBox.getBottom():
                gapExists = True
        else:
            # Gate contact above gates.
            direction = Direction.NORTH
            if gcBox.getBottom() > gtBox.getTop():
                gapExists = True



        # Route to connecting object to gate.
        if gapExists:
            for i in pattern:
                target = [ c for c in gates[i].getLeafComps() if c.getLayer() == self.params.gateLayer][0]
                self.add(
                    RouteRect(
                        fromTarg  = gates[i].getCompsSorted( layer=self.params.gateLayer)[0],
                        toTarg    = gcRect,
                        layer     = self.params.gateLayer,
                        direction = direction,
                    )
                )

########################################################################

class MosBody1( MosBody):
    """MOS transistor with contact coverage parameter.
        """

    ####################################################################

    def __init__(
        self,
        diffLayer,
        gateLayer,
        metal1Layer,
        metal2Layer,
        contactLayer,
        nf,
        gateWidth,
        gateLength,
        coverage,
        diffLeftStyle,
        diffRightStyle,
        flip            = True,
        addRules        = RulesDict(),
        envLayers       = [],
        justify         = Direction.SOUTH,
        withGateContact = True):
        """Build a stack of MOS transistors.  Options:
        * Connect gates with a poly contact,
        * Connect source/drain contacts.
        * Wire width for connecting source/drain.
        * Source/drain contact coverage.
            """
        super( MosBody1, self).__init__( locals())
        scratchPad = Point( -10, -10)

        lowerEncE = RulesDict.makeKey("minExtension", self.params.diffLayer,   self.params.contactLayer, Direction.EAST)
        lowerEncW = RulesDict.makeKey("minExtension", self.params.diffLayer,   self.params.contactLayer, Direction.WEST)
        upperEncE = RulesDict.makeKey("minExtension", self.params.metal1Layer, self.params.contactLayer, Direction.EAST)
        upperEncW = RulesDict.makeKey("minExtension", self.params.metal1Layer, self.params.contactLayer, Direction.WEST)

        # Create templates
        # d = Left   diffusion w/ optional contact
        # b = Right  diffusion w/ optional contact
        # c = Center diffusion w/ required contact
        # G = Transistor gate

        # Gate
        G = MosGate(
            diffLayer  = diffLayer,
            gateLayer  = gateLayer,
            gateWidth  = gateWidth,
            gateLength = gateLength,
            addRules   = addRules,
        )
        G.moveTo( scratchPad)



        # Left side contact.
        cc = eval( self.params.diffLeftStyle)

        if issubclass( cc, ContactEdge):
            d = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                coverage           = coverage,
                justify            = justify,
                addRules           = addRules,
                envLayers          = envLayers,
            )
        elif issubclass( cc, MosDiffusion):
            d = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                addRules           = addRules,
                envLayers          = envLayers,
                withGateContact    = withGateContact,
            )
        elif issubclass( cc, MosDummy):
            d = cc(
                diffLayer          = diffLayer,
                gateLayer          = gateLayer,
                metal1Layer        = metal1Layer,
                nf                 = 1,
                gateWidth          = gateWidth,
                gateLength         = gateLength,
                coverage           = coverage,
                flip               = flip,
                addRules           = addRules,
                envLayers          = envLayers,
                justify            = justify,
            )
        else:
            raise ValueError, "Illegal value for self.params.diffLeftStyle - %s" % self.params.diffLeftStyle
        d.moveTo( scratchPad)



        # Center contact.
        c = ContactCenter1(
            lowerLayer             = diffLayer,
            upperLayer             = metal1Layer,
            gateLayer              = gateLayer,
            width                  = gateWidth,
            gateLength             = gateLength,
            coverage               = coverage,
            justify                = justify,
            addRules               = addRules,
            envLayers              = envLayers,
            withGateContact        = withGateContact,
        )
        c.moveTo( scratchPad)



        # Right side contact.  Swap direction to reflect mirroring.
        newAddRules = copy.copy( addRules)
        newAddRules[ lowerEncE] = addRules.get( lowerEncW, 0)
        newAddRules[ lowerEncW] = addRules.get( lowerEncE, 0)
        newAddRules[ upperEncE] = addRules.get( upperEncW, 0)
        newAddRules[ upperEncW] = addRules.get( upperEncE, 0)

        cc = eval( self.params.diffRightStyle)

        if issubclass( cc, ContactEdge):
            b = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                coverage           = coverage,
                justify            = justify,
                addRules           = newAddRules,
                envLayers          = envLayers,
            )
        elif issubclass( cc, MosDiffusion):
            b = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                addRules           = newAddRules,
                envLayers          = envLayers,
                withGateContact    = withGateContact,
            )
        elif issubclass( cc, MosDummy):
            b = cc(
                diffLayer          = diffLayer,
                gateLayer          = gateLayer,
                metal1Layer        = metal1Layer,
                nf                 = 1,
                gateWidth          = gateWidth,
                gateLength         = gateLength,
                coverage           = coverage,
                flip               = flip,
                addRules           = newAddRules,
                envLayers          = envLayers,
                justify            = justify,
            )
        else:
            raise ValueError, "Illegal value for self.params.diffRightStyle - %s" % self.params.diffRightStyle
        b.mirrorY( xCoord=b.getBBox().getLeft())
        b.moveTo( scratchPad)



        # Assemble the MOS device stack
        symbolMap = { "d":d, "b":b, "c":c, "G":G}
        sequence  = []

        sequence.append("d")
        sequence.append("G")

        for i in range( 1, nf):
            sequence.append("c")
            sequence.append("G")

        sequence.append("b")
        sequence = "".join( sequence)

        if flip:
            flip       = ( MosDummy, MosContact, MosDiffusion)
        else:
            flip       = ()

        mosStack = MosStack2(
            sequence   = sequence,
            symbolMap  = symbolMap,
            alignLayer = self.params.diffLayer,
            flip       = flip,
        )

        mosStack.ungroup( owner=self)
        self.alignDogboneContacts()
        self.lock()



        # Delete unused template pieces.
        c.destroy()
        G.destroy()

    ####################################################################

    def changeEndStyle(
        self,
        diffLeftStyle,
        diffRightStyle):
        """Replace left/right source/drain diffusion contacts.  One common
        use is the support of dummy transistor gates.
            """
        diffFilter = ShapeFilter( self.params.diffLayer)
        locations  = ( Location.LOWER_RIGHT, Location.LOWER_LEFT)

        self.params.diffLeftStyle  = diffLeftStyle
        self.params.diffRightStyle = diffRightStyle

        lowerEncE = RulesDict.makeKey("minExtension", self.params.diffLayer,   self.params.contactLayer, Direction.EAST)
        lowerEncW = RulesDict.makeKey("minExtension", self.params.diffLayer,   self.params.contactLayer, Direction.WEST)
        upperEncE = RulesDict.makeKey("minExtension", self.params.metal1Layer, self.params.contactLayer, Direction.EAST)
        upperEncW = RulesDict.makeKey("minExtension", self.params.metal1Layer, self.params.contactLayer, Direction.WEST)



        # Substitute requested left and right S/D diffusion.
        styles = ( diffLeftStyle, diffRightStyle)
        comps  = self.getCompsSorted( objType=( MosDiffusion, MosDummy, ContactCenter, ContactEdge))
        for i in ( 0, -1):
            diffStyle = eval( styles[ i])

            newAddRules = copy.copy( self.params.addRules)
            if i == -1:
                # Mirror for right side.
                newAddRules[ lowerEncE] = self.params.addRules.get( lowerEncW, 0)
                newAddRules[ lowerEncW] = self.params.addRules.get( lowerEncE, 0)
                newAddRules[ upperEncE] = self.params.addRules.get( upperEncW, 0)
                newAddRules[ upperEncW] = self.params.addRules.get( upperEncE, 0)

            if type( comps[ i]) != diffStyle:
                if issubclass( diffStyle, ContactEdge):
                    cc = diffStyle(
                        lowerLayer         = self.params.diffLayer,
                        upperLayer         = self.params.metal1Layer,
                        gateLayer          = self.params.gateLayer,
                        width              = self.params.gateWidth,
                        gateLength         = self.params.gateLength,
                        coverage           = self.params.coverage,
                        justify            = self.params.justify,
                        addRules           = newAddRules,
                        envLayers          = self.params.envLayers,
                    )
                elif issubclass( diffStyle, MosDiffusion):
                    cc = diffStyle(
                        lowerLayer         = self.params.diffLayer,
                        upperLayer         = self.params.metal1Layer,
                        gateLayer          = self.params.gateLayer,
                        width              = self.params.gateWidth,
                        gateLength         = self.params.gateLength,
                        addRules           = newAddRules,
                        envLayers          = self.params.envLayers,
                        withGateContact    = ( self.params.nf < 2),
                    )
                elif issubclass( diffStyle, MosDummy):
                    cc = diffStyle(
                        diffLayer          = self.params.diffLayer,
                        gateLayer          = self.params.gateLayer,
                        metal1Layer        = self.params.metal1Layer,
                        nf                 = 1,
                        gateWidth          = self.params.gateWidth,
                        gateLength         = self.params.gateLength,
                        coverage           = self.params.coverage,
                        flip               = self.params.flip,
                        justify            = self.params.justify,
                        addRules           = newAddRules,
                        envLayers          = self.params.envLayers,
                    )
                else:
                    raise ValueError, "Illegal value - %s" % styles[i]
                self.add( cc)

                # Place new S/D diffusion on either left or right.
                if i == -1:
                    # Mirror for right side.
                    cc.mirrorY( xCoord=cc.getBBox().getLeft())

                    if isEven( len( comps)) and self.params.flip:
                        cc.mirrorX( yCoord=cc.getBBox().getBottom())

                cc.alignLocation( locations[ i],  comps[ i], filter=diffFilter)

                # Remove unwanted prior S/D diffusion contact.
                if isinstance( cc, MosDiffusion):
                    self.unwire( comps[ i], self.params.metal1Layer)
                self.remove( comps[ i])
                comps[ i].destroy()

########################################################################

class MosBody2( MosBody):
    """MOS transistor with contact offset parameters.
        """

    ####################################################################

    def __init__(
        self,
        diffLayer,
        gateLayer,
        metal1Layer,
        contactLayer,
        nf,
        gateWidth,
        gateLength,
        diffLeftStyle,
        diffRightStyle,
        diffContactLeftBottomOffset,
        diffContactLeftTopOffset,
        diffContactCenterBottomOffset,
        diffContactCenterTopOffset,
        diffContactRightBottomOffset,
        diffContactRightTopOffset,
        addRules        = RulesDict(),
        envLayers       = [],
        withGateContact = True):
        """Build a stack of MOS transistors.  Options:
        * Connect gates with a poly contact,
        * Connect source/drain contacts.
        * Wire width for connecting source/drain.
        * Source/drain contact coverage.
            """
        super( MosBody2, self).__init__( locals())
        scratchPad = Point( -10, -10)

        lowerEncE = RulesDict.makeKey("minExtension", self.params.diffLayer,   self.params.contactLayer, Direction.EAST)
        lowerEncW = RulesDict.makeKey("minExtension", self.params.diffLayer,   self.params.contactLayer, Direction.WEST)
        upperEncE = RulesDict.makeKey("minExtension", self.params.metal1Layer, self.params.contactLayer, Direction.EAST)
        upperEncW = RulesDict.makeKey("minExtension", self.params.metal1Layer, self.params.contactLayer, Direction.WEST)

        # Create templates
        # d = Left   diffusion w/ optional contact
        # b = Right  diffusion w/ optional contact
        # c = Center diffusion w/ required contact
        # G = Transistor gate

        # Gate
        G = MosGate(
            diffLayer  = diffLayer,
            gateLayer  = gateLayer,
            gateWidth  = gateWidth,
            gateLength = gateLength,
            addRules   = addRules,
        )
        G.moveTo( scratchPad)



        # Left side contact.
        cc = eval( self.params.diffLeftStyle)

        if issubclass( cc, ContactEdge):
            d = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                bottomOffset       = diffContactLeftBottomOffset,
                topOffset          = diffContactLeftTopOffset,
                addRules           = addRules,
                envLayers          = envLayers,
            )
        elif issubclass( cc, MosDiffusion):
            d = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                addRules           = addRules,
                envLayers          = envLayers,
                withGateContact    = withGateContact,
            )
        elif issubclass( cc, MosDummy):
            d = cc(
                diffLayer          = diffLayer,
                gateLayer          = gateLayer,
                metal1Layer        = metal1Layer,
                nf                 = 1,
                gateWidth          = gateWidth,
                gateLength         = gateLength,
                bottomOffset       = diffContactLeftBottomOffset,
                topOffset          = diffContactLeftTopOffset,
                addRules           = addRules,
                envLayers          = envLayers,
            )
        else:
            raise ValueError, "Illegal value for self.params.diffLeftStyle - %s" % self.params.diffLeftStyle
        d.moveTo( scratchPad)




        # Center contact.
        c = ContactCenter2(
            lowerLayer             = diffLayer,
            upperLayer             = metal1Layer,
            gateLayer              = gateLayer,
            width                  = gateWidth,
            gateLength             = gateLength,
            bottomOffset           = diffContactCenterBottomOffset,
            topOffset              = diffContactCenterTopOffset,
            addRules               = addRules,
            envLayers              = envLayers,
            withGateContact        = withGateContact,
        )
        c.moveTo( scratchPad)



        # Right side contact.  Swap direction to reflect mirroring.
        newAddRules = copy.copy( addRules)
        newAddRules[ lowerEncE] = addRules.get( lowerEncW, 0)
        newAddRules[ lowerEncW] = addRules.get( lowerEncE, 0)
        newAddRules[ upperEncE] = addRules.get( upperEncW, 0)
        newAddRules[ upperEncW] = addRules.get( upperEncE, 0)

        cc = eval( self.params.diffRightStyle)

        if issubclass( cc, ContactEdge):
            b = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                bottomOffset       = diffContactRightBottomOffset,
                topOffset          = diffContactRightTopOffset,
                addRules           = newAddRules,
                envLayers          = envLayers,
            )
        elif issubclass( cc, MosDiffusion):
            b = cc(
                lowerLayer         = diffLayer,
                upperLayer         = metal1Layer,
                gateLayer          = gateLayer,
                width              = gateWidth,
                gateLength         = gateLength,
                addRules           = newAddRules,
                envLayers          = envLayers,
                withGateContact    = withGateContact,
            )
        elif issubclass( cc, MosDummy):
            b = cc(
                diffLayer          = diffLayer,
                gateLayer          = gateLayer,
                metal1Layer        = metal1Layer,
                nf                 = 1,
                gateWidth          = gateWidth,
                gateLength         = gateLength,
                bottomOffset       = diffContactRightBottomOffset,
                topOffset          = diffContactRightTopOffset,
                addRules           = newAddRules,
                envLayers          = envLayers,
            )
        else:
            raise ValueError, "Illegal value for self.params.diffRightStyle - %s" % self.params.diffRightStyle
        b.mirrorY( xCoord=b.getBBox().getLeft())
        b.moveTo( scratchPad)



        # Assemble the MOS device stack
        symbolMap = { "d":d, "b":b, "c":c, "G":G}
        sequence  = []

        sequence.append("d")
        sequence.append("G")

        for i in range( 1, nf):
            sequence.append("c")
            sequence.append("G")

        sequence.append("b")
        sequence = "".join( sequence)

        mosStack = MosStack2(
            sequence   = sequence,
            symbolMap  = symbolMap,
            alignLayer = self.params.diffLayer,
        )

        mosStack.ungroup( owner=self)
        self.alignDogboneContacts()
        self.lock()



        # Delete unused template pieces.
        c.destroy()
        G.destroy()

########################################################################

class MosDummy( MosBody):
    """MOS dummy transistors.
        """
    isAbutable = False

    def setPin(
        self,
        pinName,
        termName,
        layer = None):
        """Create pins for lower layer rectangle and contact for the
        inside diffusion contact that abuts the non-dummy transistor.
            """
        cc = self.getComp( ContactCenter)
        cc.setPin(
            pinName  = pinName,
            termName = termName,
            layer    = layer
        )

    def tieOff(
        self,
        pinName,
        termName,
        layers = []):
        """Create pins for lower layer rectangle and contact for the
        inside diffusion contact that abuts the non-dummy transistor.
            """
        cc = self.getComp( ContactEdge)
        cc.setPin(
            pinName  = pinName,
            termName = termName,
            layer    = layer
        )

        cc = self.getComps( MosGate)
        cc.setPin(
            pinName  = pinName,
            termName = termName,
            layer    = layer
        )

########################################################################

class MosDummy1( MosDummy):
    """MOS dummy transistors with contact coverage parameter.
        """

    ####################################################################

    def __init__(
        self,
        diffLayer,
        gateLayer,
        metal1Layer,
        nf,
        gateWidth,
        gateLength,
        coverage,
        flip               = True,
        addRules           = RulesDict(),
        envLayers          = [],
        justify            = Direction.SOUTH):
        """Build a stack of MOS transistors.  Options:
        * Connect gates with a poly contact,
        * Connect source/drain contacts.
        * Wire width for connecting source/drain.
        * Source/drain contact coverage.
            """
        super( MosDummy1, self).__init__( locals())
        scratchPad = Point( -10, -10)

        # Create templates
        # d = Left   diffusion w/ optional contact
        # b = Right  diffusion w/ optional contact
        # c = Center diffusion w/ required contact
        # G = Transistor gate

        # Gate
        G = MosGate(
            diffLayer  = diffLayer,
            gateLayer  = gateLayer,
            gateWidth  = gateWidth,
            gateLength = gateLength,
            addRules   = addRules,
        )
        G.moveTo( scratchPad)



        # Right side (outermost) contact.  Swap direction to reflect mirroring.
        b = ContactEdge1(
            lowerLayer         = diffLayer,
            upperLayer         = metal1Layer,
            gateLayer          = gateLayer,
            width              = gateWidth,
            gateLength         = gateLength,
            coverage           = coverage,
            justify            = justify,
            addRules           = addRules,
            envLayers          = envLayers,
        )
        b.moveTo( scratchPad)
        b.mirrorY( xCoord=b.getBBox().getLeft())



        # Center contact.
        c = ContactCenter1(
            lowerLayer         = diffLayer,
            upperLayer         = metal1Layer,
            gateLayer          = gateLayer,
            width              = gateWidth,
            gateLength         = gateLength,
            coverage           = coverage,
            justify            = justify,
            addRules           = addRules,
            envLayers          = envLayers,
            withGateContact    = False,
        )
        c.moveTo( scratchPad)



        # Assemble the MOS device stack
        symbolMap = { "b":b, "c":c, "G":G}
        sequence  = []

        sequence.append("c")
        sequence.append("G")

        for i in range( 1, nf):
            sequence.append("c")
            sequence.append("G")

        sequence.append("b")
        sequence = "".join( sequence)

        if flip:
            flip       = ( MosContact, MosDiffusion)
        else:
            flip       = ()

        mosStack = MosStack2(
            sequence   = sequence,
            symbolMap  = symbolMap,
            alignLayer = self.params.diffLayer,
            flip       = flip,
        )
        mosStack.mirrorY( xCoord=mosStack.getBBox().getLeft())

        mosStack.ungroup( owner=self)
        self.alignDogboneContacts()
        self.lock()



        # Delete unused template pieces.
        G.destroy()

########################################################################

class MosDummy2( MosDummy):
    """MOS dummy transistors with contact offset parameters.
        """

    ####################################################################

    def __init__(
        self,
        diffLayer,
        gateLayer,
        metal1Layer,
        nf,
        gateWidth,
        gateLength,
        bottomOffset,
        topOffset,
        addRules           = RulesDict(),
        envLayers          = []):
        """Build a stack of MOS transistors.  Options:
        * Connect gates with a poly contact,
        * Connect source/drain contacts.
        * Wire width for connecting source/drain.
        * Source/drain contact coverage.
            """
        super( MosDummy2, self).__init__( locals())
        scratchPad = Point( -10, -10)

        # Create templates
        # d = Left   diffusion w/ optional contact
        # b = Right  diffusion w/ optional contact
        # c = Center diffusion w/ required contact
        # G = Transistor gate

        # Gate
        G = MosGate(
            diffLayer  = diffLayer,
            gateLayer  = gateLayer,
            gateWidth  = gateWidth,
            gateLength = gateLength,
            addRules   = addRules,
        )
        G.moveTo( scratchPad)



        # Right side contact.
        b = ContactEdge2(
            lowerLayer         = diffLayer,
            upperLayer         = metal1Layer,
            gateLayer          = gateLayer,
            width              = gateWidth,
            gateLength         = gateLength,
            bottomOffset       = bottomOffset,
            topOffset          = topOffset,
            addRules           = addRules,
            envLayers          = envLayers,
        )
        b.moveTo( scratchPad)
        b.mirrorY( xCoord=b.getBBox().getLeft())



        # Center contact.
        c = ContactCenter2(
            lowerLayer         = diffLayer,
            upperLayer         = metal1Layer,
            gateLayer          = gateLayer,
            width              = gateWidth,
            gateLength         = gateLength,
            bottomOffset       = bottomOffset,
            topOffset          = topOffset,
            addRules           = addRules,
            envLayers          = envLayers,
            withGateContact    = False,
        )
        c.moveTo( scratchPad)



        # Assemble the MOS device stack
        symbolMap = { "b":b, "c":c, "G":G}
        sequence  = []

        sequence.append("c")
        sequence.append("G")

        for i in range( 1, nf):
            sequence.append("c")
            sequence.append("G")

        sequence.append("b")
        sequence = "".join( sequence)

        mosStack = MosStack2(
            sequence   = sequence,
            symbolMap  = symbolMap,
            alignLayer = self.params.diffLayer,
        )
        mosStack.mirrorY( xCoord=mosStack.getBBox().getLeft())

        mosStack.ungroup( owner=self)
        self.alignDogboneContacts()
        self.lock()



        # Delete unused template pieces.
        G.destroy()

########################################################################

class MosStack1( MosCC):
    """Build a stack of MOS transistors based on a symbolMap, which
    defines a mapping of building blocks. and a sequence, which defines
    the placement order.
        """

    ####################################################################

    def __init__(
        self,
        diffLayer,
        metalLayer,
        sequence,
        symbolMap,
        alignLayer,
        flip = []):
        """Create the MosStack.
            """
        super( MosStack1, self).__init__( locals())

        comps = []
        alignFilter = ShapeFilter( alignLayer)

        ref = symbolMap[ sequence[0]].clone()
        self.add( ref)
        comps.append( ref)
        ref.moveTo( Point(0, 0), loc=Location.LOWER_RIGHT, filter=alignFilter)

        for c in sequence[1:]:
            comp = symbolMap[c].clone()
            self.add( comp)

            comp.place( Direction.EAST, ref, 0)
            comp.alignEdge( Direction.SOUTH, ref, filter=alignFilter)
            comps.append( comp)
            ref = comp

        if flip:
            comps = [ c for c in comps if isinstance( c, flip)]
            ref   = comps[0]
            i     = 1
            for comp in comps[1:]:
                if isOdd( i):
                    comp.mirrorX( yCoord=comp.getBBox().getBottom())
                    comp.alignEdge( Direction.SOUTH, ref, filter=alignFilter)
                i += 1

########################################################################

class MosStack2( MosCC):
    """Build a stack of MOS transistors based on a symbolMap, which
    defines a mapping of building blocks. and a sequence, which defines
    the placement order.

    Differs from MosStack1 by *not* cloning leftmost and rightmost element,
    for increased efficiency.
        """

    ####################################################################

    def __init__(
        self,
        sequence,
        symbolMap,
        alignLayer,
        flip = []):
        """Create the MosStack.
            """
        super( MosStack2, self).__init__( locals())

        comps = []
        alignFilter = ShapeFilter( alignLayer)

        ref = symbolMap[ sequence[0]]
        self.add( ref)
        comps.append( ref)
        ref.moveTo( Point(0, 0), loc=Location.LOWER_RIGHT, filter=alignFilter)

        for c in sequence[1:-1]:
            comp = symbolMap[c].clone()
            self.add( comp)

            comp.place( Direction.EAST, ref, 0)
            comp.alignEdge( Direction.SOUTH, ref, filter=alignFilter)
            comps.append( comp)
            ref = comp

        comp = symbolMap[ sequence[-1]]
        self.add( comp)
        comps.append( comp)
        comp.place( Direction.EAST, ref, 0)
        comp.alignEdge( Direction.SOUTH, ref, filter=alignFilter)

        if flip:
            comps = [ c for c in comps if isinstance( c, flip)]
            ref   = comps[0]
            i     = 1
            for comp in comps[1:]:
                if isOdd( i):
                    comp.mirrorX( yCoord=comp.getBBox().getBottom())
                    comp.alignEdge( Direction.SOUTH, ref, filter=alignFilter)
                i += 1

########################################################################

class GuardRing( MosCC):
    """Custom guard ring, which can result in smaller area than ContactRing
    in some situations, because of more sophisticated, but compute-intensive,
    well calculation.
        """

    ####################################################################

    def __init__(
        self,
        comps,
        lowerLayer,
        upperLayer,
        locations    = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST],
        encLayers    = None,
        implantLayer = None):

        super( GuardRing, self).__init__( locals())

        metFilter  = ShapeFilter( upperLayer)
        implants   = ( LayerMaterial.PIMPLANT, LayerMaterial.NIMPLANT)

        if encLayers:
            fillLayers = [ l for l in encLayers if l.getMaterial() not in implants]
        else:
            fillLayers = []

        encLayers1 = copy.copy( fillLayers)
        if implantLayer:
            encLayers1.append( implantLayer)

        # Delete fill layers, which will be added after guard ring
        # is completed.
        comp = BorrowGrouping()
        for c in comps:
            if isinstance( c, Rect) and c.getLayer() in fillLayers:
                c.destroy()
            else:
                comp.add( c)
        box  = comp.getBBox()



        # Create and place substrate contact on each side.
        grp  = {}
        cont = {}
        impl = {}

        params = {
            Direction.NORTH : ("centerLeft",  "centerRight"),
            Direction.SOUTH : ("centerLeft",  "centerRight"),
            Direction.EAST  : ("lowerCenter", "upperCenter"),
            Direction.WEST  : ("lowerCenter", "upperCenter"),
        }

        for loc in locations:
            field = params[ loc]
            perpendicular = loc.perpendicular()
            cont[ loc] = AbutContact(
                layer1    = lowerLayer,
                layer2    = upperLayer,
                routeDir1 = perpendicular,
                routeDir2 = perpendicular,
                point1    = getattr( box, field[0])(),
                point2    = getattr( box, field[1])(),
                abutDir   = perpendicular,
                abutViaSpaceFactor = 2,
            )

            rects  = EnclosingRects( cont[ loc], encLayers1, grid=self.grid).ungroupAsList()
            grp[ loc] = Grouping( components=cont[ loc])

            for rect in rects:
                if rect.getLayer() in fillLayers:
                    # Delete unwanted rectangles, which was generated as a
                    # by-product of having EnclosingRects() calculate proper
                    # implant overlap for a substrate contact diffusion.
                    rect.destroy()
                else:
                    impl[ loc] = rect
                    grp[ loc].add( rect)

            grp[ loc].place( loc, comp, 0)
            self.add( grp[loc])

        # Place substrate contacts according to design rules.
        self.add( comp)
        env = EnclosingRectsBBox( self, fillLayers)
        for loc in locations:
            ggPlace( grp[ loc], loc, comp, env=env, grid=self.grid)
        env.destroy()



        # Abut ends of each AbutContact by stretching.
        stretch = {
            Direction.NORTH : (( Direction.EAST,  "centerLeft",  "getRight"), ( Direction.WEST,  "centerRight", "getLeft"  )),
            Direction.SOUTH : (( Direction.EAST,  "centerLeft",  "getRight"), ( Direction.WEST,  "centerRight", "getLeft"  )),
            Direction.EAST  : (( Direction.NORTH, "upperCenter", "getTop"  ), ( Direction.SOUTH, "lowerCenter", "getBottom")),
            Direction.WEST  : (( Direction.NORTH, "upperCenter", "getTop"  ), ( Direction.SOUTH, "lowerCenter", "getBottom")),
        }

        for loc in locations:
            for field in stretch[ loc]:
                abutDir = field[ 0]

                if abutDir in cont:
                    # Stretch contact
                    abutBox  = cont[ abutDir].getBBox()
                    cont[ loc].stretchTo( abutDir, getattr( abutBox, field[1])())

                    # Stretch implant
                    abutBox  = impl[ abutDir].getBBox()
                    box      = impl[ loc].getBBox()
                    distance = abs( getattr( box, field[2])() - getattr( abutBox, field[2])())
                    impl[ loc].setBBox( box.expand( abutDir, distance))
                    
            # Add metal1 rectangle for pin.
            self.add( Rect( upperLayer, cont[ loc].getBBox( metFilter)))



        # Assign proper ownership.
        for loc in locations:
            grp[ loc].ungroup( owner=self)

        # Add enclosing layers.
        if fillLayers:
            fills = EnclosingRects( self, fillLayers, grid=self.grid)
            rects = fills.getComps()
            fills.ungroup( owner=self)

            # Force minimum size to match guard ring boundary.
            self.remove( comp)
            box = self.getBBox()
            for rect in rects:
                rect.setBBox( rect.getBBox().merge( box))
        else:
            self.remove( comp)



        # If MosBody, adjust for abutment
        row   = [ c for c in comps if isinstance( c, MosBody)]
        if row:
            row = row[ 0]
            ccs   = row.getCompsSorted( objType=( MosDiffusion, ContactEdge, MosDummy ))
            rects = self.getCompsSorted( objType=Rect)

            # Left edge adjustment for abutment.
            if hasattr( ccs[0], "isAbutable") and ccs[0].isAbutable:
                edge = ccs[0].getBBox().getLeft()

                for rect in rects:
                    box = rect.getBBox()
                    if box.getLeft() < edge:
                        box.setLeft( edge)
                        rect.setBBox( box)

            # Right edge adjustment for abutment.
            if hasattr( ccs[-1], "isAbutable") and ccs[-1].isAbutable:
                edge = ccs[-1].getBBox().getRight()

                for rect in rects:
                    box = rect.getBBox()
                    if box.getRight() > edge:
                        box.setRight( edge)
                        rect.setBBox( box)



        # Clean-up.
        comp.ungroup()
        self.lock()

    ####################################################################

    @staticmethod
    def convertStringToList( sides):
        """ Convert guard ring locations from string to list.
            """
        sides = [ s.strip() for s in sides.split(",") if s]

        directions = dict(
            top    = Direction.NORTH,
            bottom = Direction.SOUTH,
            left   = Direction.WEST,
            right  = Direction.EAST,
        )

        for i in range( len( sides)):
            if sides[ i] in directions:
                sides[ i] = directions[ sides[ i]]
            else:
                raise ValueError, "Unsupported guard ring direction - %s.  Should be top,bottom,left,right." % sides[ i]

        return( sides)

    ####################################################################

    def setPin(
        self,
        pinName,
        termName):
        """Create pin for guard ring metal1.
            """
        rects = self.getCompsSorted( objType=Rect, layer=self.params.upperLayer)
        pin   = Pin.find( pinName)

        if pin:
            pin.addShape( rects)
        else:
            Pin( pinName, termName).addShape( rects)

########################################################################
#                                                                      #
# Methods below this line need to be updated.                          #
#                                                                      #
########################################################################

class MosStackMap( MosCC):
    """Build a stack of MOS transistors based on an option, sequence,
    which defines a mapping of building blocks.  Example:
    
    sequence = "dGcGcGoGb"

    symbolMap = [
        Dictionary( key="d", ccType="MosSD", subType="edge",   coverage=0.5, justify=Direction.NORTH,       orient=None),
        Dictionary( key="b", ccType="MosSD", subType="edge",   coverage=0.5, justify=Direction.NORTH,       orient="mirrorY"),
        Dictionary( key="G", ccType="MosGate" ),
        Dictionary( key="c", ccType="MosSD", subType=None,     coverage=0.0, justify=Direction.NORTH_SOUTH, orient=None),
        Dictionary( key="o", ccType="MosSD", subType="center", coverage=0.5, justify=Direction.NORTH_SOUTH, orient=None),
    ]
        """
    def __init__(
        self,
        diffLayer,
        polyLayer,
        metalLayer,
        chanWidth,
        gateLength,
        sequence,
        symbolMap):
        """Create the MosStack.
            """
        scratchPad = Point( -10, -10)
        cComp = Dictionary()

        # Build template pieces
        for cc in symbolMap:
            key = cc.key
            ccType = cc.ccType

            if ccType == "MosGate":
                cComp[ key] = MosGate(
                    diffLayer=diffLayer,
                    polyLayer=polyLayer,
                    chanWidth=chanWidth,
                    gateLength=gateLength,
                )

            elif ccType == "MosSD":
                cComp[ key] = MosSD(
                    diffLayer=diffLayer,
                    polyLayer=polyLayer,
                    chanWidth=chanWidth,
                    gateLength=gateLength,
                    metalLayer=metalLayer,
                    contact=cc.subType,
                    coverage=cc.coverage,
                    justify=cc.justify,
                )

            else:
                raise TypeError, "Must be either \"gate\" or \"sd\"."

            if cc.has_key("orient") and cc.orient:
                apply( getattr( cComp[ key], cc.orient), [])

            cComp[ key].moveTo( scratchPad)



        # Clone and place.
        MosStackBase.__init__(
            self,
            diffLayer=diffLayer,
            metalLayer=metalLayer,
            sequence=sequence,
            symbolMap=cComp,
            alignLayer=diffLayer,
        )



        # Delete the template pieces.
        for comp in cComp.values():
            if comp:
                comp.destroy()

        self.lock()



class MosStackSequence( MosCC):
    """Assemble a sequence of building blocks to make a stack of MOS
    transistors.  Building blocks consist of source/drain diffusions
    and transistor poly gates.  Simplified version of MosStack with
    less flexibility.
        """
    def __init__(
        self,
        diffLayer,
        polyLayer,
        metalLayer,
        chanWidth,
        gateLength,
        sequence,
        coverage,
        justify):
        """Create MosStackSequence.
            """
        symbolMap = [
            Dictionary( key="d", ccType="MosSD", subType="edge",   coverage=coverage, justify=justify),
            Dictionary( key="b", ccType="MosSD", subType="edge",   coverage=coverage, justify=justify, orient="mirrorY"),
            Dictionary( key="c", ccType="MosSD", subType=None,     coverage=coverage, justify=justify),
            Dictionary( key="o", ccType="MosSD", subType="center", coverage=coverage, justify=justify),
            Dictionary( key="G", ccType="MosGate"),
        ]

        MosStack.__init__(
            self,
            diffLayer=diffLayer,
            polyLayer=polyLayer,
            metalLayer=metalLayer,
            chanWidth=chanWidth,
            gateLength=gateLength,
            sequence=sequence,
            symbolMap=symbolMap,
        ) 



class MosStackSimple( MosCC):
    """Assemble a sequence of building blocks to make a stack of MOS
    transistors.  Building blocks consist of source/drain diffusions
    and transistor poly gates.  Simplified version of MosStack with
    less flexibility.
        """
    def __init__(
        self,
        diffLayer,
        polyLayer,
        metalLayer,
        chanWidth,
        gateLength,
        gates,
        centerContacts,
        coverage,
        justify):
        """Create MostStackSimple.
            """
        sequence = ["d", "G"]
        for i in range( 1, gates):
            sequence.append("c")
            sequence.append("G")

        sequence.append("b")
        sequence = "".join( sequence)

        symbolMap = [
            Dictionary( key="d", ccType="MosSD", subType="edge",   coverage=coverage, justify=justify),
            Dictionary( key="b", ccType="MosSD", subType="edge",   coverage=coverage, justify=justify, orient="mirrorY"),
            Dictionary( key="G", ccType="MosGate"),
        ]

        if centerContacts:
            symbolMap.append(
                Dictionary( key="c", ccType="MosSD", subType="center", coverage=coverage, justify=justify),
            )
        else:
            symbolMap.append(
                Dictionary( key="c", ccType="MosSD", subType=None,     coverage=coverage, justify=justify),
            )

        MosStack.__init__(
            self,
            diffLayer=diffLayer,
            polyLayer=polyLayer,
            metalLayer=metalLayer,
            chanWidth=chanWidth,
            gateLength=gateLength,
            sequence=sequence,
            symbolMap=symbolMap,
        ) 

# end
