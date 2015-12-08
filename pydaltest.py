import PydalChanel as pydal

read = pydal.read

ch1 = pydal.newChannel(1)
ch1.play(read("sn bd bd"))


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





# To implement a functor, a user must pass in 2 functions
# initializer - takes "self" as first argument and 
# 	sets self.[name] to initial state values as specified by args
# renderer - takes "self" as first argument and does exactly what is 
# 	described in the comment for the render method of FunctorBuilder
class FunctorBuilder:

	def __init__(self, initializer, renderer):
		self.initializer = initializer
		self.renderer = renderer
		
	
	def initializeState(self):
		self.initilizer(self)

	# A functor can be called repeatedly 
	# to accumulate all needed arguments.
	# Its arguments must be called in order.
	# (todo: support explicit currying a la supercollider?)
	def __call__(self, *args):
		self.args += args

	# Render returns a sample time series and  
	# only references its own state and saved arguments.
	# It may modify its own state variables.
	# If an expression tree must be returned, it should be set here
	def render(self):
		self.renderer(self, *self.args)

	# If a functor makes changes to the expression tree
	# this is the method that should be used to get it. 
	def getExpressionTree():
		return self.expressionTree


class EveryBy:

	# args are int, float, pattern
	def __init__(self, *args):
		self.args = args

	def render(self):
		#some stuff
		return 


class Functor:

	def __init__(self):