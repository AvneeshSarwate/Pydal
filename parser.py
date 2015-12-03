#
# <expression> ::= <symbol> [(<mult> <number>)] | <paren-block> [(<mult> <number>)] | <expression> [(<expression>)]...  
# 
# <paren_block> ::= "[" <expression>  ["," <expression>]... "]" | "{" <expression> ["," <expression>] "}" 
# 
# <mult> ::= "*" | "x"
#
# additional features 
# 	- "x": "new step repeat" - i.e a bx3 c -> a b b b c, whereas a b*3 c -> a [b b b] c
# 	- <pat1, pat2> - plays the "next" pattern every time around 


#nodeTypes determine how their children are aggregated

#isDelimiter - whether a token is a paren, number, or mult-operator or comma 

import re
import itertools
import string 


def tokenize(inputStr):
	delimiters = ["]", "[", "{", "}", "<", ">" "*", "x", ","]
	p = "([" + "".join(delimiters) + "])"
	dirtyTokens = map(str.split, re.split(p, inputStr))
	tokens = list(itertools.chain.from_iterable(dirtyTokens))
	#print " ".join(tokens)
	return tokens

def allIn(test, ref):
	vals = [t in ref for t in test]
	return reduce(lambda a, b: a and b, vals)

def isMult(s):
	return s in ("*", "x")
def isNumber(s):
	return allIn(s, string.digits)
def isOpenParen(s):
	return s in ("{", "[")
def isEndParen(s):
	return s in ("}", "]")
def isComma(s):
	return s == ","
#TODO: more conditions required to determine valid symbol 
def isSymbol(s): 
	return allIn(s, string.letters+string.digits+":") and s[0] != ":" and s[-1] != ":"

class Node():
	def __init__(self):
		self.children = []
		self.leaf = False

	def __str__(self):
		if self.leaf:
			return self.children[0]
		else: 
			return ".".join([str(c) for c in self.children])

#will get fleshed out into classes. only need simple tree to test AST contruction
def squareBracketNode():
	return Node()
def curlyBracketNode():
	return Node()
def expressionNode():
	return Node()
def symbolNode(token):
	n = Node()
	n.leaf = True
	n.children = [token]
	return n
def symbolMultNode(tokenList, i):
	n = Node()
	n.leaf = False
	n.children = [symbolNode(tokenList[i]), symbolNode(tokenList[i+1]+tokenList[i+2])]
	return n
def parenMultNode(node, tokenList, i):
	n = Node()
	n.children = [node, symbolNode(tokenList[i]+tokenList[i+1])]
	return n 




def parseSymbol(tokenList, ind):
	if ind < len(tokenList)-1 and isMult(tokenList[ind+1]):
		if ind+1 < len(tokenList)-1 and isNumber(tokenList[ind+2]):
			return symbolMultNode(tokenList, ind), ind+3
		else:
			raise StopIteration("number must follow muliplication operator")
	else:
		return symbolNode(tokenList[ind]), ind+1 



def parseParenBlock(tokenList, ind, parseDebug = False):
	startInd = ind
	openParen = tokenList[ind]
	if openParen == "[":
		node = squareBracketNode()
	elif openParen == "{":
		node = curlyBracketNode()
	ind += 1

	while not isEndParen(tokenList[ind]):
		expNode, newInd = parseExpression(tokenList, ind)
		node.children.append(expNode)
		if isComma(tokenList[newInd]):
			if parseDebug:
				node.children.append(symbolNode(","))
			newInd += 1
		ind = newInd

	if (openParen == "[" and tokenList[ind] == "]") or (openParen == "{" and tokenList[ind] == "}"):
		if parseDebug:
			node.children.insert(0, symbolNode(openParen)) #DEBUG
			node.children.append(symbolNode(tokenList[ind]))
		return node, ind+1
	else:
		raise StopIteration("paren at index " + startInd + "must be closed")



def parseExpression(tokenList, ind):
	
	node = expressionNode()

	#at start of loop, [new]ind is always the index to read next 
	while ind < len(tokenList) and not isComma(tokenList[ind]) and not isEndParen(tokenList[ind]): #check this
		newInd = .5

		if isSymbol(tokenList[ind]):
			symbolNode, newInd = parseSymbol(tokenList, ind)
			node.children.append(symbolNode)

		elif isOpenParen(tokenList[ind]):
			parenNode, newInd = parseParenBlock(tokenList, ind)
			if newInd < len(tokenList)-1 and isMult(tokenList[newInd]):
				if newInd+1 < len(tokenList) and isNumber(tokenList[newInd+1]):
					node.children.append(parenMultNode(parenNode, tokenList, newInd))
					newInd += 2
				else:
					raise StopIteration("number must follow muliplication operator")
			else:
				node.children.append(parenNode)
		else:
			raise StopIteration("can only start expressions with symbols or open paren: ") 

		ind = newInd

	return node, ind

def printLevels(node):
	lists = [[],[]]

	a = lambda x: x%2
	b = lambda x: (a(x)+1)%2

	i = 0

	lists[a(i)].append(node)
	while not all([n.leaf for n in lists[a(i)]]):
		lists[b(i)] = []
		print "  -  ".join(map(str, lists[a(i)]))
		for n in lists[a(i)]:
			if n.leaf:
				lists[b(i)].append(n)
			else:
				lists[b(i)].extend([c for c in n.children])
		i += 1

	print "  -  ".join(map(str, lists[a(i)]))

	
test = lambda s : printLevels(parseExpression(tokenize(s), 0)[0])

cases = [
	"a a a",
	"a { a a}",
	"[a c]*2",
	"a {a a, b b } ",
	"a {a a, b b* 2 } ",
	"a {[a a]*3, b b* 2 } ",
	"{a c, d {d a}*3} b [a, g]",
	"{lt lt:2, {hc hc:2, ho sn:2 sn:3*2} {bottle bottle bottle, [bin:2 bin] bin:1} bd}"
	]

for c in cases:
	print "TEST CASE:", c
	test(c)
	print "\n\n-----------------------------------------------\n\n"
