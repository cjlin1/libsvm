#!/usr/bin/env python

from ctypes import *
from ctypes.util import find_library
from os import path
import sys

try:
	import scipy
	from scipy import sparse
except:
	scipy = None
	sparse = None

if sys.version_info[0] < 3:
	range = xrange
	from itertools import izip as zip

__all__ = ['libsvm', 'svm_problem', 'svm_parameter',
           'toPyModel', 'gen_svm_nodearray', 'print_null', 'svm_node', 'C_SVC',
           'EPSILON_SVR', 'LINEAR', 'NU_SVC', 'NU_SVR', 'ONE_CLASS',
           'POLY', 'PRECOMPUTED', 'PRINT_STRING_FUN', 'RBF',
           'SIGMOID', 'c_double', 'svm_model']

try:
	dirname = path.dirname(path.abspath(__file__))
	if sys.platform == 'win32':
		libsvm = CDLL(path.join(dirname, r'..\windows\libsvm.dll'))
	else:
		libsvm = CDLL(path.join(dirname, '../libsvm.so.2'))
except:
# For unix the prefix 'lib' is not considered.
	if find_library('svm'):
		libsvm = CDLL(find_library('svm'))
	elif find_library('libsvm'):
		libsvm = CDLL(find_library('libsvm'))
	else:
		raise Exception('LIBSVM library not found.')

C_SVC = 0
NU_SVC = 1
ONE_CLASS = 2
EPSILON_SVR = 3
NU_SVR = 4

LINEAR = 0
POLY = 1
RBF = 2
SIGMOID = 3
PRECOMPUTED = 4

PRINT_STRING_FUN = CFUNCTYPE(None, c_char_p)
def print_null(s):
	return

def genFields(names, types):
	return list(zip(names, types))

def fillprototype(f, restype, argtypes):
	f.restype = restype
	f.argtypes = argtypes

class svm_node(Structure):
	_names = ["index", "value"]
	_types = [c_int, c_double]
	_fields_ = genFields(_names, _types)

	def __init__(self, index=-1, value=0):
		self.index, self.value = index, value

	def __str__(self):
		return '%d:%g' % (self.index, self.value)

def gen_svm_nodearray(xi, feature_max=None, isKernel=False):
	if feature_max:
		assert(isinstance(feature_max, int))

	xi_shift = 0 # ensure correct indices of xi
	if scipy and isinstance(xi, tuple) and len(xi) == 2\
			and isinstance(xi[0], scipy.ndarray) and isinstance(xi[1], scipy.ndarray): # for a sparse vector
		if not isKernel:
			index_range = xi[0] + 1 # index starts from 1
		else:
			index_range = xi[0] # index starts from 0 for precomputed kernel
		if feature_max:
			index_range = index_range[scipy.where(index_range <= feature_max)]
	elif scipy and isinstance(xi, scipy.ndarray):
		if not isKernel:
			xi_shift = 1
			index_range = xi.nonzero()[0] + 1 # index starts from 1
		else:
			index_range = scipy.arange(0, len(xi)) # index starts from 0 for precomputed kernel
		if feature_max:
			index_range = index_range[scipy.where(index_range <= feature_max)]
	elif isinstance(xi, (dict, list, tuple)):
		if isinstance(xi, dict):
			index_range = xi.keys()
		elif isinstance(xi, (list, tuple)):
			if not isKernel:
				xi_shift = 1
				index_range = range(1, len(xi) + 1) # index starts from 1
			else:
				index_range = range(0, len(xi)) # index starts from 0 for precomputed kernel

		if feature_max:
			index_range = filter(lambda j: j <= feature_max, index_range)
		if not isKernel:
			index_range = filter(lambda j:xi[j-xi_shift] != 0, index_range)

		index_range = sorted(index_range)
	else:
		raise TypeError('xi should be a dictionary, list, tuple, 1-d numpy array, or tuple of (index, data)')

	ret = (svm_node*(len(index_range)+1))()
	ret[-1].index = -1

	if scipy and isinstance(xi, tuple) and len(xi) == 2\
			and isinstance(xi[0], scipy.ndarray) and isinstance(xi[1], scipy.ndarray): # for a sparse vector
		for idx, j in enumerate(index_range):
			ret[idx].index = j
			ret[idx].value = (xi[1])[idx]
	else:
		for idx, j in enumerate(index_range):
			ret[idx].index = j
			ret[idx].value = xi[j - xi_shift]

	max_idx = 0
	if len(index_range) > 0:
		max_idx = index_range[-1]
	return ret, max_idx

