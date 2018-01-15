# Pydal

A partial port of Alex McClean's Tidal to Python

Tidal can be found here: https://github.com/tidalcycles/Tidal


Basic design description:

PydalChannel.read (which wraps PydalParser.parse) returns the root node of the abstract syntax tree representation of the string pattern. 

All AST nodes have a render() method that renders the pattern to a list - [(float, set)], where float is in [0, 1] and represents a point of time in a loop, and set is the set of samples played at that point in time. Each node will request the sub-patterns generated by its children, and then combine those sub patterns differently depending on its node type (to learn how the Tidal syntax works, refer to the Tidal documentation). 

When a pattern is played on a PydalChannel, the channel object renders 1 measure's worth of the pattern (essentially a time-series of beats), and sends it over to PydalSC.scd, which schedules that set of events. Before the last even plays, PydalSC requests the next buffer's worth of events from the PydalChannel object. 

Syntax additions/differences from standard Tidal - 2 new types of brackets:
- "(pat1, pat2)"" - will play the patterns sequentially every time it is rendered
- "&lt;pat1, pat2&gt;" - will randomly select what pattern to play every time it is rendered
	- I am aware this is done with "()" in Tidal currently, but when I first implemented this it wasn't there. Will likely update this when I get around to adding in all of the new stuff that's made its way into the Tidal syntax since this project was started. 

Entry points to start with for reading the code
- in Python
	- PydalChannel.read - start of parsing a string into the AST
	- the render() methods for all of the node types in PydalAssembler.py 

- in SC
	- startPattern() - where a pattern gets handled and scheduled to play
	- playStepGenerator() - the function that defines the mechanics for individual steps in the pattern are scheduled, and how the next buffer is requested.
	- sendSample - in Pydal, you can specify different pattern "types", meaning the symbols in a Pydal pattern can be used to parameterize actions in different ways. This function is where the different types of actions can be defined. 

To run pydal - 
- make sure you have jupyter notebooks installed
- On Mac OS, make sure IAC Driver is on and has a port called 'Bus 3'
- download this Ableton set - https://splice.com/neesh/pydalbasic
- Open the PydalTest notebook in jupyter and start playing around!



Note:
This repo also contains two "microlanguages" inspired by Tidal:
- A language for creating and traversing "variation trees" (parser/spec: treeLanguage.py, 'compiler': treeBuilder.py)
- A language for creating transition graphs (everything: transitionGraph.py)

Most of the documentation and usage examples for these two microlanguages is described in the PDF AudioMostlySubmission.py. 