#!/usr/bin/env python

import string
from svm import *
from cross_validation import *

f = open("../heart_scale", "r")
labels = []
samples = []
max_index = 0
line = f.readline()
while line:
	elems = string.split(line)
	sample = {}
	for e in elems[1:]:
		points = string.split(e, ":")
		sample[int(points[0])] = float(points[1])
		if int(points[0]) > max_index:
			max_index = int(points[0])
	labels.append(float(elems[0]))
	samples.append(sample)
	line = f.readline()
f.close()

print "%d samples loaded." % (len(samples))
param = svm_parameter(svm_type = C_SVC, kernel_type = RBF)
do_cross_validation(samples, labels, param, 10)
