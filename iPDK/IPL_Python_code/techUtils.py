########################################################################
# Copyright (c) 2001-2008 by Ciranova, Inc. All rights reserved.          #
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
# TechUtils.py                                                          #
#                                                                      #
########################################################################
"""
Module: techUtils

This module implements a utility class for Technology Access.
"""


########################################################################
#                                                                      #
# Packages                                                             #
#                                                                      #
########################################################################

from cni.dlo import (
    Layer,
    LayerMaterial,
    Box,
    Rect,
    Grouping,
    Direction
)

from cni.utils import (
    getMinExtensions,
    getMinClearance
)

def  orderedRuleset(tech, rulesets):
    #
    # check to see if the requested ruleset exists for technology file.
    # If not, then try next available ruleset for the technology file.
    # If none of the requested rulesets exists, raise value exception.
    #

    rulesetNames = [ruleset.name  for ruleset in tech.getRulesets()]

    for name in rulesets:
        if name in rulesetNames:
            return(name)

    raise ValueError, "No supported ruleset for technology file"


def deviceContextExists(tech, contextName):
    #
    # check to see if the requested device context exists for technology file.
    #

    for context in tech.getDeviceContexts():
        if context.getName() == contextName:
            return(True)

    return(False)


def getNumMetalLayers(tech):
    # iterate through all mask layers defined in technology
    # file to determine the total number of metal layers
    numMetalLayers = 0
    for name in tech.getSantanaLayerNames():
        layer = Layer(name)
        if layer.isMaskLayer():
            if layer.getMaterial() == LayerMaterial.METAL:
                numMetalLayers = numMetalLayers + 1
    return(numMetalLayers)


def getAllMetalLayers(tech):
    # Get all metal layers sorted from metal1 to metalN.
    # iterate through all mask layers defined in technology file
    # to build list of metal layers for these index values.
    metalLayers = []
    for name in tech.getSantanaLayerNames():
        layer = Layer(name)
        if layer.isMaskLayer():
            if layer.getMaterial() == LayerMaterial.METAL:
                metalLayers.append(layer)
    # also sort this list of metal layers by mask number
    metalLayers.sort(lambda x,y : {True:1, False:-1} [x.isAbove(y)])
    return metalLayers

def getMetalLayer(tech, metalLayerIndex):
    # Get metal layer corresponding to metal layer index.
    # Metal layer index starts at 1.
    metalLayers = getAllMetalLayers(tech)
    return metalLayers[metalLayerIndex-1]

def getMetalLayers(tech, bottomIndex, topIndex):
    # Get metal layers from bottomIndex to topIndex
    metalLayers = getAllMetalLayers(tech)
    # extract the range of metal layers for these index values
    metalLayers = metalLayers[bottomIndex-1 : topIndex]

    return(metalLayers)

def getMaxWidthRule(tech, layer, noRuleValue=None):
    # Get maximum width rule for layer.
    # Return noRuleValue if rule does not exist.
    if tech.physicalRuleExists("maxWidth", layer):
        maxWidth = tech.getPhysicalRule("maxWidth", layer)
    else:
        maxWidth = noRuleValue
    return maxWidth

def getMinClearanceRule(tech, layer1, layer2, noRuleValue=None):
    # Get min clearance rule between two layers.
    # If the result cannot be obtained,
    # return noRuleValue (if noRuleValue is specified)
    # or 
    # raise an exception (if noRuleValue is None).
    result = getMinClearance(tech, layer1, layer2)
    if result == None:
        if noRuleValue == None:
            raise ValueError, "Cannot determine clearance between %s and %s. Make sure the techfile contains 'minClearance' rule." % (layer1, layer2)
        else:
            result = noRuleValue
    return result

def getMinExtensionRule(tech, outerLayer, innerLayer, width = None, noRuleValue = None):
    # Get min extension rule for outerLayer over innerLayer.
    # The 'width' parameter can be used when the rule is a conditional rule
    # depending on the width of the outer shape.
    # If the result cannot be obtained,
    # return noRuleValue (if noRuleValue is specified)
    # or 
    # raise an exception (if noRuleValue is None).
    result = getMinExtensions(tech, outerLayer, innerLayer, width)[0]
    if result == None:
        if noRuleValue == None:
            raise ValueError, "Cannot determine %s extension over %s. Make sure the techfile contains 'minExtension' or 'minDualExtension' rule." % (outerLayer, innerLayer)
        else:
            result = noRuleValue
    return result

def getMinEndOfLineExtensionRule(tech, outerLayer, innerLayer, width = None, noRuleValue = None):
    # Get min end-of-line extension rule for outerLayer over innerLayer.
    # Use regular extension rule if end-of-line extension is not specified.
    # The 'width' parameter can be used when the rule is a conditional rule
    # depending on the width of the outer shape.
    # If the result cannot be obtained,
    # return noRuleValue (if noRuleValue is specified)
    # or 
    # raise an exception (if noRuleValue is None).
    extensions = getMinExtensions(tech, outerLayer, innerLayer, width)
    if extensions[0] == None:
        result = extensions[1]
    elif extensions[1] == None:
        result = extensions[0]
    else:
        result = max(extensions[0], extensions[1])
    if result == None:
        if noRuleValue == None:
            raise ValueError, "Cannot determine %s extension over %s. Make sure the techfile contains 'minExtension' or 'minDualExtension' rule." % (outerLayer, innerLayer)
        else:
            result = noRuleValue
    return result

def getMinSymmetricExtensionRule(tech, outerLayer, innerLayer, width = None, noRuleValue = None):
    # Get min symmetric extension rule for outerLayer over innerLayer.
    # Use regular extension rule if symmetric extension is not specified.
    # The 'width' parameter can be used when the rule is a conditional rule
    # depending on the width of the outer shape.
    # If the result cannot be obtained,
    # return noRuleValue (if noRuleValue is specified)
    # or 
    # raise an exception (if noRuleValue is None).
    extensions = getMinExtensions(tech, outerLayer, innerLayer, width)
    if extensions[2] != None:
        result = extensions[2]
    elif extensions[0] == None:
        result = extensions[1]
    elif extensions[1] == None:
        result = extensions[0]
    else:
        result = max(extensions[0], extensions[1])
    if result == None:
        if noRuleValue == None:
            raise ValueError, "Cannot determine %s extension over %s. Make sure the techfile contains 'minExtension' or 'minDualExtension' rule." % (outerLayer, innerLayer)
        else:
            result = noRuleValue
    return result


def getMetalMinSpacingRule(tech, bottomLayerIndex, topLayerIndex, width, length):
    # Get metal min spacing rule for a stack of metal rectangles on
    # consecutive layers from 'topLayer' to 'botLayer'.
    # The size of each metal is a Rect generated with Box(0,0,width,length)
    # It is expected that width <= length
    rectBox = Box(0,0,width,length)
    g1 = Grouping()
    for layerIndex in range(bottomLayerIndex, topLayerIndex+1):
        metLayer = getMetalLayer(tech, layerIndex)
        g1.add(Rect(metLayer,rectBox))
    g2 = g1.clone()
    minSpace = g2.fgMinSpacing(Direction.EAST,g2)
    g1.destroy()
    g2.destroy()
    return minSpace
