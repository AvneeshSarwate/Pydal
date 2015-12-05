//tempoclock with beat set to 1 cycle length
(

midiOut = MIDIOut.newByName("IAC Driver", "Bus 1");
pythonOSCport = NetAddr("localhost", 34345);
tempoClock = TempoClock(1);
chanelPatternMap = Dictionary.new;
chanBackupPatMap = Dictionary.new;
channelInd = Dictionary.new;

//msg[1] is the channel being played on
//msg[2] is the string pattern getting played
startPattern = {|msg, time, addr, recvPort|
	//parse string to pattern
	//save pattern to map
	//calculate what ind/time to start from
	//save/increment ind
	//kick of playing
};

//generated as a closure via playStepGenerator.(i)where i is the channel ind
playStep = {
	//if list len == 0, exit
	//get and play next sample
	//save this sample's duration (d)
	//if 2nd to last step, send request for next pattern
	//if last step (or < 20 ms from end?), set backupPat to actual pattern
	//update indexes appropriately
	//return (d) - i.e. schedule next step on channel
};

//msg[1] is the channel being played on
//msg[2] is the backup pattern
recieveBackupPattern = {|msg, time, addr, recvPort|
	//parse string and save it to backupmap
};

//msg[1] is ind of channel to stop
stopPattern = {|msg, time, addr, recvPort|
	//set patternof msg 1 to empty list
	//set ind to 0
};

)