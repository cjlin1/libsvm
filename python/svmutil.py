#!/usr/bin/env python

import os, sys
sys.path = [os.path.dirname(os.path.abspath(__file__))] + sys.path
from svm import *
from svm import __all__ as svm_all
from svm import scipy, sparse
from commonutil import *
from commonutil import __all__ as common_all

if sys.version_info[0] < 3:
	range = xrange
	from itertools import izip as zip

__all__ = ['svm_load_model', 'svm_predict', 'svm_save_model', 'svm_train'] + svm_all + common_all


def svm_load_model(model_file_name):
	"""
	svm_load_model(model_file_name) -> model

	Load a LIBSVM model from model_file_name and return.
	"""
	model = libsvm.svm_load_model(model_file_name.encode())
	if not model:
		print("can't open model file %s" % model_file_name)
		return None
	model = toPyModel(model)
	return model

def svm_save_model(model_file_name, model):
	"""
	svm_save_model(model_file_name, model) -> None

	Save a LIBSVM model to the file model_file_name.
	"""
	libsvm.svm_save_model(model_file_name.encode(), model)

def svm_train(arg1, arg2=None, arg3=None):
	"""
	svm_train(y, x [, options]) -> model | ACC | MSE

	y: a list/tuple/ndarray of l true labels (type must be int/double).

	x: 1. a list/tuple of l training instances. Feature vector of
	      each training instance is a list/tuple or dictionary.

	   2. an l * n numpy ndarray or scipy spmatrix (n: number of features).

	svm_train(prob [, options]) -> model | ACC | MSE
	svm_train(prob, param) -> model | ACC| MSE

	Train an SVM model from data (y, x) or an svm_problem prob using
	'options' or an svm_parameter param.
	If '-v' is specified in 'options' (i.e., cross validation)
	either accuracy (ACC) or mean-squared error (MSE) is returned.
	options:
	    -s svm_type : set type of SVM (default 0)
	        0 -- C-SVC		(multi-class classification)
	        1 -- nu-SVC		(multi-class classification)
	        2 -- one-class SVM
	        3 -- epsilon-SVR	(regression)
	        4 -- nu-SVR		(regression)
	    -t kernel_type : set type of kernel function (default 2)
	        0 -- linear: u'*v
	        1 -- polynomial: (gamma*u'*v + coef0)^degree
	        2 -- radial basis function: exp(-gamma*|u-v|^2)
	        3 -- sigmoid: tanh(gamma*u'*v + coef0)
	        4 -- precomputed kernel (kernel values in training_set_file)
	    -d degree : set degree in kernel function (default 3)
	    -g gamma : set gamma in kernel function (default 1/num_features)
	    -r coef0 : set coef0 in kernel function (default 0)
	    -c cost : set the parameter C of C-SVC, epsilon-SVR, and nu-SVR (default 1)
	    -n nu : set the parameter nu of nu-SVC, one-class SVM, and nu-SVR (default 0.5)
	    -p epsilon : set the epsilon in loss function of epsilon-SVR (default 0.1)
	    -m cachesize : set cache memory size in MB (default 100)
	    -e epsilon : set tolerance of termination criterion (default 0.001)
	    -h shrinking : whether to use the shrinking heuristics, 0 or 1 (default 1)
	    -b probability_estimates : whether to train a SVC or SVR model for probability estimates, 0 or 1 (default 0)
	    -wi weight : set the parameter C of class i to weight*C, for C-SVC (default 1)
	    -v n: n-fold cross validation mode
	    -q : quiet mode (no outputs)
	"""
	prob, param = None, None
	if isinstance(arg1, (list, tuple)) or (scipy and isinstance(arg1, scipy.ndarray)):
		assert isinstance(arg2, (list, tuple)) or (scipy and isinstance(arg2, (scipy.ndarray, sparse.spmatrix)))
		y, x, options = arg1, arg2, arg3
		param = svm_parameter(options)
		prob = svm_problem(y, x, isKernel=(param.kernel_type == PRECOMPUTED))
	elif isinstance(arg1, svm_problem):
		prob = arg1
		if isinstance(arg2, svm_parameter):
			param = arg2
		else:
			param = svm_parameter(arg2)
	if prob == None or param == None:
		raise TypeError("Wrong types for the arguments")

	if param.kernel_type == PRECOMPUTED:
		for i in range(prob.l):
			xi = prob.x[i]
			idx, val = xi[0].index, xi[0].value
			if idx != 0:
				raise ValueError('Wrong input format: first column must be 0:sample_serial_number')
			if val <= 0 or val > prob.n:
				raise ValueError('Wrong input format: sample_serial_number out of range')

	if param.gamma == 0 and prob.n > 0:
		param.gamma = 1.0 / prob.n
	libsvm.svm_set_print_string_function(param.print_func)
	err_msg = libsvm.svm_check_parameter(prob, param)
	if err_msg:
		raise ValueError('Error: %s' % err_msg)

	if param.cross_validation:
		l, nr_fold = prob.l, param.nr_fold
		target = (c_double * l)()
		libsvm.svm_cross_validation(prob, param, nr_fold, target)
		ACC, MSE, SCC = evaluations(prob.y[:l], target[:l])
		if param.svm_type in [EPSILON_SVR, NU_SVR]:
			print("Cross Validation Mean squared error = %g" % MSE)
			print("Cross Validation Squared correlation coefficient = %g" % SCC)
			return MSE
		else:
			print("Cross Validation Accuracy = %g%%" % ACC)
			return ACC
	else:
		m = libsvm.svm_train(prob, param)
		m = toPyModel(m)

		# If prob is destroyed, data including SVs pointed by m can remain.
		m.x_space = prob.x_space
		return m

