#!/usr/bin/env python

from operator import itemgetter
import sys

curkey = None
total = 0
for line in sys.stdin:
	key, val = line.split("\t",1)
	val = int(val)

	if key == curkey:
		total += val
	else:
		if curkey is not None:
			print(curkey+"\t"+str(total))
		curkey = key
		total = val

print(curkey+"\t"+str(total))

