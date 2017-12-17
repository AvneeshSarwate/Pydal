import OSC
import PydalParser as parser
import copy
import threading 

class Pydal:
	
	def __init__(self, port=('127.0.0.1', 34345)):
		self.superColliderClient = OSC.OSCClient()
		self.superColliderClient.connect( ('127.0.0.1', 57120) ) 

		self.superColliderServer = OSC.OSCServer(port)
		self.serverThread = threading.Thread(target=self.superColliderServer.serve_forever)
		self.serverThread.daemon = False
		self.serverThread.start()

		self.numArpeggiatorChannels = 0

	def end(self):
		self.superColliderServer.close()

	def newChannel(self, num):
		#send message to superCollider to make new handler for channel
		return PydalChannel(num, self.superColliderServer, self.superColliderClient)

	def newArpeggiatorChannel(self, midiChannel):
		arpChan = ArpeggiatorChannel(self.numArpeggiatorChannels, self.superColliderServer, self.superColliderClient, midiChannel)
		self.numArpeggiatorChannels += 1
		return arpChan

	#num is the BPM
	def setTempo(self, num):
		msg = OSC.OSCMessage()
		msg.setAddress("/uploadTempo")
		msg.append(60.0/num)
		self.superColliderClient.send(msg)


def read(rawStr, frac = 1.0, symbolKey = 'pydal'):
	node = parser.parse(rawStr, symbolKey)
	node.frac = float(frac)
	return node
	#return PydalStringPattern(rawStr)

#pydalInstance = Pydal()
def getPydalInstance(port=('127.0.0.1', 34345)):
	return Pydal(port)

# def tempo(num):
# 	pydalInstance.setTempo(num)

# def newChannel(num):
# 	return pydalInstance.newChannel(num)

# def end():
# 	pydalInstance.end()


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


class Sequence:

	def __init__(self, seqString, *args):

		stripSymbols = lambda beats : map(lambda beat : list(beat[1])[0], beats)

	def render(self):
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
		self.isPlaying = False


	def _update(self, *args):
		renderList = self.pydalPattern.render()
		renderStr = ";".join(str(t[0]) + "-" + ",".join(t[1]) for t in renderList)
		msg = OSC.OSCMessage()
		msg.setAddress("/pydalSendUpdate")
		msg.append(self.num)
		msg.append(renderStr)
		msg.append(self.pydalPattern.frac)
		self.superColliderClient.send(msg)

	def play(self, pat, metaInfo=None):
		self.pydalPattern = pat
		self.isPlaying = True
		renderList = self.pydalPattern.render()
		renderStr = ";".join(str(t[0]) + "-" + ",".join(t[1]) for t in renderList)
		msg = OSC.OSCMessage()
		msg.setAddress("/pydalPlay")
		msg.append(self.num)
		msg.append(renderStr)
		msg.append(pat.frac)
		msg.append(pat.type)
		if metaInfo is not None:
			msg.append(metaInfo)
		self.superColliderClient.send(msg)

	def stop(self):
		self.isPlaying = False
		msg = OSC.OSCMessage()
		msg.setAddress("/pydalStop")
		msg.append(self.num)
		self.superColliderClient.send(msg)

class ArpeggiatorChannel:

	def __init__(self, num, server, client, midiChannel):
		self.num = num
		self.midiChannel = midiChannel
		self.address = "pydalChannel-" + str(num)
		self.pydalPattern = None
		self.superColliderServer = server
		self.superColliderClient = client
		self.superColliderServer.addMsgHandler("/arpeggiatorGetUpdate-"+str(self.num), self._update)


	def _update(self, *args):
		renderList = self.pydalPattern.render()
		renderStr = ";".join(str(t[0]) + "-" + ",".join(t[1]) for t in renderList)
		msg = OSC.OSCMessage()
		msg.setAddress("/arpeggiatorSendUpdate")
		msg.append(self.num)
		msg.append(renderStr)
		msg.append(self.midiChannel)
		msg.append(self.pydalPattern.frac)
		self.superColliderClient.send(msg)

	def play(self, pat):
		self.pydalPattern = pat
		renderList = self.pydalPattern.render()
		renderStr = ";".join(str(t[0]) + "-" + ",".join(t[1]) for t in renderList)
		msg = OSC.OSCMessage()
		msg.setAddress("/arpeggiatorPlay")
		msg.append(self.num)
		msg.append(renderStr)
		msg.append(self.midiChannel)
		msg.append(self.pydalPattern.frac)
		self.superColliderClient.send(msg)

	def stop(self):
		msg = OSC.OSCMessage()
		msg.setAddress("/arpeggiatorStop")
		msg.append(self.num)
		msg.append(self.midiChannel)
		self.superColliderClient.send(msg)


class LoopPattern:

	def __init__(self, loop):
		self.loop = loop #[pre-note-wait, note, vel, chan, "on/off/timeafterlasthit"]
		self.frac = round(sum([hit[0] for hit in loop]))
		self.type = "loop"

	# Pydal sequencer assumes list is a timestamp list (not hit duration list)  and then converts 
	# it to a hit list where the time associated with a hit is the time between it and the NEXT hit.
	# Also, it assumes first event happens at 0.0 time (need to add a ~ event if this is not the case)
	@staticmethod
	def hitListToTimestampList(loop):
		newLoop = copy.deepcopy(loop)
		newLoop.pop()   #remove timeAfterLastHit
		for i in range(1, len(newLoop)): #convertToTimestampLoop
			newLoop[i][0] += newLoop[i-1][0]
		if newLoop[0][0] != 0: #add 0.0 time starting event
			newLoop.insert(0, [0, 0, 0, 0, "~"])
		return newLoop

	def render(self):
		newLoop = self.hitListToTimestampList(self.loop)
		return [[hit[0], {"^".join([str(h) for h in hit[1:]])}] for hit in newLoop]


# TODO: probably want this implementation 
# - To implement a functor, a user must override the 
# 	initializeState and computation methods 
class Functor:

	def __init__(self, *args):
		self.savedArgs = args
		self.initializeState()
	
	# - Defines the names of state variables and their
	#	initial values 
	def _initializeState(self):
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
	def _computation(self):
		return


	# - If a functor makes changes to the expression tree
	# 	this is the method that should be used to get it. 
	def getExpressionTree():
		return self.expressionTree