try:
	from numba import jit
	jit_enabled = True
except:
	jit = lambda x: x
	jit_enabled = False

@jit
def csr_to_problem_jit(l, x_val, x_ind, x_rowptr, prob_val, prob_ind, prob_rowptr, indx_start):
	for i in range(l):
		b1,e1 = x_rowptr[i], x_rowptr[i+1]
		b2,e2 = prob_rowptr[i], prob_rowptr[i+1]-1
		for j in range(b1,e1):
			prob_ind[j-b1+b2] = x_ind[j]+indx_start
			prob_val[j-b1+b2] = x_val[j]
def csr_to_problem_nojit(l, x_val, x_ind, x_rowptr, prob_val, prob_ind, prob_rowptr, indx_start):
	for i in range(l):
		x_slice = slice(x_rowptr[i], x_rowptr[i+1])
		prob_slice = slice(prob_rowptr[i], prob_rowptr[i+1]-1)
		prob_ind[prob_slice] = x_ind[x_slice]+indx_start
		prob_val[prob_slice] = x_val[x_slice]

def csr_to_problem(x, prob, isKernel):
	if not x.has_sorted_indices:
		x.sort_indices()

	# Extra space for termination node and (possibly) bias term
	x_space = prob.x_space = scipy.empty((x.nnz+x.shape[0]), dtype=svm_node)
	prob.rowptr = x.indptr.copy()
	prob.rowptr[1:] += scipy.arange(1,x.shape[0]+1)
	prob_ind = x_space["index"]
	prob_val = x_space["value"]
	prob_ind[:] = -1
	if not isKernel:
		indx_start = 1 # index starts from 1
	else:
		indx_start = 0 # index starts from 0 for precomputed kernel
	if jit_enabled:
		csr_to_problem_jit(x.shape[0], x.data, x.indices, x.indptr, prob_val, prob_ind, prob.rowptr, indx_start)
	else:
		csr_to_problem_nojit(x.shape[0], x.data, x.indices, x.indptr, prob_val, prob_ind, prob.rowptr, indx_start)

class svm_problem(Structure):
	_names = ["l", "y", "x"]
	_types = [c_int, POINTER(c_double), POINTER(POINTER(svm_node))]
	_fields_ = genFields(_names, _types)

	def __init__(self, y, x, isKernel=False):
		if (not isinstance(y, (list, tuple))) and (not (scipy and isinstance(y, scipy.ndarray))):
			raise TypeError("type of y: {0} is not supported!".format(type(y)))

		if isinstance(x, (list, tuple)):
			if len(y) != len(x):
				raise ValueError("len(y) != len(x)")
		elif scipy != None and isinstance(x, (scipy.ndarray, sparse.spmatrix)):
			if len(y) != x.shape[0]:
				raise ValueError("len(y) != len(x)")
			if isinstance(x, scipy.ndarray):
				x = scipy.ascontiguousarray(x) # enforce row-major
			if isinstance(x, sparse.spmatrix):
				x = x.tocsr()
				pass
		else:
			raise TypeError("type of x: {0} is not supported!".format(type(x)))
		self.l = l = len(y)

		max_idx = 0
		x_space = self.x_space = []
		if scipy != None and isinstance(x, sparse.csr_matrix):
			csr_to_problem(x, self, isKernel)
			max_idx = x.shape[1]
		else:
			for i, xi in enumerate(x):
				tmp_xi, tmp_idx = gen_svm_nodearray(xi,isKernel=isKernel)
				x_space += [tmp_xi]
				max_idx = max(max_idx, tmp_idx)
		self.n = max_idx

		self.y = (c_double * l)()
		if scipy != None and isinstance(y, scipy.ndarray):
			scipy.ctypeslib.as_array(self.y, (self.l,))[:] = y
		else:
			for i, yi in enumerate(y): self.y[i] = yi

		self.x = (POINTER(svm_node) * l)()
		if scipy != None and isinstance(x, sparse.csr_matrix):
			base = addressof(self.x_space.ctypes.data_as(POINTER(svm_node))[0])
			x_ptr = cast(self.x, POINTER(c_uint64))
			x_ptr = scipy.ctypeslib.as_array(x_ptr,(self.l,))
			x_ptr[:] = self.rowptr[:-1]*sizeof(svm_node)+base
		else:
			for i, xi in enumerate(self.x_space): self.x[i] = xi

