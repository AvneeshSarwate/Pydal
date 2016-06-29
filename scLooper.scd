(
var noteToInd, noteToXY, isPadNote, buffers, recSynths, playSynths, recordOnTimes, loopDurTimes, recordMode, noteOnFunc, noteOffFunc, f1, f2, loopClocks, break, record_BUTTON, miniOut, padIndToRed, padIndToGreen, record_LIGHT, tempoClock, metronomeSynched, isPlaying, metronomeSync_BUTTON, isSynched, isRecording, startPlaying, stopPlaying, startRecording, stopRecording, masterClockTempoHandler, metronomeFunc, syncFlash, red_LIGHT, green_LIGHT, amber_LIGHT, mini, used, abletonLatency;

/*MIDIClient.init;
MIDIIn.connectAll;*/

miniOut = MIDIOut.newByName("Launchpad Mini", "Launchpad Mini");
miniOut.latency = 0;

mini = MIDIClient.sources.select({|elem| (elem.name == "Launchpad Mini")
	&& (elem.device == "Launchpad Mini")})[0];
/*
TODO -
continue to tweak latency
fix recordOnTimes usage - what tempoClock to use? (default vs "tempoClock" var)
things to set via python api
   set number of "count in" beats
   start/end points of loop (referenced by beat)
*/
//quneo control variables
noteToInd = {|x|
	var row = x / 16;
	var col = x % 16;
	var retVal = -1;
	if(col < 8, {retVal = row*8 + col});
	retVal
}; //convert note to pad index
noteToXY = {|x| [noteToInd.(x)%8, floor(noteToInd.(x)/8)]}; //convert note to pad xy (bottom left 0,0)
isPadNote = {|x| noteToInd.(x) != -1};
record_BUTTON = 8;
metronomeSync_BUTTON = 24;
green_LIGHT = 48;
red_LIGHT = 3;
amber_LIGHT = 51;

abletonLatency = 3.0 * 0.0354; //seconds

Routine.run {

	s.options.inDevice = "POD HD400";
	//s.options.outDevice = "Soundflower (64ch)";

	s.bootSync;

	SynthDef(\recBuf, {|bufnum|
		var input;
		input = SoundIn.ar([0, 1]);
		RecordBuf.ar(input, bufnum, trigger: \trigger.kr(0), loop: 1); //trigger control
	}).add;

	SynthDef(\playBuf, {|out = 0, bufnum|
		var scaledRate, player;
		scaledRate = BufRateScale.kr(bufnum);
		player = PlayBuf.ar(2, bufnum, scaledRate, trigger: \trigger.kr(-1), loop: 1); //trigger control
		Out.ar(out, player)
	}).add;

	s.sync;

	//create - buffs, recBufSynths, playBufSynths with newPause
	buffers = Array.fill(64, {Buffer.alloc(s, s.sampleRate * 30.0, 2)});
	recSynths = Array.fill(64, {|i| Synth.newPaused(\recBuf, [\bufnum, buffers[i]])});
	playSynths = Array.fill(64, {|i| Synth.newPaused(\playBuf, [\out, 0, \bufnum, buffers[i]])});
};

recordOnTimes = Array.fill(64, {0});
loopDurTimes = Array.fill(64, {10});
loopClocks = Array.fill(64, {TempoClock.new(1)});
recordMode = false;
isPlaying = List.fill(64, {false});
isRecording = List.fill(64, {false});
used = List.fill(64, {false});
isSynched = false;
syncFlash = -1;

break = 0.1;
f1 = {|synth, clock, loopTime, padInd|
	Task({synth.set(\trigger, -1); //this shouldn't be necessary
		s.sync;
		synth.set(\trigger, 1);}).play;
	[padInd, "TRIGGER"].postln;
	clock.sched(break, {f2.(synth, clock, loopTime, padInd)});
};
f2 = {|synth, clock, loopTime, padInd|
	synth.set(\trigger, -1);
	clock.sched(loopTime-break, {f1.(synth, clock, loopTime, padInd)});
};

f = {|msg, time, addr, recvPort|
	//msg[1] is the new BEAT DURATION (not tempo)
	tempoClock = TempoClock.new(1/msg[1], 0);
	t = tempoClock;
	tempoClock.schedAbs(1, metronomeFunc);
};
OSCFunc(f, "/masterClockBeat").oneShot;

f = {
	if(isSynched, {
		if(syncFlash > 0,
			{miniOut.noteOn(0, metronomeSync_BUTTON, amber_LIGHT)},
			{miniOut.noteOn(0, metronomeSync_BUTTON, 0)}
		);
		},
		{
			miniOut.noteOn(0, metronomeSync_BUTTON, amber_LIGHT)
		}
	);
	syncFlash = syncFlash * -1;
};
OSCFunc(f, "/masterClockBeat");

masterClockTempoHandler = {|msg, time, addr, recvPort|
	tempoClock.tempo = 1/msg[1].asFloat;
};
OSCFunc(masterClockTempoHandler, "/masterClockTempo");


miniOut.noteOn(0, metronomeSync_BUTTON, amber_LIGHT);
miniOut.noteOn(0, record_BUTTON, green_LIGHT);
(0..63).do({|i| miniOut.noteOn(0, ((i/8).floor * 16) + (i%8), 0)});

startRecording = {|padInd, note|
	recSynths[padInd].set(\trigger, 1);
	recSynths[padInd].run(true);
	recordOnTimes[padInd] = TempoClock.default.beats;
	miniOut.noteOn(0, note, red_LIGHT);
	["RECORDING START", padInd].postln;
	isRecording[padInd] = true;
	used[padInd] = true;
};

startPlaying = {|padInd, note|
	playSynths[padInd].set(\trigger, 1);
	playSynths[padInd].run(true);
	loopClocks[padInd].sched(loopDurTimes[padInd],
		{"FIRS TEMO CLOCK RESET".postln;
			f1.(playSynths[padInd], loopClocks[padInd], loopDurTimes[padInd], padInd)});
	if(used[padInd], {miniOut.noteOn(0, note, green_LIGHT)});
	["PLAY START", padInd, tempoClock.beats].postln;
	isPlaying[padInd] = true;
};

stopRecording = {|padInd, note|
	Task({recSynths[padInd].set(\trigger, -1);
		s.sync;
		recSynths[padInd].run(false);}).play;
	loopDurTimes[padInd] = TempoClock.default.beats - recordOnTimes[padInd];
	miniOut.noteOn(0, note, amber_LIGHT);
	["RECORDING STOP", padInd].postln;
	isRecording[padInd] = false;
};

stopPlaying = {|padInd, note|
	Task({playSynths[padInd].set(\trigger, -1);
		s.sync;
		playSynths[padInd].run(false);}).play;
	loopClocks[padInd].clear;
	if(used[padInd],  {miniOut.noteOn(0, note, amber_LIGHT)});
	["PLAY STOP", padInd].postln;
	isPlaying[padInd] = false;
};

/*
noteOn
IF RECORD
trigger recBufSynth 1
unPause recBufSynth
remember hit times (separate for each pad)
IF PLAY
trigger playSynth 1
unpause playSynth
start loopTrigger tempoClock
*/
noteOnFunc = {|vel, note, chan, port|
	[note, "NOTE ON"].postln;
	if(isPadNote.(note), {
		var padInd = noteToInd.(note);
		var frozenRecordMode = recordMode;
		if(isSynched,
			{
				var funcToExecute;
				if(frozenRecordMode && isRecording[padInd], {funcToExecute = {stopRecording.(padInd, note)}});
				if(frozenRecordMode && isRecording[padInd].not, {funcToExecute = {startRecording.(padInd, note)}});
				if(frozenRecordMode.not && isPlaying[padInd], {funcToExecute = {stopPlaying.(padInd, note)}});
				if(frozenRecordMode.not && isPlaying[padInd].not, {funcToExecute = {startPlaying.(padInd, note)}});
				tempoClock.sched(tempoClock.timeToNextBeat - (abletonLatency*tempoClock.tempo), funcToExecute);
				["LATENCY COMPENSATED", tempoClock.timeToNextBeat,
					tempoClock.timeToNextBeat - (abletonLatency*tempoClock.tempo),
					tempoClock.beats].postln;
			},
			{
				if(frozenRecordMode,
					{startRecording.(padInd, note)},
					{startPlaying.(padInd, note)}
				);
			}
		);
	});

	if(note == record_BUTTON, {recordMode = recordMode.not});
	if(note == metronomeSync_BUTTON, {isSynched = isSynched.not});
};
MIDIFunc.noteOn(noteOnFunc, nil, nil, mini.uid);

/*
noteOff
IF RECORD
trigger recBufSynth -1
pause recBufSynth
save recorded duration
IF PLAY
trigger playSynth -1
pause playSynth
destroy loopTrigger tempoClock
*/
noteOffFunc = {|vel, note, chan, port|
	if(isPadNote.(note) && isSynched.not, {
		var padInd = noteToInd.(note);
		if(recordMode,
			{stopRecording.(padInd, note);},
			{stopPlaying.(padInd, note);}
		);
	});
	if(note == record_BUTTON, {
		if(recordMode,
			{miniOut.noteOn(0, record_BUTTON, red_LIGHT)},
			{miniOut.noteOn(0, record_BUTTON, green_LIGHT)}
	)});
};

MIDIFunc.noteOff(noteOffFunc, nil, nil, mini.uid);

)



(
t = TempoClock(1);
t.tempo = 50;
t.tempo



)

