import re
import itertools


def factorial(n):
	v = 1
	for i in range(1, n+1):
		v *= i
	return v

#print factorial(9), factorial(10), factorial(5)


def milPerm(n, symbols):
	k = 1
	while factorial(k) < n:
		k +=1
	print k-1

#print milPerm(1000000, ['0', '1', '2', '3','4', '5', '6','7', '8', '9'])


gStr = """
f1 --(s1)--> f2 --(pad1)--> f4

f2 --(seq1)--> f3

"""

def parseGraphString(gStr):
	strLines = filter(lambda a: (not a.isspace()) and len(a) != 0, gStr.split("\n"))
	for line in strLines:
		tokens = filter(lambda a: len(a) != 0, line.split())

		# split line into states and arrows
		# validate state, arrow, state [arrow, state]* pattern

print parseGraphString(gStr)



# general idea - a "state" consists of a functor that 
# is called when that state is transitioned to, its arguments being those that
# are provided from the "transition message" that signals the move to that state

# a "transition" is an OSC message with certain arguments

class TransitionGraph:

	def __init__(self, stateKeyToFunctor, graphString):
		self.stateKeyToFunctor = stateKeyToFunctor # map from stateString -> functor
		self.states = Set() #list of current active state strings
		self.linksByTransition = {} # map from transitionString -> set of links
		self.graphString = graphString
		self.parseGraphString()

	def parseGraphString(self):
		gStr = self.graphString
		strLines = filter(lambda a: (not a.isspace()) and len(a) != 0, gStr.split("\n"))
		for line in strLines:
			tokens = filter(lambda a: len(a) != 0, line.split())

			# split line into states and arrows
			# validate state, arrow, state [arrow, state]* pattern


	def transitionHandler(self, addr, tags, stuff, source):
		linksFromOldStates = filter(lambda link: link.fromState in states, linksByTransition[addr])
		newStates = map(lambda link:  link.toState, linksFromOldStates)
		
		for state in newStates:
			stateKeyToFunctor[state](*stuff)

		self.states = newStates

class Link:

	def __init__(fromStateString, transString, toStateString):
		self.fromState = fromStateString
		self.transition = transString
		self.toState = toStateString
