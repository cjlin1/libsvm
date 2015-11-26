/**
***
*** Copyright(C) 2015 Intel Corporation and Jaak Simm KU Leuven
*** All rights reserved.
***
*** Redistribution and use in source and binary forms, with or without
*** modification, are permitted provided that the following conditions
*** are met:
***
*** 1. Redistributions of source code must retain the above copyright
*** notice, this list of conditions and the following disclaimer.
***
*** 2. Redistributions in binary form must reproduce the above copyright
*** notice, this list of conditions and the following disclaimer in the
*** documentation and/or other materials provided with the distribution.
***
*** 3. Neither the name of the copyright holder nor the names of its
*** contributors may be used to endorse or promote products derived from
*** this software without specific prior written permission.
***
*** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
*** AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
*** THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
*** PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
*** CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
*** EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
*** PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
*** OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
*** WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
*** OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
*** EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
***
**/

#include <iomanip>

#include "svm.h"
#include "chemo_test.h"

static void exit_with_help()
 {
	 std::clog <<
		 "Usage: svm-train [options] db_path training_path prediction_path out_path [model_path]\n"
		 "options:\n"
		 "-s svm_type : set type of SVM (default 0)\n"
		 "	0 -- C-SVC		(multi-class classification)\n"
		 "	1 -- nu-SVC		(multi-class classification)\n"
		 "	2 -- one-class SVM\n"
		 "	3 -- epsilon-SVR	(regression)\n"
		 "	4 -- nu-SVR		(regression)\n"
		 "-t kernel_type : set type of kernel function (default 2)\n"
		 "	0 -- linear: u'*v\n"
		 "	1 -- polynomial: (gamma*u'*v + coef0)^degree\n"
		 "	2 -- radial basis function: exp(-gamma*|u-v|^2)\n"
		 "	3 -- sigmoid: tanh(gamma*u'*v + coef0)\n"
		 "	4 -- precomputed kernel (kernel values in training_set_file)\n"
		 "	5 -- tanimoto kernel count(u'&v)/count(u'|v)\n"
		 "	6 -- linear binary: u'*v\n"
		 "	7 -- rbf binary: exp(-gamma*|u-v|^2)\n"
		 "	8 -- tanimoto binary: count(u'&v)/count(u'|v)\n"
		 "	9 -- linear numerical: u'*v\n"
		 "-D dot type: set dot type for kernel, default is DEFAULT\n"
		 "	0 -- default: use original libsvm kernels\n"
		 "	1 -- dense: dense optimized kernel\n"
		 "	2 -- sparse: sparse optimized kernel\n"
		 "	3 -- sparse_bin: sparse binary optimized kernel\n"
		 "-d degree : set degree in kernel function (default 3)\n"
		 "-g gamma : set gamma in kernel function (default 1/num_features)\n"
		 "-r coef0 : set coef0 in kernel function (default 0)\n"
		 "-c cost : set the parameter C of C-SVC, epsilon-SVR, and nu-SVR (default 1)\n"
		 "-n nu : set the parameter nu of nu-SVC, one-class SVM, and nu-SVR (default 0.5)\n"
		 "-p epsilon : set the epsilon in loss function of epsilon-SVR (default 0.1)\n"
		 "-m cachesize : set cache memory size in MB (default 100)\n"
		 "-e epsilon : set tolerance of termination criterion (default 0.001)\n"
		 "-h shrinking : whether to use the shrinking heuristics, 0 or 1 (default 1)\n"
		 "-b probability_estimates : whether to train a SVC or SVR model for probability estimates, 0 or 1 (default 0)\n"
		 "-wi weight : set the parameter C of class i to weight*C, for C-SVC (default 1)\n"
		 "-N : cpus to use 0-all possible, default is '1'\n"
		 << std::endl;
	 exit(1);
}

