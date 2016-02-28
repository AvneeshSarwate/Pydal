import treeLanguage as tl 

class TreeBuilder:

	def __init__(self, rootValue, transformationFunc):
		self.root = Node(rootValue)
		self.currentNode = self.root
		self.transFunc = transformationFunc
		self.funcMap = {}
		self.funcMap['\/'] = self.moveDown
		self.funcMap['^'] = self.moveUp
		self.funcMap['<'] = self.moveLeft
		self.funcMap['>'] = self.moveRight
		self.funcMap['\/!'] = self.newDown
		self.funcMap['<!'] = self.newLeft
		self.funcMap['>!'] = self.newRight

	def moveDown(self):
		return

	def moveUp(self):
		return

	def moveLeft(self):
		return

	def moveRight(self):
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
