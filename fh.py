import OSC
import threading
import random
import copy
import phrase

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
		self.loopInfo = [[{} for j in range(n)] for i in range(n)]

		#[(loops, loopInfo)]
		self.scenes = [0]*100 # scenes[18] is scene in 1st row 8th column of launchpad  
		self.sceneStack = []

		#todo - update scales/roots here when changed programatically?
		self.scales = [[0, 2, 3, 5, 7, 8, 10] for i in range(n-1)] + [range(12)]
		self.roots = [60, 60, 36, 36]

		self.superColliderServer.addMsgHandler("/algRequest", self.handleAlgRequest)
		self.superColliderServer.addMsgHandler("/saveLoop", self.saveNewLaunchpadLoop)
		self.superColliderServer.addMsgHandler("/algRequestUpdate", self.updateChannel)
		self.superColliderServer.addMsgHandler("/loopPlay", self.loopPlay)
		self.superColliderServer.addMsgHandler("/saveScene", self.saveSceneHandler)
		self.superColliderServer.addMsgHandler("/playScene", self.playSceneHandler)

		self.channels = {} #key - int, val - (transFunc, rootMel)
		self.savedStrings = []

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
		self.savedStrings.append(stuff[4])
		hitList, button, startBeat = self.stringToHitList(stuff[4])
		chanInd, bankNum = stuff[:2]
		self.loops[chanInd][bankNum] = hitList
		self.loopInfo[chanInd][bankNum]["button"] = button
		self.loopInfo[chanInd][bankNum]["playing"] = True
		self.roots[chanInd] = stuff[2]
		self.scales[chanInd] = map(int, stuff[3].split(","))

	#stuff = [chanInd, bankNum, playing(bool)]
	def loopPlay(self, addr, tags, stuff, source):
		self.loopInfo[stuff[0]][stuff[1]]["playing"] = stuff[2]


	@staticmethod 
	def stringToHitList(loopString):
		lineSplit = loopString.split(" ")
		def splitHit(hitString):
			s = hitString.split(",")
			return [float(s[0]), int(s[1]), int(s[2]), int(s[3]), s[4]]
		recBuf = map(splitHit, lineSplit[1].split("-"))
		return recBuf, lineSplit[0], lineSplit[2]

	@staticmethod
	def hitListToString(hitList, button, startBeat, playing=0):
		return str(button) + " " + "-".join(map(lambda h: ",".join(map(str, h)), hitList)) + " " + str(startBeat) + " " + str(playing)


	def sceneToString(self, loops, loopInfo):
		sceneStringList = []
		for i in range(len(loops)):
			for j in range(len(loops[i])):
				if loops[i][j] != 0:
					sceneStringList.append(self.hitListToString(loops[i][j], loopInfo[i][j]["button"], "startBeat", 1 if loopInfo[i][j]["playing"] else 0))
				else:
					sceneStringList.append("none")
		return ":".join(sceneStringList)

	def sendScene(self, loops, loopInfo, roots, scales):
		msg = OSC.OSCMessage()
		msg.setAddress("/sendScene")
		msg.append(self.sceneToString(loops, loopInfo))
		msg.append(",".join(map(str, roots)))
		msg.append(",".join([".".join(map(str, scale)) for scale in scales]))
		self.superColliderClient.send(msg)

	def sendCurrentScene(self):
		self.sendScene(self.loops, self.loopInfo, self.roots, self.scales)

	#stuff[0] is ind of pad to which to save scene
	def saveSceneHandler(self, addr, tags, stuff, source):
		self.saveScene(int(stuff[0]))

	def saveScene(self, ind):
		c = copy.deepcopy
		self.scenes[ind] = (c(self.loops), c(self.loopInfo), c(self.roots), c(self.scales))

	#stuff[0] is ind of pad corresponding to which scene to play
	def playSceneHandler(self, addr, tags, stuff, source):
		self.playScene(int(stuff[0]))

	def playScene(self, ind):
		c = copy.deepcopy
		self.sceneStack.append((c(self.loops), c(self.loopInfo), c(self.roots), c(self.scales)))
		self.loops, self.loopInfo, self.roots, self.scales = c(self.scenes[ind])
		self.sendCurrentScene()

	def undoScenePlay(self):
		self.loops, self.loopInfo, self.roots, self.scales = self.sceneStack.pop()
		self.sendCurrentScene()

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

	def rootScale(self, chan=0, root=0, scale='minor'):
		msg = OSC.OSCMessage()
		msg.setAddress('/rootScale')
		msg.append(root)
		keyval = scale
		if scale in phrase.modes.keys():
			keyval = ",".join(map(str, phrase.modes[scale]))
		else:
			keyval = scale.split(',')
			keyval = map(lambda a: int(a.strip()), keyval)
			if len(keyval) == 0:
				raise StopIteration("malformed scale string")
			keyval = ','.join(keyval)
		msg.append(keyval)
		msg.append(chan)
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

