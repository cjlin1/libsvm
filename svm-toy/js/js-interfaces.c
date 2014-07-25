#include<stdio.h>
#include<stdlib.h>
#include<errno.h>
#include<string.h>
#include<ctype.h>
#include "svm.h"
#define Malloc(type,n) (type *)malloc((n)*sizeof(type))

void print_null(const char *s) {}

void exit_with_help(){exit(1);}

void parse_command_line(const char* input_command, struct svm_parameter* param)
{
	void (*print_func)(const char*) = NULL;	// default printing to stdout
	char command[256];
	char *curr = NULL;
	char *prev = NULL;

	strcpy(command, input_command);
	curr = strtok(command," \t\n"); // label

	// default values
	param->svm_type = C_SVC;
	param->kernel_type = RBF;
	param->degree = 3;
	param->gamma = 0;	// 1/num_features
	param->coef0 = 0;
	param->nu = 0.5;
	param->cache_size = 100;
	param->C = 1;
	param->eps = 1e-3;
	param->p = 0.1;
	param->shrinking = 1;
	param->probability = 0;
	param->nr_weight = 0;
	param->weight_label = NULL;
	param->weight = NULL;

	if(curr == NULL) return;

	do
	{
		if(curr[0] != '-') break;
		if(curr[1] == 'q') continue; // no quiet mode for toy
		
		prev = curr;
		if((curr = strtok(NULL, " \t\n")) == NULL)
			exit_with_help();
		switch(prev[1])
		{
			case 's':
				param->svm_type = atoi(curr);
				break;
			case 't':
				param->kernel_type = atoi(curr);
				break;
			case 'd':
				param->degree = atoi(curr);
				break;
			case 'g':
				param->gamma = atof(curr);
				break;
			case 'r':
				param->coef0 = atof(curr);
				break;
			case 'n':
				param->nu = atof(curr);
				break;
			case 'm':
				param->cache_size = atof(curr);
				break;
			case 'c':
				param->C = atof(curr);
				break;
			case 'e':
				param->eps = atof(curr);
				break;
			case 'p':
				param->p = atof(curr);
				break;
			case 'h':
				param->shrinking = atoi(curr);
				break;
			case 'b':
				param->probability = atoi(curr);
				break;
			case 'w':
				++param->nr_weight;
				param->weight_label = (int *)realloc(param->weight_label,sizeof(int)*param->nr_weight);
				param->weight = (double *)realloc(param->weight,sizeof(double)*param->nr_weight);
				param->weight_label[param->nr_weight-1] = atoi(&prev[2]);
				param->weight[param->nr_weight-1] = atof(curr);
				break;
			default:
				fprintf(stderr,"Unknown option: -%c\n", prev[1]);
				exit_with_help();
		}
	}while((curr = strtok(NULL, " \t\n")) != NULL);
	

	svm_set_print_string_function(print_func);
}


struct svm_model* libsvm_train_for_toy(struct svm_problem* prob, const char* command)
{
	struct svm_parameter param;
	parse_command_line(command, &param);

	if(param.svm_type == EPSILON_SVR ||
			param.svm_type == NU_SVR)
	{
		
		for(int i = 0; i < prob->l; ++i)
		{
			prob->y[i] = prob->x[i][1].value;
			prob->x[i][1].index = -1;
		}

		if(param.gamma == 0)
			param.gamma = .1;
	}
	else
	{
		if(param.gamma == 0)
			param.gamma = .5;
	}

	struct svm_model* model = svm_train(prob, &param);

	svm_destroy_param(&param);
	free(prob->y);
	free(prob->x);
	free(prob);

	return model;
}

double libsvm_predict_for_toy(double f1, double f2, struct svm_model* model)
{
	static struct svm_node node[3];

	if(model->param.svm_type == EPSILON_SVR || model->param.svm_type == NU_SVR)
	{
		node[0].index = 1;
		node[0].value = f1;
		node[1].index = -1;
	}
	else
	{
		node[0].index = 1;
		node[0].value = f1;
		node[1].index = 2;
		node[1].value = f2;
		node[2].index = -1;
	}

	double result = svm_predict(model, node);
	
	return result;
}


struct svm_problem* create_svm_nodes(int size)
{
	struct svm_problem* prob = Malloc(struct svm_problem, 1);
	prob->l = size;
	prob->y = Malloc(double,prob->l);
	prob->x = Malloc(struct svm_node *, prob->l);
	struct svm_node* x_space = NULL;
	x_space = (struct svm_node*) realloc(x_space, sizeof(struct svm_node) * prob->l * 3);

	for(int i = 0; i < prob->l; ++i)
		prob->x[i] = x_space + i*3;

	return prob;
}


void add_instance(struct svm_problem* prob, int i, double y, double f1, double f2)
{
	prob->x[i][0].index = 1;
	prob->x[i][0].value = f1;
	prob->x[i][1].index = 2;
	prob->x[i][1].value = f2;
	prob->x[i][2].index = -1;
	prob->y[i] = y;
}


double get_svr_epsilon(struct svm_model* model)
{
	return model->param.p;
}

int main()
{
	exit(1);
}
