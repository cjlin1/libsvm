import svmc

from svmc import C_SVC, NU_SVC, ONE_CLASS, EPSILON_SVR, NU_SVR
from svmc import LINEAR, POLY, RBF, SIGMOID

def _int_array(seq):
	size = len(seq)
	array = svmc.int_array(size)
	i = 0
	for item in seq:
		svmc.int_set(array,i,item)
		i = i + 1
	return array

def _double_array(seq):
	size = len(seq)
	array = svmc.double_array(size)
	i = 0
	for item in seq:
		svmc.double_set(array,i,item)
		i = i + 1
	return array

def _free_int_array(x):
	if x != 'NULL':
		svmc.int_destroy(x)

def _free_double_array(x):
	if x != 'NULL':
		svmc.double_destroy(x)

def _int_array_to_list(x,n):
	return map(svmc.int_get,[x]*n,range(n))

def _double_array_to_list(x,n):
	return map(svmc.double_get,[x]*n,range(n))

class svm_parameter:
	
	# default values
	default_parameters = {
	'svm_type' : C_SVC,
	'kernel_type' : RBF,
	'degree' : 3,
	'gamma' : 0,		# 1/k
	'coef0' : 0,
	'nu' : 0.5,
	'cache_size' : 40,
	'C' : 1,
	'eps' : 1e-3,
	'p' : 0.1,
	'shrinking' : 1,
	'nr_weight' : 0,
	'weight_label' : [],
	'weight' : [],
	}

	def __init__(self,**kw):
		self.__dict__['param'] = svmc.new_svm_parameter()
		for attr,val in self.default_parameters.items():
			setattr(self,attr,val)
		for attr,val in kw.items():
			setattr(self,attr,val)

	def __getattr__(self,attr):
		get_func = getattr(svmc,'svm_parameter_%s_get' % (attr))
		return get_func(self.param)

	def __setattr__(self,attr,val):

		if attr == 'weight_label':
			self.__dict__['weight_label_len'] = len(val)
			val = _int_array(val)
			_free_int_array(self.weight_label)
		elif attr == 'weight':
			self.__dict__['weight_len'] = len(val)
			val = _double_array(val)
			_free_double_array(self.weight)

		set_func = getattr(svmc,'svm_parameter_%s_set' % (attr))
		set_func(self.param,val)

	def __repr__(self):
		ret = '<svm_parameter:'
		for name in dir(svmc):
			if name[:len('svm_parameter_')] == 'svm_parameter_' and name[-len('_set'):] == '_set':
				attr = name[len('svm_parameter_'):-len('_set')]
				if attr == 'weight_label':
					ret = ret+' weight_label = %s,' % _int_array_to_list(self.weight_label,self.weight_label_len)
				elif attr == 'weight':
					ret = ret+' weight = %s,' % _double_array_to_list(self.weight,self.weight_len)
				else:
					ret = ret+' %s = %s,' % (attr,getattr(self,attr))
		return ret+'>'

	def __del__(self):
		_free_int_array(self.weight_label)
		_free_double_array(self.weight)
		svmc.delete_svm_parameter(self.param)

def _convert_to_svm_node_array(x):
	""" convert a sequence or mapping to an svm_node array """
	data = svmc.svm_node_array(len(x)+1)
	svmc.svm_node_array_set(data,len(x),-1,0)
	import operator
	if type(x) == type({}):
		keys = x.keys()
		keys.sort()
		j = 0
		for k in keys:
			svmc.svm_node_array_set(data,j,k,x[k])
			j = j + 1
	elif operator.isSequenceType(x):
		for j in range(len(x)):
			svmc.svm_node_array_set(data,j,j+1,x[j])
	else:
		raise TypeError,"data must be a mapping or a sequence"
	
	return data

class svm_problem:
	def __init__(self,y,x):
		assert len(y) == len(x)
		self.prob = prob = svmc.new_svm_problem()
		self.size = size = len(y)

		self.y_array = y_array = svmc.double_array(size)
		for i in range(size):
			svmc.double_set(y_array,i,y[i])

		self.x_matrix = x_matrix = svmc.svm_node_matrix(size)
		self.data = []
		self.maxlen = 0;
		for i in range(size):
			data = _convert_to_svm_node_array(x[i])
			self.data.append(data);
			svmc.svm_node_matrix_set(x_matrix,i,data)
			self.maxlen = max(self.maxlen,len(x[i]))

		svmc.svm_problem_l_set(prob,size)
		svmc.svm_problem_y_set(prob,y_array)
		svmc.svm_problem_x_set(prob,x_matrix)

	def __repr__(self):
		return "<svm_problem: size = %s>" % (self.size)

	def __del__(self):
		svmc.delete_svm_problem(self.prob)
		svmc.double_destroy(self.y_array)
		for i in range(self.size):
			svmc.svm_node_array_destroy(self.data[i])
		svmc.svm_node_matrix_destroy(self.x_matrix)

class svm_model:
	def __init__(self,arg1,arg2=None):
		if arg2 == None:
			# create model from file
			filename = arg1
			self.model = svmc.svm_load_model(filename)
		else:
			# create model from problem and parameter
			prob,param = arg1,arg2
			self.prob = prob
			if param.gamma == 0:
				param.gamma = 1.0/prob.maxlen
			msg = svmc.svm_check_parameter(prob.prob,param.param)
			if msg: raise ValueError, msg
			self.model = svmc.svm_train(prob.prob,param.param)

	def predict(self,x):
		data = _convert_to_svm_node_array(x)
		ret = svmc.svm_predict(self.model,data)
		svmc.svm_node_array_destroy(data)
		return ret

	def save(self,filename):
		svmc.svm_save_model(filename,self.model)

	def __del__(self):
		svmc.svm_destroy_model(self.model)
