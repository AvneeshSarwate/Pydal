import treeLanguage as tl 


def main():

	inc = lambda a: a+1	
	inc = Counter()
	tree = TreeBuilder(0, inc)
	tree.execute('\/! \/! >! >! <  < >!')
	print [c.value for c in tree.root.children[0].children]


class Counter:

	def __init__(self):
		self.count = 0

	def __call__(self, arg):
		self.count += 1
		return self.count 

class TreeBuilder:

	# Given a "flattened" token list, when trying to find what function matches
	# what token, first split the token by ":" to get the "function key."
	# This will allow you to use indexing for move[down, left, right]
	def __init__(self, rootValue, transformationFunc):
		self.root = Node(rootValue)
		self.currentNode = self.root
		self.transFunc = transformationFunc
		self.siblingInd = 0
		self.funcMap = {}
		self.funcMap['\/'] = self.moveDown
		self.funcMap['^'] = self.moveUp
		self.funcMap['<'] = self.moveLeft
		self.funcMap['>'] = self.moveRight
		self.funcMap['\/!'] = self.newDown
		self.funcMap['<!'] = self.newLeft
		self.funcMap['>!'] = self.newRight

	def moveDown(self, symbol):
		ind = int(symbol.split(":")[1]) if ":" in symbol else 0
		if len(self.currentNode.children) != 0:
			self.siblingInd = ind%len(self.children)
			self.currentNode = self.children[self.siblingInd]

	def moveUp(self, symbol):
		if not self.currentNode.parent is None:
			self.currentNode = self.currentNode.parent

	def moveRight(self, symbol):
		ind = int(symbol.split(":")[1]) if ":" in symbol else 1
		self.siblingInd = (self.siblingInd + ind) % len(self.currentNode.parent.children)
		self.currentNode = self.currentNode.parent.children[self.siblingInd]

	def moveLeft(self, symbol):
		ind = int(symbol.split(":")[1]) if ":" in symbol else 1
		self.siblingInd = (self.siblingInd - ind) % len(self.currentNode.parent.children)
		self.currentNode = self.currentNode.parent.children[self.siblingInd]

	def newDown(self, symbol):
		newVal = self.transFunc(self.currentNode.value)
		newNode = Node(newVal, self.currentNode)
		self.currentNode.children.append(newNode)
		newNode.treePosition = self.currentNode.treePosition + "-" + str(len(self.currentNode.children)-1)
		self.siblingInd = len(self.currentNode.children) - 1
		self.currentNode = newNode

		#TODO: - hanlde creating new siblings for tree root

	def newRight(self, symbol):
		newVal = self.transFunc(self.currentNode.value)
		newNode = Node(newVal, self.currentNode.parent)
		self.currentNode.parent.children.insert(self.siblingInd+1, newNode)
		newNode.treePosition = self.currentNode.parent.treePosition + "-" + str(self.siblingInd+1)
		#TODO: modify sibling ind of all subsequent silings
		for c in self.currentNode.parent.children[self.siblingInd+2:]:
			newLastPosition = str(int(c.treePosition.split("-")[-1])+1)
			positionSplit = c.treePosition.split("-")
			positionSplit[-1] = newLastPosition
			c.treePosition = "-".join(positionSplit)
		self.currentNode = newNode
		self.siblingInd += 1

	def newLeft(self, symbol):
		newVal = self.transFunc(self.currentNode.value)
		newNode = Node(newVal, self.currentNode.parent)
		self.currentNode.parent.children.insert(self.siblingInd - 1, newNode)
		newNode.treePosition = self.currentNode.parent.treePosition + "-" + str(max(self.siblingInd - 1, 0))
		#TODO: modify sibling ind of all subsequent silings
		for c in self.currentNode.parent.children[self.siblingInd+1:]:
			newLastPosition = str(int(c.treePosition.split("-")[-1])+1)
			positionSplit = c.treePosition.split("-")
			positionSplit[-1] = newLastPosition
			c.treePosition = "-".join(positionSplit)
		self.currentNode = newNode

	def execute(self, treeString):
		actions = tl.parse(treeString).split(" ")
		for a in actions:
			actionType = a.split(":")[0]
			self.funcMap[actionType](a)

class Node:

	def __init__(self, value = None, parent = None):
		self.children = []
		self.value = value
		self.parent = parent
		self.treePosition = "0"




if __name__ == "__main__":
	main()

