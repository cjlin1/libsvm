#!/usr/bin/env python

import random
from svm import *

def do_cross_validation(prob_x, prob_y, param, nr_fold):
	"Do cross validation for a given SVM problem."
	prob_l = len(prob_y)
	total_correct = 0
	total_error = sumv = sumy = sumvv = sumyy = sumvy = 0.
	prob = svm_problem(prob_y, prob_x)
    	target = cross_validation(prob, param, nr_fold)
	for i in range(prob_l):
		if param.svm_type == EPSILON_SVR or param.svm_type == NU_SVR:
			v = target[i]
			y = prob_y[i]
			sumv = sumv + v
			sumy = sumy + y
			sumvv = sumvv + v * v
			sumyy = sumyy + y * y
			sumvy = sumvy + v * y
			total_error = total_error + (v-y) * (v-y)
		else:
			v = target[i]
			if v == prob_y[i]:
				total_correct = total_correct + 1 
	if param.svm_type == EPSILON_SVR or param.svm_type == NU_SVR:
		print "Cross Validation Mean squared error = %g" % (total_error / prob_l)
		print "Cross Validation Squared correlation coefficient = %g" % (((prob_l * sumvy - sumv * sumy) * (prob_l * sumvy - sumv * sumy)) / ((prob_l * sumvv - sumv * sumv) * (prob_l * sumyy - sumy * sumy)))
	else:
		print "Cross Validation Accuracy = %g%%" % (100.0 * total_correct / prob_l)
