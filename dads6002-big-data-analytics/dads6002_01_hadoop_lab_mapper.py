#!/usr/bin/env python

from operator import itemgetter
import sys

for line in sys.stdin:
	for word in line.split():
		print(word+"\t1")



