import OSC
import cleanParser as parser
import copy
import threading 

class Pydal:
	
	def __init__(self):
		self.superColliderClient = OSC.OSCClient()
		self.superColliderClient.connect( ('127.0.0.1', 57120) ) 

		self.superColliderServer = OSC.OSCServer(('127.0.0.1', 34345))
		self.serverThread = threading.Thread(target=self.superColliderServer.serve_forever)
		self.serverThread.daemon = False
		self.serverThread.start()

	def end(self):
		self.superColliderServer.close()

	def newChannel(self, num):
		#send message to superCollider to make new handler for channel
		return PydalChannel(num, self.superColliderServer, self.superColliderClient)



def read(rawStr):
	return PydalStringPattern(rawStr)

pydalInstance = Pydal()

def newChannel(num):
	return pydalInstance.newChannel(num)

def end():
	pydalInstance.end()


#this is the return object from a Pydal "function"
#Pydal functions can be composed 
#	(implementation help - https://mathieularose.com/function-composition-in-python/)
#design question - should Pydal functions actually be stateful functors?
class PydalFuncPattern:

	def __init__(self):
		self.stringPattern = None
		self.renderStack = None
		self.funcList = None

	def render(self):
		#apply func list to pattern
		return

class PydalStringPattern:

	def __init__(self, rawStr):
		self.rawStr = rawStr
		self.expressionTree = parser.parse(rawStr)
		self.tokens = parser.tokenize(rawStr)
		self.renderStack = []

	def render(self):
		renderedPattern = self.expressionTree.render(1.0)
		self.renderStack.append(copy.deepcopy(renderedPattern)) 
		return renderedPattern

class PydalChannel:

	def __init__(self, num, server, client):
		self.num = num
		self.address = "pydalChannel-" + str(num)
		self.pydalPattern = None
		self.superColliderServer = server
		self.superColliderClient = client
		self.superColliderServer.addMsgHandler("/pydalGetUpdate-"+str(self.num), self._update)


	def _update(self, *args):
		renderList = self.pydalPattern.render()
		renderStr = ";".join(str(t[0]) + "-" + ",".join(t[1]) for t in renderList)
		msg = OSC.OSCMessage()
		msg.setAddress("/pydalSendUpdate")
		msg.append(self.num)
		msg.append(renderStr)
		self.superColliderClient.send(msg)

	def play(self, pat):
		self.pydalPattern = pat
		renderList = self.pydalPattern.render()
		renderStr = ";".join(str(t[0]) + "-" + ",".join(t[1]) for t in renderList)
		msg = OSC.OSCMessage()
		msg.setAddress("/pydalPlay")
		msg.append(self.num)
		msg.append(renderStr)
		self.superColliderClient.send(msg)

	def stop(self):
		msg = OSC.OSCMessage()
		msg.setAddress("/pydalStop")
		msg.append(self.num)
		self.superColliderClient.send(msg)

# TODO: probably want this implementation 
# - To implement a functor, a user must override the 
# 	initializeState and computation methods 
class Functor:

	def __init__(self, *args):
		self.savedArgs = args
		self.initializeState()
	
	# - Defines the names of state variables and their
	#	initial values 
	def initializeState(self):
		return

	# - A functor can be called repeatedly to accumulate all needed arguments.
	# - Its arguments must be called in order.
	# (todo: support explicit currying a la supercollider?)
	def __call__(self, *args):
		self.args += args

	# - This method uses computation() to render the final series
	#	and expression tree	
	def render(self, *args):
		return self.computation(*(self.savedArgs+args))


	# - This returns a sample time series and only references its
	# 	arguments and the variables defined in intializeState().
	# - It may modify its own state variables.
	# - If an expression tree must be returned, it should be set here. 
	# - NEVER CALL THIS EXPLICITLY - use render() instead 
	def computation(self):
		return


	# - If a functor makes changes to the expression tree
	# 	this is the method that should be used to get it. 
	def getExpressionTree():
		return self.expressionTree


