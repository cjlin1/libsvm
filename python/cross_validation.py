#!/usr/bin/env python

import random
from svm import *

def do_cross_validation(prob_x, prob_y, param, nr_fold):
	"Do cross validation for a given SVM problem."
	total_correct = 0
	total_error = sumv = sumy = sumvv = sumyy = sumvy = 0.
	prob_l = len(prob_y)
	for i in range(prob_l):
		j = random.randrange(i,prob_l);
		prob_x[i], prob_x[j] = prob_x[j], prob_x[i]
		prob_y[i], prob_y[j] = prob_y[j], prob_y[i]
	for i in range(nr_fold):
		begin = i * prob_l / nr_fold
		end = (i + 1) * prob_l / nr_fold
		subprob = svm_problem(prob_y[:begin] + prob_y[end:], prob_x[:begin] + prob_x[end:])
		if param.svm_type == EPSILON_SVR or param.svm_type == NU_SVR:
			submodel = svm_model(subprob, param)
			error = 0.0
			for j in range(begin, end):
				v = submodel.predict(prob_x[j])
				y = prob_y[j]
				error = error + (v - y) * (v - y)
				sumv = sumv + v
				sumy = sumy + y
				sumvv = sumvv + v * v
				sumyy = sumyy + y * y
				sumvy = sumvy + v * y
			print "Mean squared error = %g" % (error / (end - begin))
			total_error = total_error + error
		else:
			submodel = svm_model(subprob, param)
			correct = 0
			for j in range(begin, end):
				v = submodel.predict(prob_x[j])
				if v == prob_y[j]: correct = correct + 1
			print "Accuracy = %g%% (%d/%d)" % (100.0 * correct / (end - begin), correct, (end - begin))
			total_correct = total_correct + correct
	if param.svm_type == EPSILON_SVR or param.svm_type == NU_SVR:
		print "Cross Validation Mean squared error = %g" % (total_error / prob_l)
		print "Cross Validation Squared correlation coefficient = %g" % (((prob_l * sumvy - sumv * sumy) * (prob_l * sumvy - sumv * sumy)) / ((prob_l * sumvv - sumv * sumv) * (prob_l * sumyy - sumy * sumy)))
	else:
		print "Cross Validation Accuracy = %g%%" % (100.0 * total_correct / prob_l)