def notesByBeat(noteList):
	byBeat = [[] for i in range(int(noteList[-1][0])+1)]
	#print "BY BEAT", byBeat
	for n in noteList:
		#print n
		byBeat[int(n[0])].append([n[0]%1] + n[1:])
	return byBeat

def flattenByBeat(byBeat):
	flattened = []
	for i in range(len(byBeat)):
		flattened += map(lambda note: [note[0]+i] + note[1:], byBeat[i])
	return flattened



#converts to a list of (timeStamp, midiNote, velocity, channel, duration)
#TODO: fix assumtion that we start with note on, and that
#there is strict alternation of note on/off per midiNote
def hitListToNoteList(hitList):
	noteToStartStop = {}
	timeSoFar = 0
	for h in hitList[:len(hitList)-1]:
		timeSoFar += h[0]
		if h[1] not in noteToStartStop:
			noteToStartStop[h[1]] = [(timeSoFar,  h[2], h[3], h[4])] #time, velocity, midiChan, on/off
		else:
			noteToStartStop[h[1]].append((timeSoFar, h[2], h[3], h[4]))


	noteList = []
	# for n in noteToStartStop:
	# 	print n, noteToStartStop[n]
	for midiNote in noteToStartStop:
		startStop = noteToStartStop[midiNote]
		for i in range(0, len(startStop), 2):
			if len(startStop) == i+1:
				noteList.append([startStop[i][0], midiNote, startStop[i][1], startStop[i][2], int(timeSoFar)+0.95-startStop[i][0]])
			else:
				#time, midiNote, onVelocity, midiChan, duration
				noteList.append([startStop[i][0], midiNote, startStop[i][1], startStop[i][2], startStop[i+1][0]-startStop[i][0]])

	noteList.sort()
	return noteList

def noteListToHitList(noteList):
	intermediateHitList = []
	for n in noteList:
		intermediateHitList.append([n[0], n[1], n[2], n[3], 'on'])
		intermediateHitList.append([n[0]+n[4], n[1], n[2], n[3], 'off'])

	intermediateHitList.sort()
	timeAfterLastHit = int(intermediateHitList[-1][0])+1 - intermediateHitList[-1][0]
	#print intermediateHitList
	for i in range(len(intermediateHitList)-1, 0, -1):
		intermediateHitList[i][0] -= intermediateHitList[i-1][0]

	intermediateHitList.append([timeAfterLastHit, 0, 0, 0, 'timeAfterLastHit'])

	return intermediateHitList




#TODO - figure out higher level organization of melody manipulation module
# 1. need a standard format to work with, make it a class (noteList as standard format?)
#	- notelist manipulation can result in hitlsits that aren't creatable when playing with hands,
#	  make sure this won't result in any hanging notes or weird length loops

