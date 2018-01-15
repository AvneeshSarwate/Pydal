import treeLanguage as tl 


# For testing the generated tree
def main():
	inc = lambda a: a+1	
	inc = Counter()
	tree = TreeBuilder(0, inc)
	tree.execute('\/! \/! >! >! <  < >!')
	print [c.value for c in tree.root.children[0].children]
	levels = tree.nodesByDepth()
	for l in levels:
		print l 
	print toDotFile("test1", tree.root)

# a simple class to help test the validity of the generated tree structure
class Counter:
	def __init__(self):
		self.count = 0

	def __call__(self, arg):
		self.count += 1
		return self.count

#Saves the tree as a DOT file
def toDotFile(fileName, tree):
	el = []
	def addEdges(node, edgeList):
		for c in node.children:
			edgeList.append(str(node.value) + "->" + str(c.value))
			addEdges(c, edgeList)
	addEdges(tree, el)
	return "digraph " + fileName + " { \n" + "\n".join(el) + "\n}"
 

class TreeBuilder:

	# Given a "flattened" token list, when trying to find what function matches
	# what token, first split the token by ":" to get the "function key."
	# This will allow you to use indexing for move[down, left, right]
	def __init__(self, rootValue, transformationFunc):
		self.root = Node(rootValue)
		self.currentNode = self.root
		self.transFunc = transformationFunc
		self.siblingInd = 0
		self.siblingIndStack = [0]
		self.funcMap = {}
		self.funcMap['\/'] = self._moveDown
		self.funcMap['^'] = self._moveUp
		self.funcMap['<'] = self._moveLeft
		self.funcMap['>'] = self._moveRight
		self.funcMap['\/!'] = self._newDown
		self.funcMap['<!'] = self._newLeft
		self.funcMap['>!'] = self._newRight

	def _moveDown(self, symbol):
		ind = int(symbol.split(":")[1]) if ":" in symbol else 0
		if len(self.currentNode.children) != 0:
			self.siblingInd = ind%len(self.children)
			self.siblingIndStack.push(self.siblingInd)
			self.currentNode = self.children[self.siblingInd]
 
	def _moveUp(self, symbol):
		if not self.currentNode.parent is None:
			self.currentNode = self.currentNode.parent
			self.siblingIndStack.pop()
			self.siblingInd = self.siblingIndStack[-1]

	def _moveRight(self, symbol):
		ind = int(symbol.split(":")[1]) if ":" in symbol else 1
		self.siblingInd = (self.siblingInd + ind) % len(self.currentNode.parent.children)
		self.siblingIndStack[-1] = self.siblingInd
		self.currentNode = self.currentNode.parent.children[self.siblingInd]

	def _moveLeft(self, symbol):
		ind = int(symbol.split(":")[1]) if ":" in symbol else 1
		self.siblingInd = (self.siblingInd - ind) % len(self.currentNode.parent.children)
		self.siblingIndStack[-1] = self.siblingInd
		self.currentNode = self.currentNode.parent.children[self.siblingInd]

	def _newDown(self, symbol):
		newVal = self.transFunc(self.currentNode.value)
		newNode = Node(newVal, self.currentNode)
		self.currentNode.children.append(newNode)
		newNode.treePosition = self.currentNode.treePosition + "-" + str(len(self.currentNode.children)-1)
		self.siblingInd = len(self.currentNode.children) - 1
		self.siblingIndStack.push(self.siblingInd)
		self.currentNode = newNode

	def _newRight(self, symbol):
		newVal = self.transFunc(self.currentNode.value)
		newNode = Node(newVal, self.currentNode.parent)
		self.currentNode.parent.children.insert(self.siblingInd+1, newNode)
		newNode.treePosition = self.currentNode.parent.treePosition + "-" + str(self.siblingInd+1)
		for c in self.currentNode.parent.children[self.siblingInd+2:]:
			newLastPosition = str(int(c.treePosition.split("-")[-1])+1)
			positionSplit = c.treePosition.split("-")
			positionSplit[-1] = newLastPosition
			c.treePosition = "-".join(positionSplit)
		self.currentNode = newNode
		self.siblingInd += 1
		self.siblingIndStack[-1] = self.siblingInd

	def _newLeft(self, symbol):
		newVal = self.transFunc(self.currentNode.value)
		newNode = Node(newVal, self.currentNode.parent)
		self.currentNode.parent.children.insert(self.siblingInd - 1, newNode)
		newNode.treePosition = self.currentNode.parent.treePosition + "-" + str(max(self.siblingInd - 1, 0))
		for c in self.currentNode.parent.children[self.siblingInd+1:]:
			newLastPosition = str(int(c.treePosition.split("-")[-1])+1)
			positionSplit = c.treePosition.split("-")
			positionSplit[-1] = newLastPosition
			c.treePosition = "-".join(positionSplit)
		self.currentNode = newNode


	# parses a string of tree commands and executes the operations
	def execute(self, treeString):
		actions = tl.parse(treeString).split(" ")
		traversedVariants = []
		for a in actions:
			actionType = a.split(":")[0].strip('@')
			self.funcMap[actionType](a)
			if "@" not in a:
				traversedVariants.append(self.currentNode.value)
		return traversedVariants

	def nodesByDepth(self, returnValues=True):
		nodes = [[self.root]]
		vals = [[self.root.value]]
		children = [child for node in nodes[-1] for child in node.children]
		while len(children) != 0:
			nodes.append(children)
			vals.append(map(lambda n: n.value, children))
			children = [child for node in nodes[-1] for child in node.children]

		return vals if returnValues else nodes

class Node:

	def __init__(self, value = None, parent = None):
		self.children = []
		self.value = value
		self.parent = parent
		self.treePosition = "0"


if __name__ == "__main__":
	main()

