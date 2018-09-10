#!/usr/bin/env python

from __future__ import print_function
from array import array
import sys

try:
	import scipy
	from scipy import sparse
except:
	scipy = None
	sparse = None


__all__ = ['svm_read_problem', 'evaluations', 'csr_find_scale_param', 'csr_scale']

def svm_read_problem(data_file_name, return_scipy=False):
	"""
	svm_read_problem(data_file_name, return_scipy=False) -> [y, x], y: list, x: list of dictionary
	svm_read_problem(data_file_name, return_scipy=True)  -> [y, x], y: ndarray, x: csr_matrix

	Read LIBSVM-format data from data_file_name and return labels y
	and data instances x.
	"""
	if scipy != None and return_scipy:
		prob_y = array('d')
		prob_x = array('d')
		row_ptr = array('l', [0])
		col_idx = array('l')
	else:
		prob_y = []
		prob_x = []
		row_ptr = [0]
		col_idx = []
	indx_start = 1
	for i, line in enumerate(open(data_file_name)):
		line = line.split(None, 1)
		# In case an instance with all zero features
		if len(line) == 1: line += ['']
		label, features = line
		prob_y.append(float(label))
		if scipy != None and return_scipy:
			nz = 0
			for e in features.split():
				ind, val = e.split(":")
				if ind == '0':
					indx_start = 0
				val = float(val)
				if val != 0:
					col_idx.append(int(ind)-indx_start)
					prob_x.append(val)
					nz += 1
			row_ptr.append(row_ptr[-1]+nz)
		else:
			xi = {}
			for e in features.split():
				ind, val = e.split(":")
				xi[int(ind)] = float(val)
			prob_x += [xi]
	if scipy != None and return_scipy:
		prob_y = scipy.frombuffer(prob_y, dtype='d')
		prob_x = scipy.frombuffer(prob_x, dtype='d')
		col_idx = scipy.frombuffer(col_idx, dtype='l')
		row_ptr = scipy.frombuffer(row_ptr, dtype='l')
		prob_x = sparse.csr_matrix((prob_x, col_idx, row_ptr))
	return (prob_y, prob_x)

def evaluations_scipy(ty, pv):
	"""
	evaluations_scipy(ty, pv) -> (ACC, MSE, SCC)
	ty, pv: ndarray

	Calculate accuracy, mean squared error and squared correlation coefficient
	using the true values (ty) and predicted values (pv).
	"""
	if not (scipy != None and isinstance(ty, scipy.ndarray) and isinstance(pv, scipy.ndarray)):
		raise TypeError("type of ty and pv must be ndarray")
	if len(ty) != len(pv):
		raise ValueError("len(ty) must be equal to len(pv)")
	ACC = 100.0*(ty == pv).mean()
	MSE = ((ty - pv)**2).mean()
	l = len(ty)
	sumv = pv.sum()
	sumy = ty.sum()
	sumvy = (pv*ty).sum()
	sumvv = (pv*pv).sum()
	sumyy = (ty*ty).sum()
	with scipy.errstate(all = 'raise'):
		try:
			SCC = ((l*sumvy-sumv*sumy)*(l*sumvy-sumv*sumy))/((l*sumvv-sumv*sumv)*(l*sumyy-sumy*sumy))
		except:
			SCC = float('nan')
	return (float(ACC), float(MSE), float(SCC))

def evaluations(ty, pv, useScipy = True):
	"""
	evaluations(ty, pv, useScipy) -> (ACC, MSE, SCC)
	ty, pv: list, tuple or ndarray
	useScipy: convert ty, pv to ndarray, and use scipy functions for the evaluation

	Calculate accuracy, mean squared error and squared correlation coefficient
	using the true values (ty) and predicted values (pv).
	"""
	if scipy != None and useScipy:
		return evaluations_scipy(scipy.asarray(ty), scipy.asarray(pv))
	if len(ty) != len(pv):
		raise ValueError("len(ty) must be equal to len(pv)")
	total_correct = total_error = 0
	sumv = sumy = sumvv = sumyy = sumvy = 0
	for v, y in zip(pv, ty):
		if y == v:
			total_correct += 1
		total_error += (v-y)*(v-y)
		sumv += v
		sumy += y
		sumvv += v*v
		sumyy += y*y
		sumvy += v*y
	l = len(ty)
	ACC = 100.0*total_correct/l
	MSE = total_error/l
	try:
		SCC = ((l*sumvy-sumv*sumy)*(l*sumvy-sumv*sumy))/((l*sumvv-sumv*sumv)*(l*sumyy-sumy*sumy))
	except:
		SCC = float('nan')
	return (float(ACC), float(MSE), float(SCC))

def csr_find_scale_param(x, lower=-1, upper=1):
	assert isinstance(x, sparse.csr_matrix)
	assert lower < upper
	l, n = x.shape
	feat_min = x.min(axis=0).toarray().flatten()
	feat_max = x.max(axis=0).toarray().flatten()
	coef = (feat_max - feat_min) / (upper - lower)
	coef[coef != 0] = 1.0 / coef[coef != 0]

	# (x - ones(l,1) * feat_min') * diag(coef) + lower
	# = x * diag(coef) - ones(l, 1) * (feat_min' * diag(coef)) + lower
	# = x * diag(coef) + ones(l, 1) * (-feat_min' * diag(coef) + lower)
	# = x * diag(coef) + ones(l, 1) * offset'
	offset = -feat_min * coef + lower
	offset[coef == 0] = 0

	if sum(offset != 0) * l > 3 * x.getnnz():
		print(
			"WARNING: The #nonzeros of the scaled data is at least 2 times larger than the original one.\n"
			"If feature values are non-negative and sparse, set lower=0 rather than the default lower=-1.",
			file=sys.stderr)

	return {'coef':coef, 'offset':offset}

def csr_scale(x, scale_param):
	assert isinstance(x, sparse.csr_matrix)

	offset = scale_param['offset']
	coef = scale_param['coef']
	assert len(coef) == len(offset)

	l, n = x.shape

	if not n == len(coef):
		print("WARNING: The dimension of scaling parameters and feature number do not match.", file=sys.stderr)
		coef = resize(coef, n)
		offset = resize(offset, n)

	# scaled_x = x * diag(coef) + ones(l, 1) * offset'
	offset = sparse.csr_matrix(offset.reshape(1, n))
	offset = sparse.vstack([offset] * l, format='csr', dtype=x.dtype)
	scaled_x = x.dot(sparse.diags(coef, 0, shape=(n, n))) + offset

	if scaled_x.getnnz() > x.getnnz():
		print(
			"WARNING: original #nonzeros %d\n" % x.getnnz() +
			"       > new      #nonzeros %d\n" % scaled_x.getnnz() +
			"If feature values are non-negative and sparse, get scale_param by setting lower=0 rather than the default lower=-1.",
			file=sys.stderr)

	return scaled_x
