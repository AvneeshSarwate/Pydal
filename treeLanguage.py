
#traversal - \/ ^  <  >
#creation - add "!" to movement 
#instruction grouping - "()"
#repetition - "*n"



#<expression>  ::= <symbol> ["*" <number>] | <paren-bkock> | <expression> [(<expression>)]...  

#<paren-block> ::= "(" <expression> [<expression>]... ")" ["*" <number>]

#<mult>		   ::= "*"

#<symbol>	   ::=  \/ ^  <  > \/! ^!  <!  >!


import re
import itertools
import string
 
def main():
	st = '\/ ^ (< <)*2 >'
	print tokenize(st)
	print str(parseExpression(tokenize(st), 0, 0, True)[0])

def tokenize(inputStr):
	delimiters = ['\(', '\)', '\*']
	p = "([" + "".join(delimiters) + "])"
	dirtyTokens = map(str.split, re.split(p, inputStr))
	tokens = list(itertools.chain.from_iterable(dirtyTokens))
	#print " ".join(tokens)
	return tokens

def isSymbol(s):
	return s in ['\/', '^', '<', '>', '\/!', '^!', '<!', '>!']

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
		return parseMult(tokenList, ind+1, symbolNode)
	else:
		return SymbolNode(tokenList[ind:ind+1]), ind+1 

 
class ParenNode:

	def __init__(self, children, frac = 1):
		self.children = children
		self.leaf = False
		self.frac = frac
		self.type = "Paren"

	def __str__(self):
		return "["+".".join([str(c) for c in self.children])+"]"

class SymbolNode:

	def __init__(self, children, frac = 1):
		self.children = children
		self.frac = frac
		self.leaf = True
		self.type = "Symbol"

	def __str__(self):
		return self.children[0]

class ExpressionNode:

	def __init__(self, children):
		self.children = children
		self.type = "Expression"
		self.leaf = False

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

	def __str__(self):
		return str(self.child) + "*" + str(self.multNum)

if __name__ == "__main__":
	main()