class svm_parameter(Structure):
	_names = ["svm_type", "kernel_type", "degree", "gamma", "coef0",
			"cache_size", "eps", "C", "nr_weight", "weight_label", "weight",
			"nu", "p", "shrinking", "probability"]
	_types = [c_int, c_int, c_int, c_double, c_double,
			c_double, c_double, c_double, c_int, POINTER(c_int), POINTER(c_double),
			c_double, c_double, c_int, c_int]
	_fields_ = genFields(_names, _types)

	def __init__(self, options = None):
		if options == None:
			options = ''
		self.parse_options(options)

	def __str__(self):
		s = ''
		attrs = svm_parameter._names + list(self.__dict__.keys())
		values = map(lambda attr: getattr(self, attr), attrs)
		for attr, val in zip(attrs, values):
			s += (' %s: %s\n' % (attr, val))
		s = s.strip()

		return s

	def set_to_default_values(self):
		self.svm_type = C_SVC;
		self.kernel_type = RBF
		self.degree = 3
		self.gamma = 0
		self.coef0 = 0
		self.nu = 0.5
		self.cache_size = 100
		self.C = 1
		self.eps = 0.001
		self.p = 0.1
		self.shrinking = 1
		self.probability = 0
		self.nr_weight = 0
		self.weight_label = None
		self.weight = None
		self.cross_validation = False
		self.nr_fold = 0
		self.print_func = cast(None, PRINT_STRING_FUN)

	def parse_options(self, options):
		if isinstance(options, list):
			argv = options
		elif isinstance(options, str):
			argv = options.split()
		else:
			raise TypeError("arg 1 should be a list or a str.")
		self.set_to_default_values()
		self.print_func = cast(None, PRINT_STRING_FUN)
		weight_label = []
		weight = []

		i = 0
		while i < len(argv):
			if argv[i] == "-s":
				i = i + 1
				self.svm_type = int(argv[i])
			elif argv[i] == "-t":
				i = i + 1
				self.kernel_type = int(argv[i])
			elif argv[i] == "-d":
				i = i + 1
				self.degree = int(argv[i])
			elif argv[i] == "-g":
				i = i + 1
				self.gamma = float(argv[i])
			elif argv[i] == "-r":
				i = i + 1
				self.coef0 = float(argv[i])
			elif argv[i] == "-n":
				i = i + 1
				self.nu = float(argv[i])
			elif argv[i] == "-m":
				i = i + 1
				self.cache_size = float(argv[i])
			elif argv[i] == "-c":
				i = i + 1
				self.C = float(argv[i])
			elif argv[i] == "-e":
				i = i + 1
				self.eps = float(argv[i])
			elif argv[i] == "-p":
				i = i + 1
				self.p = float(argv[i])
			elif argv[i] == "-h":
				i = i + 1
				self.shrinking = int(argv[i])
			elif argv[i] == "-b":
				i = i + 1
				self.probability = int(argv[i])
			elif argv[i] == "-q":
				self.print_func = PRINT_STRING_FUN(print_null)
			elif argv[i] == "-v":
				i = i + 1
				self.cross_validation = 1
				self.nr_fold = int(argv[i])
				if self.nr_fold < 2:
					raise ValueError("n-fold cross validation: n must >= 2")
			elif argv[i].startswith("-w"):
				i = i + 1
				self.nr_weight += 1
				weight_label += [int(argv[i-1][2:])]
				weight += [float(argv[i])]
			else:
				raise ValueError("Wrong options")
			i += 1

		libsvm.svm_set_print_string_function(self.print_func)
		self.weight_label = (c_int*self.nr_weight)()
		self.weight = (c_double*self.nr_weight)()
		for i in range(self.nr_weight):
			self.weight[i] = weight[i]
			self.weight_label[i] = weight_label[i]

