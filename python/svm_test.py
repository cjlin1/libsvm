#!/usr/bin/env python

from svm import *

# the XOR problem
labels = [0, 1, 1, 0]
samples = [[0, 0], [0, 1], [1, 0], [1, 1]]
problem = svm_problem(labels, samples);
size = len(samples)

kernels = [LINEAR, POLY, RBF, SIGMOID]
kname = ['linear','polynomial','rbf','sigmoid']

param = svm_parameter(C = 10)
for k in kernels:
	param.kernel_type = k;
	model = svm_model(problem,param)
	errors = 0
	for i in range(size):
		prediction = model.predict(samples[i])
		if (labels[i] != prediction):
			errors = errors + 1
	print "##########################################"
	print " kernel %s: error rate = %d / %d" % (kname[param.kernel_type], errors, size)
	print "##########################################"
