


# "bd {sn sn, ho ho hc}"
# for a tree, you 


# "{{bd bd, ho ho hc} {~ sn:2 ~, ~ cp}, {bin bin ~, ~ bottle ~ cp}} "


import itertools
import copy
import random


#other node types needed: SquareBracket, 




#render for () and <> (random and "next") - must wrap a single {} or []
#	render children totally 
#	select appropriate rendered child
#for {} expressions, this could lead to the length of the full expression
#	to be greater than "1". Alternatively, children which are "too long" 
#	could be stateful and are cut off and remember their position to start 
#	next, just like with a normal {} (the state would be stored in the
#	() or <> node)

#every top level expression can (should?) be considered as wrapped in a []
#	for ease of computation

#for expression containing a x-node, the grandparent of the expression with 
#	the x-term must handle it. eg {ax5, b d c}, the {}  is the grandparent
#	of the ax5


def flattenChildren(childList):
	timeToTuple = {} #combine the children 
	for timePitchTuple in itertools.chain.from_iterable(childList):
		if timePitchTuple[0] not in timeToTuple:
			timeToTuple[timePitchTuple[0]] = timePitchTuple
		else:
			timeToTuple[timePitchTuple[0]] = (timePitchTuple[0], timeToTuple[timePitchTuple[0]][1] | timePitchTuple[1])

	return sorted(timeToTuple.values(), None, lambda tup: tup[0])

def mergeRenderedChildren(childFrac, children):
	merge = []
	for i in range(len(children)):
		timeShift = lambda timePitchTuple: (timePitchTuple[0]+(i*childFrac), timePitchTuple[1])
		merge += map(timeShift, children[i])
	#print "merge", childFrac, merge 
	return merge



#node.frac is the length (in beats) of a chunk returned from a call to "render"
#TODO: make sure the above is actually true in all the code 

class PydalNode:
	def __init__(self, children):
		self.children = children
		self.frac = sum(map(lambda c : c.frac, children))
		self.type = "" #the type of thing that this pydal pattern is sequencing


	def __add__(self, b):
		return PydalNode([self, b]) #TODO: make sure we REALLY want this to be dependent on child instances
		
	def render(self, frac=None):

		scale = 1.0 if frac is None else frac/self.frac
		self.frac = self.frac if frac is None else frac

		childFracs = map(lambda node: node.frac*scale, self.children)
		childFracs.insert(0, 0)
		accumulatedShift = 0
		merge = []

		for i in range(len(childFracs)-1):
			accumulatedShift += childFracs[i]
			#print i, accumulatedShift
			timeShift = lambda timePitchTuple: (timePitchTuple[0]+accumulatedShift, timePitchTuple[1])

			#because 0 is inserted into child fracs, use childFracs[i+1] 
			#so each child is rendered with its actual frac value
			merge += map(timeShift, self.children[i].render(childFracs[i+1]))

		return merge
	

#render for SquareBracket:
#	render children
#	scale children to same total length
#	combine children 
class SquareBracketNode(PydalNode):

	def __init__(self, children, frac = 1):
		self.children = children
		self.leaf = False
		self.frac = frac
		self.type = "SquareBracket"

	def render(self, frac=None):
		self.frac = frac = self.frac if frac is None else frac
		renderedChildren = [c.render(frac) for c in self.children]
		return flattenChildren(renderedChildren)

	def __str__(self):
		return "["+".".join([str(c) for c in self.children])+"]"



class SymbolNode(PydalNode):

	def __init__(self, children, frac = 1):
		self.children = children
		self.frac = frac
		self.leaf = True
		self.type = "Symbol"

	def render(self, frac=None):
		self.frac = frac = self.frac if frac is None else frac
		return [(0, set(self.children))]

	def __str__(self):
		return self.children[0]

class ExpressionNode(PydalNode):

	def __init__(self, children, frac = 1):
		self.frac = frac
		self.children = children
		self.type = "Expression"
		self.leaf = False

	def render(self, frac=None):
		self.frac = frac = self.frac if frac is None else frac
		#todo: why is the 1.0 needed? frac should always be a decimal 
		#because 1.0 is passed in at the root of the AST
		childFrac = 1.0 * frac / len(self.children)
		renderedChildren = [c.render(childFrac) for c in self.children]
		return mergeRenderedChildren(childFrac, renderedChildren)

	def __str__(self):
		return ".".join([str(c) for c in self.children])



