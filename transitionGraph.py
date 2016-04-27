import re
import itertools


def funcStateTest(f, *args):
	print "function", f, "with args", args

def main():
	gStr = """
	f1 --(s1)--> f2 --(pad1)--> f4

	f2 --(seq1)--> f3

	"""

	funcMap = {}
	funcMap["f1"] = lambda *args: funcStateTest("f1", args)
	funcMap["f2"] = lambda *args: funcStateTest("f2", args)
	funcMap["f3"] = lambda *args: funcStateTest("f3", args)

	tg = TransitionGraph(funcMap, gStr)

	print tg.toGraphVisString()

	print tg.states
	tg.transitionHandler("s1", 0, 0, 0)
	print tg.states

# general idea - a "state" consists of a functor that 
# is called when that state is transitioned to, its arguments being those that
# are provided from the "transition message" that signals the move to that state

# a "transition" is an OSC message with certain arguments
class TransitionGraph:

	def __init__(self, stateKeyToFunctor, graphString, initialStates = None):
		self.stateKeyToFunctor = stateKeyToFunctor # map from stateString -> functor
		self.linksByTransition = {} # map from transitionString -> set of links
		self.graphString = graphString
		self.tokens = self.parseGraphStringIntoTokens()
		#list of current active state strings (first state in graph string by default)
		self.states = set([self.tokens[0][0]]) if initialStates is None else initialStates 
		self.generateGraphFromTokens(self.tokens)

		#todo - instantiate OSC server

	def parseGraphStringIntoTokens(self):
		gStr = self.graphString
		strLines = filter(lambda a: (not a.isspace()) and len(a) != 0, gStr.split("\n"))
		tokens = []

		arrowRE = "^--\([0-9A-Za-z]+\)-->$"
		symbolRE = "^([0-9A-Za-z]+)$"

		for line in strLines:
			lineTokens = filter(lambda a: len(a) != 0, line.split())
			i = 0
			m = lambda reStr, argStr: re.match(reStr, argStr)

			#move forward 2 tokens each time
			while i < len(lineTokens)-1:
				if not (m(symbolRE, lineTokens[i+0]) and m(arrowRE, lineTokens[i+1]) and m(symbolRE, lineTokens[i+2])):
					raise StopIteration("improperly formatted graph string")
				i += 2

			tokens.append(lineTokens)

		for t in tokens:
			print t
		return tokens


	def generateGraphFromTokens(self, tokens):
		for lineTokens in tokens:
			print "LINE TOKENS", lineTokens
			i = 0

			#move forward 2 tokens each time
			while i < len(lineTokens)-1:
				transitionStr = lineTokens[i+1][3:-4]
				if not transitionStr in self.linksByTransition:
					self.linksByTransition[transitionStr] = set()
				self.linksByTransition[transitionStr].add(Link(lineTokens[i+0], transitionStr, lineTokens[i+2]))	
				print i, lineTokens[i+0], transitionStr, lineTokens[i+2]
				#todo: add osc hanlder (self.transitionHanlder)
				i += 2


	def transitionHandler(self, addr, tags, stuff, source):
		linksFromOldStates = filter(lambda link: link.fromState in self.states, self.linksByTransition[addr])
		newStates = set(map(lambda link:  link.toState, linksFromOldStates))
		
		for state in newStates:
			self.stateKeyToFunctor[state](stuff)

		self.states = newStates

	def toGraphVisString(self):
		dotFileLines = []
		for link in itertools.chain.from_iterable(self.linksByTransition.values()):
			dotFileLines.append(link.fromState + " -> " + "\"("+link.transition+")\"" + " -> " + link.toState)

		return "digraph G {\n" + "\n".join(dotFileLines) + "\n}"

class Link:

	def __init__(self, fromStateString, transString, toStateString):
		self.fromState = fromStateString
		self.transition = transString
		self.toState = toStateString

if __name__ == "__main__":
	main()