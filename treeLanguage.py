
#traversal - \/ ^  <  >
#creation - add "!" to movement 
#instruction grouping - "()"
#repetition - "*n"



#<expression>  ::= <symbol> ["*" <number>] | <paren-bkock> | <expression> [(<expression>)]...  

#<paren-block> ::= "(" <expression> [<expression>]... ")" ["*" <number>]

#<mult>		   ::= "*"

#<symbol>	   ::=  (passes isSymbol function - \/ ^  <  > \/! ^!  <!  >! with variants)


# new syntax not in original paper: 
# 	- You can go down to the nth child with \/:n (indexes wrap around if n > numChildren)
#	- You can move forwards/backwards n steps among siblings with >:n and <:n (indexes wrap around)
#	- For instructions suffixed with @, the node value arrived at via that instruction will 
#		be returned in a traversal list. See treeBuilder.execute() for simple implementation


import re
import itertools
import string

def parse(inputStr, debug=False):
	return parseExpression(tokenize(inputStr), 0, 0, debug)[0].render()
 
def main():
	st = '\/ ^ ((^ <)*2 \/*2)*2 >'
	print tokenize(st)
	print parse(st, True)

def tokenize(inputStr):
	delimiters = ['\(', '\)', '\*']
	p = "([" + "".join(delimiters) + "])"
	dirtyTokens = map(str.split, re.split(p, inputStr))
	tokens = list(itertools.chain.from_iterable(dirtyTokens))
	#print " ".join(tokens)
	return tokens

def isSymbol(sym):
	symbolTypes = ['(\\\/(:[0-9]+)?@?)$', '\^@?', '(<(:[0-9]+)?@?)$', '(>(:[0-9]+)?@?)$', '\\\/!@?', '<!@?', '>!@?']
	return True in [re.match(s, sym) and True for s in symbolTypes]



def parseExpression(tokenList, ind, depth, debug = False):
	node = ExpressionNode([])

	while ind < len(tokenList) and tokenList[ind] != ")":
		if debug:
			print "expression \t", depth, ind, tokenList[ind]
		newInd = .5

		if isSymbol(tokenList[ind]):
			symbolOrMultNode, newInd = parseSymbol(tokenList, ind, depth+1, debug)
			node.children.append(symbolOrMultNode)
		elif tokenList[ind] == "(":
			parenOrMultNode, newInd = parseParenBlock(tokenList, ind+1, depth+1, debug)
			node.children.append(parenOrMultNode)
		else:
			raise StopIteration("can only start expressions with symbols or open paren: ") 

		ind = newInd

	return node, ind

def parseParenBlock(tokenList, ind, depth, debug = False):
	startInd = ind - 1
	
	node = ParenNode([])

	while not tokenList[ind] == ")":
		if debug:
			print "paren \t\t", depth, ind, tokenList[ind]
		expNode, newInd = parseExpression(tokenList, ind, depth+1, debug)
		node.children.append(expNode)
		ind = newInd

	if tokenList[ind] == ")":
		if ind+1 < len(tokenList) and tokenList[ind+1] == "*":
			return parseMult(tokenList, ind+1, node, depth+1, debug)
		else:
			return node, ind+1
	else:
		raise StopIteration("paren at index " + startInd + "must be closed")


def parseMult(tokenList, ind, node, depth, debug = False):
	if debug:
			print "mult \t\t", depth, ind, tokenList[ind]
	if tokenList[ind+1].isdigit():
		return MultNode(node, tokenList[ind+1]), ind+2
	else:
		raise StopIteration("number must follow muliplication operator")


def parseSymbol(tokenList, ind, depth, debug = False):
	if debug:
			print "symbol \t\t", depth, ind, tokenList[ind]
	symbolNode = SymbolNode(tokenList[ind:ind+1])
	if ind+1 < len(tokenList) and tokenList[ind+1] == "*":
		return parseMult(tokenList, ind+1, symbolNode, depth+1, debug)
	else:
		return SymbolNode(tokenList[ind:ind+1]), ind+1 

 
class ParenNode:

	def __init__(self, children, frac = 1):
		self.children = children
		self.leaf = False
		self.frac = frac
		self.type = "Paren"

	def render(self):
		return " ".join([c.render() for c in self.children])

	def __str__(self):
		return "["+".".join([str(c) for c in self.children])+"]"

class SymbolNode:

	def __init__(self, children, frac = 1):
		self.children = children
		self.frac = frac
		self.leaf = True
		self.type = "Symbol"

	def render(self):
		return self.children[0]

	def __str__(self):
		return self.children[0]

class ExpressionNode:

	def __init__(self, children):
		self.children = children
		self.type = "Expression"
		self.leaf = False

	def render(self):
		return " ".join([c.render() for c in self.children])

	def __str__(self):
		return ".".join([str(c) for c in self.children])


class MultNode:

	#child is either a SymbolNode or a ParenNode
	#multNum is an integer 
	def __init__(self, child, multNum, frac = 1):
		self.child = child
		self.multNum = int(multNum)
		self.frac = frac
		self.type = "Mult"
		self.leaf = False
		self.children = [self.child]

	def render(self):
		return " ".join([c.render() for c in self.children]*self.multNum)

	def __str__(self):
		return str(self.child) + "*" + str(self.multNum)


if __name__ == "__main__":
	main()