# functions:
# splitAtBeats - splits a notelist into a list of segments starting at the indicies given (ending at the next largest index)
#	- can be combined well with "a c b b <a c, b c>" style sequencing
# 
# 
# 




def beatShuffle(hitList, start=None, end=None):
	#TODO - handle timeAfterLastBeat properly when shuffle includes last beat
	beatList = notesByBeat(hitListToNoteList(hitList))
	s = 0 if (start is None or start >= len(beatList)) else start
	e = len(beatList) if (end is None or end >= len(beatList) or end < s) else end 
	shuffleSeg = beatList[s:e]
	random.shuffle(shuffleSeg)
	rejoined = beatList[:s] + shuffleSeg + beatList[e:]
	return noteListToHitList(flattenByBeat(rejoined))

def scaleNotesCalc(root, scale, n):
    notes = [0]*n
    for i in range(n):
        notes[i] = root + (i/len(scale))*12 + scale[i%len(scale)] 
    return notes

#TODO - fix assumption that root note is 60
def randTranspose(hitList, root, scale, down=3, up=3, start=None, end=None, beatIndexed=True, intraBeatRandom=False):
	hitList = copy.deepcopy(hitList)
	noteList = hitListToNoteList(hitList)
	scaleNotes = scaleNotesCalc(root-36, scale, 50)
	if beatIndexed:
		beatList = notesByBeat(noteList)
		s = 0 if (start is None or start in range(len(beatList))) else start
		e = len(beatList) if (end is None or end >= len(beatList) or end < s) else end
		beatList = notesByBeat(noteList)
		for b in beatList[s:e]:
			r = random.randint(-1*down, up)
			for n in b:
				r = random.randint(-1*down, up) if intraBeatRandom else r
				#print n[1], r, scaleNotes.index(n[1]) + r
				n[1] = scaleNotes[scaleNotes.index(n[1]) + r]
		noteList = flattenByBeat(beatList)
	else:
		s = 0 if (start is None or start >= len(hitList)) else start
		e = len(hitList) if (end is None or end >= len(hitList) or end < s) else end
		for n in noteList:
			n[1] = scaleNotes[scaleNotes.index(n[1]) + random.randint(-1*down, up)]

	return noteListToHitList(noteList)

def randBeatMove(hitList):
	beatList = notesByBeat(hitListToNoteList(hitList))
	i = random.randint(0, len(beatList)-1)
	k = random.choice(list(set(range(len(beatList))) - set([i])))
	if i > k:
		beatList.insert(k, beatList.pop(i))
	else :
		beatList.insert(k-1, beatList.pop(i))
	return noteListToHitList(flattenByBeat(beatList))


def treeFunc(hitList, root, scale, p=0.3):
	if random.uniform(0, 1) > p :
		i = random.randint(0, len(hitList))
		j = random.randint(0, len(hitList))
		return randTranspose(hitList, root, scale, start=min(i, j), end=max(i, j), beatIndexed=False)
	else:
		return randBeatMove(hitList)


#TODO: print the strings of a few different buffers as test cases 

