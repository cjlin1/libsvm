#!/usr/bin/env python

from svm import *

# a three-class problem
labels = [0, 1, 1, 2]
samples = [[0, 0], [0, 1], [1, 0], [1, 1]]
problem = svm_problem(labels, samples);
size = len(samples)

kernels = [LINEAR, POLY, RBF]
kname = ['linear','polynomial','rbf']

param = svm_parameter(C = 10,nr_weight = 2,weight_label = [1,0],weight = [10,1])
for k in kernels:
	param.kernel_type = k;
	model = svm_model(problem,param)
	errors = 0
	for i in range(size):
		prediction = model.predict(samples[i])
		probability = model.predict_probability
		if (labels[i] != prediction):
			errors = errors + 1
	print "##########################################"
	print " kernel %s: error rate = %d / %d" % (kname[param.kernel_type], errors, size)
	print "##########################################"

param = svm_parameter(kernel_type = RBF, C=10)
model = svm_model(problem, param)
print "##########################################"
print " Decision values of predicting %s" % (samples[0])
print "##########################################"

print "Numer of Classes:", model.get_nr_class()
d = model.predict_values(samples[0])
for i in model.get_labels():
	for j in model.get_labels():
		if j>i:
			print "{%d, %d} = %9.5f" % (i, j, d[i,j])

param = svm_parameter(kernel_type = RBF, C=10, probability = 1)
model = svm_model(problem, param)
pred_label, pred_probability = model.predict_probability(samples[1])
print "##########################################"
print " Probability estimate of predicting %s" % (samples[1])
print "##########################################"
print "predicted class: %d" % (pred_label)
for i in model.get_labels():
	print "prob(label=%d) = %f" % (i, pred_probability[i])

print "##########################################"
print " Precomputed kernels"
print "##########################################"
samples = [[1, 0, 0, 0, 0], [2, 0, 1, 0, 1], [3, 0, 0, 1, 1], [4, 0, 1, 1, 2]]
problem = svm_problem(labels, samples);
param = svm_parameter(kernel_type=PRECOMPUTED,C = 10,nr_weight = 2,weight_label = [1,0],weight = [10,1])
model = svm_model(problem, param)
pred_label = model.predict(samples[0])
