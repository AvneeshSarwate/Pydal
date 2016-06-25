(
var noteToInd, noteToXY, isPadNote, buffers, recSynths, playSynths, recordOnTimes, loopDurTimes, recordMode, noteOnFunc, noteOffFunc, f1, f2, loopClocks, break, record_BUTTON, quneoOut, padIndToRed, padIndToGreen, record_LIGHT;

MIDIClient.init;
MIDIIn.connectAll;

quneoOut = MIDIOut.newByName("QUNEO", "QUNEO");
quneoOut.latency = 0;

//quneo control variables
noteToInd = {|x| x - 36}; //convert note to pad index
noteToXY = {|x| [noteToInd.(x)%4, floor(noteToInd.(x)/4)]}; //convert note to pad xy (bottom left 0,0)
isPadNote = {|x| (noteToInd.(x) >=0) && (noteToInd.(x) < 16)};
record_BUTTON = 24;
record_LIGHT = 33;
padIndToGreen = ((0..15)*2);
padIndToRed = ((0..15)*2 + 1);

Routine.run {
	s.bootSync;

	SynthDef(\recBuf, {|bufnum|
		var input;
		input = SoundIn.ar(0);
		RecordBuf.ar(input, bufnum, trigger: \trigger.kr(0), loop: 1); //trigger control
	}).add;

	SynthDef(\playBuf, {|out = 0, bufnum|
		var scaledRate, player;
		scaledRate = BufRateScale.kr(bufnum);
		player = PlayBuf.ar(1, bufnum, scaledRate, trigger: \trigger.kr(-1), loop: 1); //trigger control
		Out.ar(out, player)
	}).add;

	s.sync;

	//create - buffs, recBufSynths, playBufSynths with newPause
	buffers = Array.fill(16, {Buffer.alloc(s, s.sampleRate * 10.0, 1)});
	recSynths = Array.fill(16, {|i| Synth.newPaused(\recBuf, [\bufnum, buffers[i]])});
	playSynths = Array.fill(16, {|i| Synth.newPaused(\playBuf, [\out, 0, \bufnum, buffers[i]])});
};

recordOnTimes = Array.fill(16, {0});
loopDurTimes = Array.fill(16, {10});
loopClocks = Array.fill(16, {TempoClock.new(1)});
recordMode = false;
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
	if(isPadNote.(note), {
		var padInd = noteToInd.(note);
		if(recordMode,
			{
				recSynths[padInd].set(\trigger, 1);
				recSynths[padInd].run(true);
				recordOnTimes[padInd] = TempoClock.default.beats;
				quneoOut.noteOn(0, padIndToGreen[padInd], 127);
				["RECORDING START", padInd].postln;
			},
			{
				playSynths[padInd].set(\trigger, 1);
				playSynths[padInd].run(true);
				loopClocks[padInd].sched(loopDurTimes[padInd],
					{"FIRS TEMO CLOCK RESET".postln;
						f1.(playSynths[padInd], loopClocks[padInd], loopDurTimes[padInd], padInd)});
				quneoOut.noteOn(0, padIndToRed[padInd], 127);
				["PLAY START", padInd].postln;
	});});
	if(note == record_BUTTON, {
		recordMode = recordMode.not;
	});
};
MIDIFunc.noteOn(noteOnFunc, nil, nil, 2017846184);

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
	if(isPadNote.(note), {
		var padInd = noteToInd.(note);
		if(recordMode,
			{
				Task({recSynths[padInd].set(\trigger, -1);
					s.sync;
					recSynths[padInd].run(false);}).play;
				loopDurTimes[padInd] = TempoClock.default.beats - recordOnTimes[padInd];
				quneoOut.noteOff(0, padIndToGreen[padInd], 127);
				["RECORDING STOP", padInd].postln;
			},
			{
				Task({playSynths[padInd].set(\trigger, -1);
					s.sync;
					playSynths[padInd].run(false);}).play;
				loopClocks[padInd].clear;
				quneoOut.noteOff(0, padIndToRed[padInd], 127);
				["PLAY STOP", padInd].postln;
	});});
	if(note == record_LIGHT, {
		if(recordMode,
			{quneoOut.noteOn(0, record_LIGHT, 127)},
			{quneoOut.noteOff(0, record_LIGHT, 127)}
);});};

MIDIFunc.noteOff(noteOffFunc, nil, nil, 2017846184);



)