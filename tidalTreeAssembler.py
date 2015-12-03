


# "bd {sn sn, ho ho hc}"
# for a tree, you 


"{{bd bd, ho ho hc} {~ sn:2 ~, ~ cp}, {bin bin ~, ~ bottle ~ cp}} "


import itertools


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


def mergeChildren(childList):
	timeToSet = {} #combine the children 
	for timePitchTuple in itertools.chain.from_iterable(childList):
		if timePitchTuple[0] not in timeToSet:
			timeToSet[timePitchTuple[0]] = timePitchTuple
		else:
			timeToSet[timePitchTuple[0]] = (timePitchTuple[0], timeToSet[timePitchTuple[0]] | timePitchTuple[1])

	return sorted(timeToSet.values(), None, lambda tup: tup[0])

#render for SquareBracket:
#	render children
#	scale children to same total length
#	combine children 
class SquareBracketNode:

	def __init__(self, children = [], frac = 1):
		self.children = children
		self.leaf = False
		self.frac = frac

	def render(frac):
		#render grandchildren
		renderedGrandchildren = [[gc.render(frac / len(c.children)) for gc in c.children] for c in self.children]

		#render expression ("assemble" grandchildren)
		renderedChildren = []
		for i in range(len(renderedGrandchildren)):
			renderedChild = []
			grandChildFrac = frac / len(renderedGrandchildren[i])
			for j in range(len(renderedGrandchildren[i])):
				timeShift = lambda timePitchTuple: (timePitchTuple[0]+(j*grandChildFrac), timePitchTuple[1])
				renderedChild += map(timeShift, renderedGrandchildren[i][j])
			renderedChildren.append(renderedChild)

		return mergeChildren(renderedChildren)

class SymbolNode:

	def __init__(self, children = [], frac = 1):
		self.children = children
		self.frac = frac
		self.leaf = True

	def render(frac):
		return [(frac, Set(self.children))]

class ExpressionNode:

	def __init__(self, children = []):
		self.children = children
		

class CurlyBracketNode:

	def __init__(self, children = [], frac = 1):
		self.children = children
		self.leaf = False
		#must be set in initial construction wrt self.children
		self.alignmentInds = [0] * len(self.children)

		#should this be saved state? how do we want to hanlde <> and () - "choice" operators?
		#we could make it st choice operators must contain a single "overlay" operator ({} or []) 
		self.frac = frac 

	#because each expression is potentially nested inside a larger one,
	#the durations of each term may only be a fraction of their original
	#length wrt the number of terms in the "parent" expression. 
	#frac thus represents the fraction of the total loop time that
	#this sub expression takes [0, 1]
	def render(frac):
		#allign and select grandchildren 
		#use grandchild expressions to figure out this node's expressions
		#	ex, {bd lt, bd sn sn} would have children with expressions "bd lt" and "bd sn sn",
		# 	and grandchildren "bd", "lt" from child 1, and "bd", "sn", "sn" from child 2.
		#	while its own expressions would be "bd/bd lt/sn", "bd/sn lt/bd", and "bd/sn lt/sn"
		# 	in that order, with "a/b" meaning samples a and b are played at the same time
		#this is a stateful computation and will return the "next" alignment on every call
		alignment = [[] for i in len(self.children)]
		for i in range(len(self.children[0].children)):
			for j in len(self.children):
				alignment[j].append( self.children[j].children[ self.alignmentInds[j] ] )
				self.alignmentInds[j] = (self.alignmentInds[j]+1) % len(self.children[j].children)


		#render grandchildren 
		#however, grandchild expressions could be nested expressions (and thus stateful) themselves.
		#	therefore, we need to "re-render" the grandchildren each time after alligning them
		#	a "rendered" expression is a [(float, set)], where float is in [0, 1] and 
		#	represents a point of time in a loop, and set is the set of samples played 
		#	at that point in time
		grandChildFrac = frac / len(self.children[0])
		for i in range(len(alignment)):
			for j in range(len(alignment[i])):
				alignment[i][j] = alignment[i][j].render(grandChildFrac)

		#render expression ("assemble" grandchildren)
		#	once the children have been aligned/selected and rendered, use their rendered
		#	forms to render the final version of this "state" of the expression
		renderedChildren = []#combine the "grandchildren" into "children"
		for i in range(len(alignment)):
			renderedChild = []
			for j in range(len(alignment[i])):
				timeShift = lambda timePitchTuple: (timePitchTuple[0]+(j*grandChildFrac), timePitchTuple[1])
				renderedChild += map(timeShift, alignment[i][j])
			renderedChildren.append(renderedChild)

		return mergeChildren(renderedChildren)



	#how many times this node must be evaluated before it returns the same expression
	def getPeriod():  



