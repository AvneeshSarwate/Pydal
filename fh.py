import OSC
import threading
import random
import copy

#functionHanlder
class FH:
	
	def __init__(self):
		self.superColliderClient = OSC.OSCClient()
		self.superColliderClient.connect( ('127.0.0.1', 57120) ) 

		self.superColliderServer = OSC.OSCServer(('127.0.0.1', 13371))
		self.serverThread = threading.Thread(target=self.superColliderServer.serve_forever)
		self.serverThread.daemon = False
		self.serverThread.start()

		n = 4

		self.loops = [[0]*n for i in range(n)]
		self.scales = [0]*4
		self.roots = [0]*4

		self.superColliderServer.addMsgHandler("/algRequest", self.handleAlgRequest)
		self.superColliderServer.addMsgHandler("/saveLoop", self.saveNewLaunchpadLoop)
		self.superColliderServer.addMsgHandler("/algRequestUpdate", self.updateChannel)

		self.channels = {} #key - int, val - (transFunc, rootMel)

	#stuff = [chanInd, bankNum, root, scale, loopString] 
	def handleAlgRequest(self, addr, tags, stuff, source):
		msg = OSC.OSCMessage()
		msg.setAddress("/algResponse")
		msg.append(int(stuff[0]))
		msg.append(int(stuff[1]))
		print "got from supercollider"
		print stuff
		hitList, scale, startBeat = self.stringToHitList(stuff[4])
		for h in hitList:
			h[1] += 5
		msg.append(self.hitListToString(hitList, scale, startBeat))
		self.superColliderClient.send(msg)

	#stuff = [chanInd, bankNum, root, scale, loopString] 	
	def saveNewLaunchpadLoop(self, addr, tags, stuff, source):
		hitList, button, startBeat = self.stringToHitList(stuff[4])
		chanInd, bankNum = stuff[:2]
		self.loops[chanInd][bankNum] = hitList
		self.roots[chanInd] = stuff[2]
		self.scales[chanInd] = stuff[3].split(",")

	def sendLoop(self, chanInd, loop):
		msg = OSC.OSCMessage()
		msg.setAddress("/liveCodeEndpoint")
		msg.append(self.hitListToString(loop, chanInd, 5))
		self.superColliderClient.send(msg)

	@staticmethod 
	def stringToHitList(loopString):
		lineSplit = loopString.split(" ")
		def splitHit(hitString):
			s = hitString.split(",")
			return [float(s[0]), int(s[1]), int(s[2]), int(s[3]), s[4]]
		recBuf = map(splitHit, lineSplit[1].split("-"))
		return recBuf, lineSplit[0], lineSplit[2]

	@staticmethod
	def hitListToString(hitList, button, startBeat):
		return str(button) + " " + "-".join(map(lambda h: ",".join(map(str, h)), hitList)) + " " + str(startBeat)

	def end(self):
		self.superColliderServer.close()

	def startChannel(self, chanInd, transFunc, rootMel):
		#self.stopChannel(chanInd)
		self.channels[chanInd] = (transFunc, rootMel)
		msg = OSC.OSCMessage()
		msg.setAddress("/algStart")
		msg.append(chanInd)
		msg.append(self.hitListToString(rootMel, 'fillerStuff', 'fillerStuff'))
		self.superColliderClient.send(msg)

	#stuff[0] is channelInd
	def updateChannel(self, addr, tags, stuff, source):
		chanInd = stuff[0]
		transFunc = self.channels[chanInd][0]
		rootMel = self.channels[chanInd][1]
		newMel = transFunc(rootMel)
		msg = OSC.OSCMessage()
		msg.setAddress("/algRecieveUpdate")
		msg.append(chanInd)
		msg.append(self.hitListToString(newMel, 'fillerStuff', 'fillerStuff'))
		self.superColliderClient.send(msg)


	def stopChannel(self, chanInd):
		msg = OSC.OSCMessage()
		msg.setAddress("/algStop")
		msg.append(chanInd)
		self.superColliderClient.send(msg)


def oneHitShift(hitList):
	i1 = random.randint(0, len(hitList)-1)
	i2 = random.randint(0, len(hitList)-1)
	h2 = copy.deepcopy(hitList)
	hit = hitList[i1]
	h2.pop(i1)
	h2.insert(i2, hit)
	return h2

# hitString = '19 0.015517354926804,36,90,3,on-0.069313140281711,36,0,3,off-0.40111655031738,36,88,3,on-0.13826123650379,36,0,3,off-0.30373582635919,36,86,3,on-0.068988503365478,36,0,3,off-0.37323516937636,36,94,3,on-0.16584420671271,36,0,3,off-0.37435709074858,41,102,3,on-0.22119814726626,41,0,3,off-0.52463878235438,41,99,3,on-0.17918737393996,41,0,3,off-0.58129390059232,41,97,3,on-0.17996301558244,41,0,3,off-0.3181157736951,36,108,3,on-0.25061781998902,36,0,3,off-0.8401201725943,36,97,3,on-0.29228857541083,36,0,3,off-0.75886568925363,41,99,3,on-0.2358261358357,41,0,3,off-0.7734233730412,41,111,3,on-0.27621152805202,41,0,3,off-0.65788063380083,0,0,0,timeAfterLastHit 14'
# hitString = '19 0.0155173549268,36,90,3,on-0.0693131402817,36,0,3,off-0.401116550317,36,88,3,on-0.138261236504,36,0,3,off-0.303735826359,36,86,3,on-0.0689885033655,36,0,3,off-0.373235169376,36,94,3,on-0.165844206713,36,0,3,off-0.374357090749,41,102,3,on-0.221198147266,41,0,3,off-0.524638782354,41,99,3,on-0.17918737394,41,0,3,off-0.581293900592,41,97,3,on-0.179963015582,41,0,3,off-0.318115773695,36,108,3,on-0.250617819989,36,0,3,off-0.840120172594,36,97,3,on-0.292288575411,36,0,3,off-0.758865689254,41,99,3,on-0.235826135836,41,0,3,off-0.773423373041,41,111,3,on-0.276211528052,41,0,3,off-0.657880633801,0,0,0,timeAfterLastHit 14'

# print hitListToString(*stringToHitList(hitString)) == hitString
# print hitListToString(*stringToHitList(hitString))




