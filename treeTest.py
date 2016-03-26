import random
from treeBuilder import TreeBuilder as TB
import copy

def oneHitShift(hitList):
	i1 = random.randint(0, len(hitList)-1)
	i2 = random.randint(0, len(hitList)-1)
	h2 = copy.deepcopy(hitList)
	hit = hitList[i1]
	h2.pop(i1)
	h2.insert(i2, hit)
	return h2

l = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

t = TB(l, oneHitShift)

t.execute('\/! \/! >! >! <  < >!')

levels = t.nodesByDepth()
for l in levels:
	print l 