static void parse_cmd_line(int argc, char **argv, int& cpus_count,
	std::string& db_path,
	std::string& train_path,
	std::string& predict_path,
	std::string& model_path,
	std::string& out_path,
	svm_parameter& svm_param)
{
	int i;

	// default values
	svm_param.svm_type = C_SVC;
	svm_param.kernel_type = RBF;
	svm_param.dot_type = DEFAULT;
	svm_param.degree = 3;
	svm_param.gamma = 0;	// 1/num_features
	svm_param.coef0 = 0;
	svm_param.nu = 0.5;
	svm_param.cache_size = 100;
	svm_param.C = 1;
	svm_param.eps = 1e-3;
	svm_param.p = 0.1;
	svm_param.shrinking = 1;
	svm_param.probability = 0;
	svm_param.nr_weight = 0;
	svm_param.weight_label = NULL;
	svm_param.weight = NULL;

	for(i = 1;i<argc;i++)
	{
		if(argv[i][0] != '-') break;
		if(++i >= argc)
			exit_with_help();
		switch(argv[i - 1][1])
		{
		case 's':
			svm_param.svm_type = atoi(argv[i]);
			break;
		case 't':
			svm_param.kernel_type = atoi(argv[i]);
			break;
		case 'd':
			svm_param.degree = atoi(argv[i]);
			break;
		case 'g':
			svm_param.gamma = atof(argv[i]);
			break;
		case 'r':
			svm_param.coef0 = atof(argv[i]);
			break;
		case 'n':
			svm_param.nu = atof(argv[i]);
			break;
		case 'm':
			svm_param.cache_size = atof(argv[i]);
			break;
		case 'c':
			svm_param.C = atof(argv[i]);
			break;
		case 'e':
			svm_param.eps = atof(argv[i]);
			break;
		case 'p':
			svm_param.p = atof(argv[i]);
			break;
		case 'h':
			svm_param.shrinking = atoi(argv[i]);
			break;
		case 'b':
			svm_param.probability = atoi(argv[i]);
			break;
		case 'w':
			++svm_param.nr_weight;
			svm_param.weight_label = (int *)realloc(svm_param.weight_label, sizeof(int)*svm_param.nr_weight);
			svm_param.weight = (double *)realloc(svm_param.weight, sizeof(double)*svm_param.nr_weight);
			svm_param.weight_label[svm_param.nr_weight - 1] = atoi(&argv[i - 1][2]);
			svm_param.weight[svm_param.nr_weight - 1] = atof(argv[i]);
			break;
		case 'N':
			cpus_count = atoi(argv[i]);
			break;
		case 'D':
			svm_param.dot_type = atoi(argv[i]);
			break;
		default:
			std::clog << "Unknown option: -" << argv[i - 1][1] << "\"" << std::endl;
			exit_with_help();
		}
	}

	if(i >= argc - 3)
			exit_with_help();

		db_path = argv[i];
		train_path = argv[i + 1];
		predict_path = argv[i + 2];
		out_path = argv[i + 3];

		if(i<argc - 4)
			model_path = argv[i + 4];
}

static uint64_t fill_svm_data(const chemo::Target<chemo::Compound<>>& target, svm_problem& prob)
{
	int64_t max_index = 0;
	int64_t min_index = 0;

	prob.l = target.activities().size();
	prob.y = new double[prob.l];
	prob.x = new svm_node*[prob.l];

	for(uint64_t i = 0; i<prob.l; i++)
	{
		auto& compound = target.activities()[i].compound();
		prob.x[i] = new svm_node[compound.features().size() + 1];

		prob.y[i] = target.activities()[i].activity() ? 1 : -1;

		size_t size = compound.features().size();
		size_t index = 0;
		for(index = 0; index<size; index++)
		{
			auto feature = compound.features()[index];
			if(max_index<feature) max_index = feature;
			if(min_index>feature) min_index = feature;

			//TODO: chembl and industry seems do not have '-1'
			//for libsvm indexes values are 0-2^32. -1= end of indexes
			//in case of chemogenomics data indexes are -2^31-2^31
			if(feature == -1) throw(std::runtime_error("index should not be \"-1\""));

			prob.x[i][index].index = feature;
			if(!compound.values().empty())
			{
				prob.x[i][index].value = compound.values()[index];
			}
			else
				prob.x[i][index].value = 1;
		}

		prob.x[i][index].index = -1;
		prob.x[i][index].value = 0;
	}

	if(min_index<0 && max_index<0) max_index = -min_index;
	if(min_index<0 && max_index>0) max_index = -min_index + max_index;
	if(min_index>0 && max_index>0) max_index = max_index;
	if(min_index>0 && max_index<0) max_index = 0;
	return max_index;
}

//TODO: workaround to get dec_values, for 2 class
static double svm_predict_dec(const svm_model *model, const svm_node *x)
{
	int nr_class = model->nr_class;
	double *dec_values;
	if(model->param.svm_type == ONE_CLASS ||
		model->param.svm_type == EPSILON_SVR ||
		model->param.svm_type == NU_SVR)
		dec_values = new double[1];
	else
		dec_values = new double[nr_class*(nr_class - 1) / 2];
	double pred_result = svm_predict_values(model, x, dec_values);
	pred_result = dec_values[0];
	delete[] dec_values;
	return pred_result;
}

