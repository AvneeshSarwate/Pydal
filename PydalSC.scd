//tempoclock with beat set to 1 cycle length
(

midiOut = MIDIOut.newByName("IAC Driver", "Bus 1");
pythonOSCport = NetAddr("localhost", 34345);
tempoClock = TempoClock(1);
channelPatternMap = Dictionary();
chanBackupPatMap = Dictionary();
channelInd = Dictionary();

drumTypes = Dictionary();
drumTypes["bd"] = 30;
drumTypes["lt"] = 40;
drumTypes["ht"] = 50;
drumTypes["sn"] = 60;
drumTypes["ho"] = 70;
drumTypes["hc"] = 75;
drumTypes["cr"] = 80;
drumTypes["rd"] = 85;
drumTypes["bot"] = 90;
drumTypes["cp"] = 100;
drumTypes["bin"] = 102;
drumTypes["bend"] = 104;
drumTypes["aud"] = 108;

//msg[1] is the channel being played on
//msg[2] is the string pattern getting played
startPattern = {|msg, time, addr, recvPort|
	//parse string to pattern
	var patternList = patternRead.(msg[2]);

	//save pattern to map
	channelPatternMap[msg[1]] = timeListToDurationList.(patternList);

	//calculate what ind/time to start from
	loopFrac = tempClock.beats % 1;
	ind = 0;
	patternList.do({|p|
		if(loopFrac > p[0], {ind+=1})
	});
	ind+=1;

	//save/increment ind
	channelInd[msg[1]] = ind;

	tempoClock.sched(patternList[ind][0] - loopFrac, playStepGenerator.(msg[1]));
	//kick of playing
};

playStepGenerator = {|i|
	playStep = {
		//if list len == 0, exit
		var retVal = nil;
		if(channelPatternMap.get(i).size != 0, {
			var ind = channelInd.get(i);
			var patList = channelPatternMap.get(i)
			var step = patList[ind];
			var dur = step[0];

			step[1].do({|samp| sendSample.(samp)});

			//if 2nd to last step, send request for next pattern
			if(ind == patList.size-2, {pythonOSCport.sendMsg("/pydalGetUpdate-"++i)});

			//if last step (or < 20 ms from end?), set backupPat to actual pattern
			if(ind == patList.size-1, {channelPatternMap[i] = chanBackupPatMap[i]});

			//update indexes appropriately
			channelInd[i] = (ind+1)%patList.size;

			//return (d) - i.e. schedule next step on channel
			retVal = dur;
		});
		retVal
	};
	playStep
};


//generated as a closure via playStepGenerator.(i)where i is the channel ind


//msg[1] is the channel being played on
//msg[2] is the backup pattern
recieveBackupPattern = {|msg, time, addr, recvPort|
	//parse string and save it to backupmap
	chanBackupPatMap[msg[1]] = timeListToDurationList.(patternRead.(msg[2]));
};

//msg[1] is ind of channel to stop
stopPattern = {|msg, time, addr, recvPort|
	if(channelPatternMap.includes(msg[1]), {channelPatternMap[msg[1]] = []});
};

patternRead = {|patternStr|
	var patternList = List.new;
	patternStr.split($;).do({|s|
		var step = s.split($-);
		var time = step[0].asFloat;
		var sampSet = Set.newFrom(step[1].split($,));
		step[0].postln;
		step[1].postln;
		patternList.add([time, sampSet]);
	});
	patternList
};

timeListToDurationList = {|oldList|
	pList = List.new;
	(0..oldList.size-2).do({|i|
		pList.add([oldList[i+1][0] - oldList[i][0], oldList[i][1]]);
	});
	pList.add([1 - oldList[oldList.size-1][0], oldList[oldList.size-1][1]]);
	plist
};

sendSample = {|drumStr|

	drumInd = drumStr.split($:)[1];
	drumInd = if(drumInd.isNil, 0, {drumInd.asInteger});
	drumType = drumTypes[drumStr.split($:)[0]].asInteger;

	//todo - send cc map stuff if applicable
	Task({
		midiOut.noteOn(chanInd-1, drumType+drumInd); //maybe add velocity based on gain?
		0.001.wait;
		midiOut.noteOff(chanInd-1, drumType+drumInd);
	}).play;
};

)
//===========================================================================
//scratch code below
(
d = Dictionary.new;
d.includes(5);
)


(
var patternSplit = {|patternStr|
	var patternList = List.new;
	patternStr.split($;).do({|s|
		var step = s.split($-);
		var time = step[0].asFloat;
		var sampSet = Set.newFrom(step[1].split($,));
		step[0].postln;
		step[1].postln;
		patternList.add([time, sampSet]);
	});
	patternList
};
b = patternSplit.("0.6-a,b;0.8-c");
"0.6-a,b;0.8-c".split($;).postln;
"break".postln;
b.do({|e| [e[0], e[1], e.class].postln});
b.size.postln;
nil
)
"0.6".asFloat
(
b = [1, 3];
Set(b)
)