class svm_model(Structure):
	_names = ['param', 'nr_class', 'l', 'SV', 'sv_coef', 'rho',
			'probA', 'probB', 'sv_indices', 'label', 'nSV', 'free_sv']
	_types = [svm_parameter, c_int, c_int, POINTER(POINTER(svm_node)),
			POINTER(POINTER(c_double)), POINTER(c_double),
			POINTER(c_double), POINTER(c_double), POINTER(c_int),
			POINTER(c_int), POINTER(c_int), c_int]
	_fields_ = genFields(_names, _types)

	def __init__(self):
		self.__createfrom__ = 'python'

	def __del__(self):
		# free memory created by C to avoid memory leak
		if hasattr(self, '__createfrom__') and self.__createfrom__ == 'C':
			libsvm.svm_free_and_destroy_model(pointer(pointer(self)))

	def get_svm_type(self):
		return libsvm.svm_get_svm_type(self)

	def get_nr_class(self):
		return libsvm.svm_get_nr_class(self)

	def get_svr_probability(self):
		return libsvm.svm_get_svr_probability(self)

	def get_labels(self):
		nr_class = self.get_nr_class()
		labels = (c_int * nr_class)()
		libsvm.svm_get_labels(self, labels)
		return labels[:nr_class]

	def get_sv_indices(self):
		total_sv = self.get_nr_sv()
		sv_indices = (c_int * total_sv)()
		libsvm.svm_get_sv_indices(self, sv_indices)
		return sv_indices[:total_sv]

	def get_nr_sv(self):
		return libsvm.svm_get_nr_sv(self)

	def is_probability_model(self):
		return (libsvm.svm_check_probability_model(self) == 1)

	def get_sv_coef(self):
		return [tuple(self.sv_coef[j][i] for j in range(self.nr_class - 1))
				for i in range(self.l)]

	def get_SV(self):
		result = []
		for sparse_sv in self.SV[:self.l]:
			row = dict()

			i = 0
			while True:
				if sparse_sv[i].index == -1:
					break
				row[sparse_sv[i].index] = sparse_sv[i].value
				i += 1

			result.append(row)
		return result

def toPyModel(model_ptr):
	"""
	toPyModel(model_ptr) -> svm_model

	Convert a ctypes POINTER(svm_model) to a Python svm_model
	"""
	if bool(model_ptr) == False:
		raise ValueError("Null pointer")
	m = model_ptr.contents
	m.__createfrom__ = 'C'
	return m

fillprototype(libsvm.svm_train, POINTER(svm_model), [POINTER(svm_problem), POINTER(svm_parameter)])
fillprototype(libsvm.svm_cross_validation, None, [POINTER(svm_problem), POINTER(svm_parameter), c_int, POINTER(c_double)])

fillprototype(libsvm.svm_save_model, c_int, [c_char_p, POINTER(svm_model)])
fillprototype(libsvm.svm_load_model, POINTER(svm_model), [c_char_p])

fillprototype(libsvm.svm_get_svm_type, c_int, [POINTER(svm_model)])
fillprototype(libsvm.svm_get_nr_class, c_int, [POINTER(svm_model)])
fillprototype(libsvm.svm_get_labels, None, [POINTER(svm_model), POINTER(c_int)])
fillprototype(libsvm.svm_get_sv_indices, None, [POINTER(svm_model), POINTER(c_int)])
fillprototype(libsvm.svm_get_nr_sv, c_int, [POINTER(svm_model)])
fillprototype(libsvm.svm_get_svr_probability, c_double, [POINTER(svm_model)])

fillprototype(libsvm.svm_predict_values, c_double, [POINTER(svm_model), POINTER(svm_node), POINTER(c_double)])
fillprototype(libsvm.svm_predict, c_double, [POINTER(svm_model), POINTER(svm_node)])
fillprototype(libsvm.svm_predict_probability, c_double, [POINTER(svm_model), POINTER(svm_node), POINTER(c_double)])

fillprototype(libsvm.svm_free_model_content, None, [POINTER(svm_model)])
fillprototype(libsvm.svm_free_and_destroy_model, None, [POINTER(POINTER(svm_model))])
fillprototype(libsvm.svm_destroy_param, None, [POINTER(svm_parameter)])

fillprototype(libsvm.svm_check_parameter, c_char_p, [POINTER(svm_problem), POINTER(svm_parameter)])
fillprototype(libsvm.svm_check_probability_model, c_int, [POINTER(svm_model)])
fillprototype(libsvm.svm_set_print_string_function, None, [PRINT_STRING_FUN])
