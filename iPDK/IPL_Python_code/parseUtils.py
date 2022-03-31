#################################  COPYRIGHT  #################################
#                                                                             #
#  Copyright (c) 2007-2008 by Ciranova, Inc. All rights reserved.             #
#                                                                             #
#  Ciranova PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.        #
#                                                                             #
#################################  COPYRIGHT  #################################

########################################################################
#                                                                      #
# parseUtils.py                                                        #
#                                                                      #
########################################################################
"""
Module: parseUtils

This module implements basic parsing utilities for S-Expression parse trees
"""


class SETNode(object):
    """
    SExpressionTree Node class
    """
    def __init__(self, value=None,parent=None):
        self.value=value
        self.parent=parent
        self.children=[]
        
    def FindMatchingChild(self,tagValue):
        for child in self.children:
            if(child.value == tagValue): return child

        #if we made it here, node wasn't found
        raise Exception,'Expression Node \"'+tagValue+'\" is missing.'
    
    def MatchingChildExists(self, tagValue):
        for child in self.children:
            if(child.value == tagValue): return True #found a match
        
        return False #if made it here, no matches found

    def FindMatchingChildren(self, tagValue):
        matches=[]

        for child in self.children:
            if(child.value == tagValue): matches.append(child)

        return matches

    def getChildValue(self):
        # Get single child value. Raise exception if node does not have
        # unique single child.
        if len(self.children) != 1:
            raise RuntimeError("No unique single child")
        return self.children[0].value

    def getChildrenValue(self):
        # Get children values as list.
        return [getattr(x, 'value') for x in self.children]

    def setChildValue(self, newValue):
        # Set single child value. Raise exception if node does not have
        # unique single child.
        if len(self.children) != 1:
            raise RuntimeError("No unique single child")
        self.children[0].value=newValue    
    
class TraversalObject(object):
    """
    TraversalObject class
    """
    def __init__(self):
        self.level=0
        self.nodeRef=None
    