class MultNode(PydalNode):

	#child is either a SymbolNode or a *BracketNode
	#multNum is an integer 
	#TODO: "x" multiplier and fractional multiples 
	def __init__(self, child, multNum, frac = 1):
		self.child = child
		self.multNum = int(multNum)
		self.frac = frac
		self.type = "Mult"
		self.leaf = False
		self.children = [self.child]

	def render(self, frac=None):
		self.frac = frac = self.frac if frac is None else frac
		childFrac = frac / self.multNum
		childCopies = [self.child.render(childFrac) for i in range(self.multNum)]
		return mergeRenderedChildren(childFrac, childCopies)

	def __str__(self):
		return str(self.child) + "*" + str(self.multNum)



class CurlyBracketNode(PydalNode):

	def __init__(self, children, frac = 1):
		self.children = children
		self.leaf = False
		#must be set in initial construction wrt self.children
		self.alignmentInds = None

		#should this be saved state? how do we want to hanlde <> and () - "choice" operators?
		#we could make it st choice operators must contain a single "overlay" operator ({} or []) 
		self.frac = frac 
		self.type = "CurlyBracket"

	#because each expression is potentially nested inside a larger one,
	#the durations of each term may only be a fraction of their original
	#length wrt the number of terms in the "parent" expression. 
	#frac thus represents the fraction of the total loop time that
	#this sub expression takes [0, 1]
	def render(self, frac=None):
		self.frac = frac = self.frac if frac is None else frac

		if self.alignmentInds is None:
			self.alignmentInds = [0] * len(self.children)

		#allign and select grandchildren 
		#use grandchild expressions to figure out this node's expressions
		#	ex, {bd lt, bd sn sn} would have children with expressions "bd lt" and "bd sn sn",
		# 	and grandchildren "bd", "lt" from child 1, and "bd", "sn", "sn" from child 2.
		#	while its own expressions would be "bd/bd lt/sn", "bd/sn lt/bd", and "bd/sn lt/sn"
		# 	in that order, with "a/b" meaning samples a and b are played at the same time
		#this is a stateful computation and will return the "next" alignment on every call
		alignment = [[] for i in range(len(self.children))]
		for i in range(len(self.children[0].children)):
			for j in range(len(self.children)):
				alignment[j].append( self.children[j].children[ self.alignmentInds[j] ] )
				self.alignmentInds[j] = (self.alignmentInds[j]+1) % len(self.children[j].children)

		#render grandchildren 
		#however, grandchild expressions could be nested expressions (and thus stateful) themselves.
		#	therefore, we need to "re-render" the grandchildren each time after alligning them
		#	a "rendered" expression is a [(float, set)], where float is in [0, 1] and 
		#	represents a point of time in a loop, and set is the set of samples played 
		#	at that point in time
		grandChildFrac = frac / len(self.children[0].children)
		for i in range(len(alignment)):
			for j in range(len(alignment[i])):
				alignment[i][j] = alignment[i][j].render(grandChildFrac)

		#render expression ("assemble" grandchildren)
		#	once the children have been aligned/selected and rendered, use their rendered
		#	forms to render the final version of this "state" of the expression
		renderedChildren = []#combine the "grandchildren" into "children"
		for i in range(len(alignment)):
			renderedChildren.append(mergeRenderedChildren(grandChildFrac, alignment[i]))

		return flattenChildren(renderedChildren)

	def __str__(self):
		return "{"+".".join([str(c) for c in self.children])+"}"

	#how many times this node must be evaluated before it returns the same expression
	#def getPeriod():  



class AngleBracketNode(PydalNode):

	def __init__(self, children, frac=1):
		self.children = children
		self.leaf = False
		self.frac = frac
		self.type = "AngleBracket"

	def render(self, frac=None):
		self.frac = frac = self.frac if frac is None else frac
		randInd = random.randint(0, len(self.children)-1)
		child = self.children[randInd].render(frac)
		return child

	def __str__(self):
		return "<"+".".join([str(c) for c in self.children])+">"



class ParenBracketNode(PydalNode):

	def __init__(self, children, frac=1):
		self.children = children
		self.leaf = False
		self.frac = frac
		self.type = "ParenBracket"

		self.seqInd = 0

	def render(self, frac=None):
		self.frac = frac = self.frac if frac is None else frac
		child = self.children[self.seqInd].render(frac)
		self.seqInd = (self.seqInd+1) % len(self.children)
		return child

	def __str__(self):
		return "("+".".join([str(c) for c in self.children])+")"

