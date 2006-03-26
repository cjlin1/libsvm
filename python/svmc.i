%module svmc
%{
#include "svm.h"
%}

enum { C_SVC, NU_SVC, ONE_CLASS, EPSILON_SVR, NU_SVR };	/* svm_type */
enum { LINEAR, POLY, RBF, SIGMOID, PRECOMPUTED };	/* kernel_type */

%pragma make_default

struct svm_parameter
{
	int svm_type;
	int kernel_type;
	int degree;	// for poly
	double gamma;	// for poly/rbf/sigmoid
	double coef0;	// for poly/sigmoid

	// these are for training only
	double cache_size; // in MB
	double eps;	// stopping criteria
	double C;	// for C_SVC, EPSILON_SVR and NU_SVR
	int nr_weight;		// for C_SVC
	int *weight_label;	// for C_SVC
	double* weight;		// for C_SVC
	double nu;	// for NU_SVC, ONE_CLASS, and NU_SVR
	double p;	// for EPSILON_SVR
	int shrinking;	// use the shrinking heuristics
	int probability;
};

struct svm_problem
{
	int l;
	double *y;
	struct svm_node **x;
};

%pragma no_default

struct svm_model *svm_train(const struct svm_problem *prob, const struct svm_parameter *param);

void svm_cross_validation(const struct svm_problem *prob, const struct svm_parameter *param, int nr_fold, double *target);

int svm_save_model(const char *model_file_name, const struct svm_model *model);
struct svm_model *svm_load_model(const char *model_file_name);

int svm_get_svm_type(const struct svm_model *model);
int svm_get_nr_class(const struct svm_model *model);
void svm_get_labels(const struct svm_model *model, int *label);
double svm_get_svr_probability(const struct svm_model *model);

void svm_predict_values(const struct svm_model *model, const struct svm_node *x, double* decvalue);
double svm_predict(const struct svm_model *model, const struct svm_node *x);
double svm_predict_probability(const struct svm_model *model, const struct svm_node *x, double* prob_estimates);

void svm_destroy_model(struct svm_model *model);
/* Not necessary: the weight vector is (de)allocated at python-part
   void svm_destroy_param(struct svm_parameter *param); */

const char *svm_check_parameter(const struct svm_problem *prob, const struct svm_parameter *param);
int svm_check_probability_model(const struct svm_model *model);

%include carrays.i		
%array_functions(int,int)
%array_functions(double,double)


%inline %{
struct svm_node *svm_node_array(int size)
{
	return (struct svm_node *)malloc(sizeof(struct svm_node)*size);
}

void svm_node_array_set(struct svm_node *array, int i, int index, double value)
{
	array[i].index = index;
	array[i].value = value;
}

void svm_node_array_destroy(struct svm_node *array)
{
	free(array);
}

struct svm_node **svm_node_matrix(int size)
{
	return (struct svm_node **)malloc(sizeof(struct svm_node *)*size);	
}

void svm_node_matrix_set(struct svm_node **matrix, int i, struct svm_node* array)
{
	matrix[i] = array;
}

void svm_node_matrix_destroy(struct svm_node **matrix)
{
	free(matrix);
}

%}
