import treeLanguage as tl 

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

	def moveDown(self, ind):
		if len(self.currentNode.children) != 0:
			self.siblingInd = ind%len(self.children)
			self.currentNode = self.children[self.siblingInd]

	def moveUp(self):
		if not self.currentNode.parent is None:
			self.currentNode = self.currentNode.parent

	def moveLeft(self, ind):
		return

	def moveRight(self, ind):
		return

	def newDown(self):
		return

	def newLeft(self):
		return

	def newRight(self):
		return





class Node:

	def __init__(self, value = None, parent = None):
		self.children = []
		self.value = value
		self.parent = parent