int main(int argc, char **argv)
{
	svm_set_print_string_function(nullptr);
	int cpus_count = 1;
	std::string db_path;
	std::string train_path;
	std::string predict_path;
	std::string model_path;
	std::string out_path;
	svm_parameter svm_param;
	parse_cmd_line(argc, argv, cpus_count, db_path, train_path, predict_path, model_path, out_path, svm_param);

	if(!cpus_count) cpus_count = tbb::task_scheduler_init::default_num_threads();
	tbb::task_scheduler_init init(cpus_count);
	
	std::clog << "cpus: " << cpus_count << std::endl;
	std::clog << "train: " << train_path << std::endl;
	std::clog << "pred: " << predict_path << std::endl;
	std::clog << "out: " << out_path << std::endl;
	std::clog << "model: " << model_path << std::endl;

	auto compounds = chemo::load_compounds_bin<chemo::Compound<>>(db_path);
	std::clog << "compounds: " << compounds->size() << std::endl;

	tbb::tick_count t = tbb::tick_count::now();
	auto train_target = chemo::load_train_target<chemo::Compound<>>(train_path, *compounds);
	double train_load_time = (tbb::tick_count::now() - t).seconds();

	t = tbb::tick_count::now();
	auto predict_target = chemo::load_pred_target<chemo::Compound<>>(predict_path, *compounds);
	double predict_load_time = (tbb::tick_count::now() - t).seconds();

	std::clog << "LoadTargets times secs[train, pred]: "	<< train_load_time << ", " << predict_load_time	<< std::endl;

	t = tbb::tick_count::now();
	svm_problem train_prob;
	uint64_t max_index = fill_svm_data(*train_target, train_prob);
	if(svm_param.gamma == 0 && max_index>0)
		svm_param.gamma = 1.0 / max_index;
	double fill_svm_train_data_time = (tbb::tick_count::now() - t).seconds();

	/*const char* msg = svm_check_parameter(&train_prob, &svm_param);
	if(msg)
	{
		std::clog << msg << std::endl;
		return 1;
	}*/

	t = tbb::tick_count::now();
	svm_model* model = svm_train(&train_prob, &svm_param);
	double train_time = (tbb::tick_count::now() - t).seconds();

	t = tbb::tick_count::now();
	svm_problem predict_prob;
	fill_svm_data(*predict_target, predict_prob);
	double fill_svm_pred_data_time = (tbb::tick_count::now() - t).seconds();

	t = tbb::tick_count::now();
	//TODO: 2 class only!
	std::vector<double> predictions(predict_prob.l);

	tbb::parallel_for(tbb::blocked_range<std::size_t>(0, predict_prob.l), [&](const tbb::blocked_range<std::size_t>& r)
	{
		for(std::size_t i = r.begin(); i != r.end(); i++)
		{
			predictions[i] = svm_predict_dec(model, predict_prob.x[i]);
		}
	});

	double predict_time = (tbb::tick_count::now() - t).seconds();

	std::clog << "Train&Predict times secs[fill_data_train, fill_data_pred, train, pred]: "
		<< fill_svm_train_data_time << ", "
		<< fill_svm_pred_data_time << ", "
		<< train_time << ", "
		<< predict_time << std::endl;

	t = tbb::tick_count::now();
	std::ofstream pred(out_path);
	for(size_t i = 0; i < predictions.size(); i++)
	{
		pred << predict_target->activities()[i].compound().id() << " " << std::setprecision(8) << predictions[i] << "\n";
	}
	pred.close();
	double out_save_time = (tbb::tick_count::now() - t).seconds();

	t = tbb::tick_count::now();
	if(!model_path.empty())
	{
		if(svm_save_model(model_path.c_str(), model))
		{
			throw(std::runtime_error("can't save model to file: " + model_path));
		}
	}

	svm_free_and_destroy_model(&model);
	svm_destroy_param(&svm_param);

	double model_save_time = (tbb::tick_count::now() - t).seconds();
	std::clog << "SavePredictions times secs[pred,model]: "
		<< out_save_time << ", "
		<< model_save_time
		<< std::endl;

	t = tbb::tick_count::now();
	delete[] train_prob.y;
	for(std::size_t i = 0; i<train_prob.l; i++) delete[] train_prob.x[i];
	delete[] train_prob.x;
	for(std::size_t i = 0; i<predict_prob.l; i++) delete[] predict_prob.x[i];
	delete[] predict_prob.x;
	delete[] predict_prob.y;
	double free_data_time = (tbb::tick_count::now() - t).seconds();
	std::clog << "FreeTrain&PredictData times secs: " << free_data_time << std::endl;
}