hitString = '19 0.015517354926804,36,90,3,on-0.069313140281711,36,0,3,off-0.40111655031738,36,88,3,on-0.13826123650379,36,0,3,off-0.30373582635919,36,86,3,on-0.068988503365478,36,0,3,off-0.37323516937636,36,94,3,on-0.16584420671271,36,0,3,off-0.37435709074858,41,102,3,on-0.22119814726626,41,0,3,off-0.52463878235438,41,99,3,on-0.17918737393996,41,0,3,off-0.58129390059232,41,97,3,on-0.17996301558244,41,0,3,off-0.3181157736951,36,108,3,on-0.25061781998902,36,0,3,off-0.8401201725943,36,97,3,on-0.29228857541083,36,0,3,off-0.75886568925363,41,99,3,on-0.2358261358357,41,0,3,off-0.7734233730412,41,111,3,on-0.27621152805202,41,0,3,off-0.65788063380083,0,0,0,timeAfterLastHit 14'
hitString = '19 0.0155173549268,36,90,3,on-0.0693131402817,36,0,3,off-0.401116550317,36,88,3,on-0.138261236504,36,0,3,off-0.303735826359,36,86,3,on-0.0689885033655,36,0,3,off-0.373235169376,36,94,3,on-0.165844206713,36,0,3,off-0.374357090749,41,102,3,on-0.221198147266,41,0,3,off-0.524638782354,41,99,3,on-0.17918737394,41,0,3,off-0.581293900592,41,97,3,on-0.179963015582,41,0,3,off-0.318115773695,36,108,3,on-0.250617819989,36,0,3,off-0.840120172594,36,97,3,on-0.292288575411,36,0,3,off-0.758865689254,41,99,3,on-0.235826135836,41,0,3,off-0.773423373041,41,111,3,on-0.276211528052,41,0,3,off-0.657880633801,0,0,0,timeAfterLastHit 14'
hl1 = '59 0,67,115,1,on-0.35805304900001,67,0,1,off-0.099085806999994,68,114,1,on-0.33568892400001,68,0,1,off-0.11485539500001,70,93,1,on-0.381267638,70,0,1,off-0.18247946000002,72,114,1,on-0.36613351199998,72,0,1,off-0.16243621499999,0,0,0,timeAfterLastHit 242'
hl2 = '69 0,67,108,1,on-0.44206642100005,68,86,1,on-0.156972967,67,0,1,off-0.31932736300001,70,58,1,on-0.11475639299999,68,0,1,off-0.39217421299998,72,91,1,on-0.07848408000001,70,0,1,off-0.49621856299996,0,0,0,timeAfterLastHit 275'
hl3 = '59 0.00026503200000061,67,116,1,on-0.109492002,67,0,1,off-0.114887669,67,97,1,on-0.083770298999999,67,0,1,off-0.150910389,67,113,1,on-0.094081841000001,67,0,1,off-0.162514201,67,114,1,on-0.083863190000001,67,0,1,off-0.177834871,67,117,1,on-0.083826460000001,67,0,1,off-0.156259629,67,106,1,on-0.073450127999999,67,0,1,off-0.188066174,67,110,1,on-0.083808517,67,0,1,off-0.173343166,67,107,1,on-0.073152808,67,0,1,off-0.182253786,67,112,1,on-0.073165353,67,0,1,off-0.167248956,67,97,1,on-0.068336707,67,0,1,off-0.198340459,67,97,1,on-0.062599650000001,67,0,1,off-0.188070831,67,105,1,on-0.083570547000001,67,0,1,off-0.172715621,68,118,1,on-0.078436826999999,68,0,1,off-0.151519889,68,111,1,on-0.072601442,68,0,1,off-0.172986674,68,107,1,on-0.062571509000001,68,0,1,off-0.193675872,68,117,1,on-0.083643336000002,68,0,1,off-0.178736165,0,0,0,timeAfterLastHit 4'
# print FH.hitListToString(*FH.stringToHitList(hitString)) == hitString

newHS = FH.stringToHitList(hl3)[0]
noteList = hitListToNoteList(newHS)
codecHS = noteListToHitList(noteList)
# print hitList
# print beatShuffle(newHS)
# for n in noteList:
# 	print n
# tot1 = 0
# for h in newHS:
# 	tot1 += h[0]
# 	print h
# tot2 = 0
# for h in codecHS:
# 	tot2+= h[0]
# 	print h
# print tot1, tot2
# beats = notesByBeat(noteList)
# for b in beats:
# 	print 
# notes = flattenByBeat(beats)
# for n in notes:
# 	print n
# print hitListToString(*stringToHitList(hitString))

hl = randTranspose(newHS, 60, [0, 2, 3, 5, 7, 8, 10])
#print hitListToNoteList(hl)