def svm_predict(y, x, m, options=""):
	"""
	svm_predict(y, x, m [, options]) -> (p_labels, p_acc, p_vals)

	y: a list/tuple/ndarray of l true labels (type must be int/double).
	   It is used for calculating the accuracy. Use [] if true labels are
	   unavailable.

	x: 1. a list/tuple of l training instances. Feature vector of
	      each training instance is a list/tuple or dictionary.

	   2. an l * n numpy ndarray or scipy spmatrix (n: number of features).

	Predict data (y, x) with the SVM model m.
	options:
	    -b probability_estimates: whether to predict probability estimates,
	        0 or 1 (default 0); for one-class SVM only 0 is supported.
	    -q : quiet mode (no outputs).

	The return tuple contains
	p_labels: a list of predicted labels
	p_acc: a tuple including  accuracy (for classification), mean-squared
	       error, and squared correlation coefficient (for regression).
	p_vals: a list of decision values or probability estimates (if '-b 1'
	        is specified). If k is the number of classes, for decision values,
	        each element includes results of predicting k(k-1)/2 binary-class
	        SVMs. For probabilities, each element contains k values indicating
	        the probability that the testing instance is in each class.
	        Note that the order of classes here is the same as 'model.label'
	        field in the model structure.
	"""

	def info(s):
		print(s)

	if scipy and isinstance(x, scipy.ndarray):
		x = scipy.ascontiguousarray(x) # enforce row-major
	elif sparse and isinstance(x, sparse.spmatrix):
		x = x.tocsr()
	elif not isinstance(x, (list, tuple)):
		raise TypeError("type of x: {0} is not supported!".format(type(x)))

	if (not isinstance(y, (list, tuple))) and (not (scipy and isinstance(y, scipy.ndarray))):
		raise TypeError("type of y: {0} is not supported!".format(type(y)))

	predict_probability = 0
	argv = options.split()
	i = 0
	while i < len(argv):
		if argv[i] == '-b':
			i += 1
			predict_probability = int(argv[i])
		elif argv[i] == '-q':
			info = print_null
		else:
			raise ValueError("Wrong options")
		i+=1

	svm_type = m.get_svm_type()
	is_prob_model = m.is_probability_model()
	nr_class = m.get_nr_class()
	pred_labels = []
	pred_values = []

	if scipy and isinstance(x, sparse.spmatrix):
		nr_instance = x.shape[0]
	else:
		nr_instance = len(x)

	if predict_probability:
		if not is_prob_model:
			raise ValueError("Model does not support probabiliy estimates")

		if svm_type in [NU_SVR, EPSILON_SVR]:
			info("Prob. model for test data: target value = predicted value + z,\n"
			"z: Laplace distribution e^(-|z|/sigma)/(2sigma),sigma=%g" % m.get_svr_probability());
			nr_class = 0

		prob_estimates = (c_double * nr_class)()
		for i in range(nr_instance):
			if scipy and isinstance(x, sparse.spmatrix):
				indslice = slice(x.indptr[i], x.indptr[i+1])
				xi, idx = gen_svm_nodearray((x.indices[indslice], x.data[indslice]), isKernel=(m.param.kernel_type == PRECOMPUTED))
			else:
				xi, idx = gen_svm_nodearray(x[i], isKernel=(m.param.kernel_type == PRECOMPUTED))
			label = libsvm.svm_predict_probability(m, xi, prob_estimates)
			values = prob_estimates[:nr_class]
			pred_labels += [label]
			pred_values += [values]
	else:
		if is_prob_model:
			info("Model supports probability estimates, but disabled in predicton.")
		if svm_type in (ONE_CLASS, EPSILON_SVR, NU_SVC):
			nr_classifier = 1
		else:
			nr_classifier = nr_class*(nr_class-1)//2
		dec_values = (c_double * nr_classifier)()
		for i in range(nr_instance):
			if scipy and isinstance(x, sparse.spmatrix):
				indslice = slice(x.indptr[i], x.indptr[i+1])
				xi, idx = gen_svm_nodearray((x.indices[indslice], x.data[indslice]), isKernel=(m.param.kernel_type == PRECOMPUTED))
			else:
				xi, idx = gen_svm_nodearray(x[i], isKernel=(m.param.kernel_type == PRECOMPUTED))
			label = libsvm.svm_predict_values(m, xi, dec_values)
			if(nr_class == 1):
				values = [1]
			else:
				values = dec_values[:nr_classifier]
			pred_labels += [label]
			pred_values += [values]

	if len(y) == 0:
		y = [0] * nr_instance
	ACC, MSE, SCC = evaluations(y, pred_labels)

	if svm_type in [EPSILON_SVR, NU_SVR]:
		info("Mean squared error = %g (regression)" % MSE)
		info("Squared correlation coefficient = %g (regression)" % SCC)
	else:
		info("Accuracy = %g%% (%d/%d) (classification)" % (ACC, int(round(nr_instance*ACC/100)), nr_instance))

	return pred_labels, (ACC, MSE, SCC), pred_values