class SExpressionTree(object):
    """
    Tree class to represent S-Expression parse trees
    """
 
    def __init__(self,exprDelimiterIn='(', exprDelimiterOut=')', commentChar=';'):
        """
        Ctor -- just makes empty tree
        """
        #various delimiters of interest
        self.exprDelimiterIn=exprDelimiterIn
        self.exprDelimiterOut=exprDelimiterOut
        self.commentChar=commentChar
        self.rootNode=None
        
    def SETFromFile(self,inFileName, rootNodeName):
        """
        SETFromFile -- parses input file and builds tree
        """
        #if this tree already had nodes, detach them now
        self.rootNode=None
        
        #open the inFile stream
        inFile=open(inFileName,'r')

        #pre-process file then read into sstream for easier parsing
        ss=''
        inDelimCnt=0
        outDelimCnt=0
        while True:
            #read character by character (assumes each char is one byte)
            c=inFile.read(1)
            if(len(c) == 0): break  #end of file

            #if comment, then skip remainder of line
            if(c == self.commentChar): inFile.readline() #comment, skip remainder of line
            elif(c == self.exprDelimiterIn):
                ss+=' ' + c + ' ' #add space around delimiters, so easier to find later
                inDelimCnt+=1
            elif(c == self.exprDelimiterOut):
                ss+=' ' + c + ' ' #add space around delimiters, so easier to find later
                outDelimCnt+=1
            else: ss+= c #just a regular character...

        #check S-expression consistency
        if(inDelimCnt != outDelimCnt): raise Exception, 'Malformed S-Expression.  Missing delimiters.'

        #find the root node -- this must be a unique name; otherwise, it will just visit the first one
        foundRootNode=False
        tokens=ss.split()  #split into tokens
        for i in range(len(tokens)):
            if(tokens[i] == rootNodeName):
                foundRootNode=True
                rootTokenIndex=i
                break
            
        #check file consistency
        if(not foundRootNode): raise Exception,'Cannot find rootNode '+rootNodeName+'.'

        #add root node to tree
        self.rootNode=SETNode(tokens[rootTokenIndex])
        #discard tokens we've already looked at
        tokens=tokens[rootTokenIndex+1:]
        #make sure root parent is None, or some methods will break
        self.rootNode.parent=None

        #
        #parse and build the expression tree
        #
        potentialParent=self.rootNode
        parentStack=stack()
        priorWasInDelim=False
        for token in tokens:
            if(token == self.exprDelimiterOut):
                parentStack.pop() #move up one parent
                if(parentStack.empty()): break #we're back at the top -- so, we're done
                priorWasInDelim=False
            elif(token == self.exprDelimiterIn):
                #consistency check
                if(priorWasInDelim): raise Exception,'Malformed S-Expression. Consecutive in-delimiters not allowed.'
                #move down one level
                parentStack.push(potentialParent)
                priorWasInDelim=True
            else:
                #make new child
                child=SETNode(token)

                #set child/parent relationship
                parentStack.top().children.append(child)
                child.parent=parentStack.top()

                #mark the child as next potential parent node
                potentialParent=child

                priorWasInDelim=False

        #check S-expression consistency
        if(not parentStack.empty()): raise Exception,'Malformed S-Expression!'

        #close the inFile
        inFile.close()
    
    def SetRootNode(self,setNode):
        self.rootNode=setNode
        self.rootNode.parent=None
            
    def GetRootNode(self):
        return self.rootNode
        
    def FindNodeByTag(self,tagValue):
        travSeq=self.LevelOrderTraverse()
        for to in travSeq:
            if(to.nodeRef.value == tagValue): return to.nodeRef
        
        return None  # node not found
    
    def FindNodesByTag(self,tagValue):
        travSeq=self.LevelOrderTraverse()
        nodeList=[]
        for to in travSeq:
            if(to.nodeRef.value == tagValue):
                nodeList.append(to.nodeRef)
        
        return nodeList


    def LevelOrderTraverse(self,rootNode=None):
        """
        LevelOrderTraversal
        """
        if(self.rootNode == None): return []
                
        if(rootNode == None): rootNode=self.rootNode
        #use queue-based approach
        nodeQueue=queue()
        levelQueue=queue()
        front=SETNode()
        levelFront=0
        traversalSequence=[]

        #start from nodeID
        nodeQueue.push(rootNode)
        levelQueue.push(levelFront) #root node is level 0
        while(not nodeQueue.empty()):
            front=nodeQueue.front()
            levelFront=levelQueue.front()
            nodeQueue.pop()
            levelQueue.pop()

            to=TraversalObject()
            to.nodeRef=front
            to.level=levelFront
            traversalSequence.append(to)

            numChildren=len(front.children)
            if(numChildren != 0):
                for k in range(numChildren):
                    nodeQueue.push(front.children[k])
                    levelQueue.push(levelFront+1) #parent's level plus 1

        return traversalSequence



class stack(object):
    """
    Stack class -- emulates interface and functionality of C++ STL stack, to some degree
    """
    def __init__(self):
        self.stack=[]
        
    def push(self,item):
        self.stack.append(item)
        
    def pop(self):
        self.stack.pop()
        
    def empty(self):
        if(len(self.stack) == 0): return True
        else: return False
        
    def size(self):
        return len(self.stack)
    
    def top(self):
        return self.stack[-1]

class queue(object):
    """
    Queue class -- emulates interface and functionality of C++ STL queue, to some degree
    """
    def __init__(self):
        self.queue=[]
        
    def push(self,item):
        self.queue.append(item)
        
    def pop(self):
        self.queue.pop(0)
        
    def empty(self):
        if(len(self.queue) == 0): return True
        else: return False
        
    def size(self):
        return len(self.queue)
    
    def front(self):
        return self.queue[0]
    
    def back(self):
        return self.queue[-1]

        
        
