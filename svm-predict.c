#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include "svm.h"

char* line;
int max_line_len = 1024;
struct svm_node *x;
int max_nr_attr = 64;

struct svm_model* model;

char* readline(FILE *input)
{
	int len;
	
	if(fgets(line,max_line_len,input) == NULL)
		return NULL;

	while(strrchr(line,'\n') == NULL)
	{
		max_line_len *= 2;
		line = (char *) realloc(line, max_line_len);
		len = strlen(line);
		if(fgets(line+len,max_line_len-len,input) == NULL)
			break;
	}
	return line;
}

void predict(FILE *input, FILE *output)
{
	int correct = 0;
	int total = 0;
	double error = 0;
	double sumv = 0, sumy = 0, sumvv = 0, sumyy = 0, sumvy = 0;
	
#define SKIP_TARGET\
	while(isspace(*p)) ++p;\
	while(!isspace(*p)) ++p;

#define SKIP_ELEMENT\
	while(*p!=':') ++p;\
	++p;\
	while(isspace(*p)) ++p;\
	while(*p && !isspace(*p)) ++p;

	while(readline(input)!=NULL)
	{
		int i = 0;
		double target,v;
		const char *p = line;

		if(sscanf(p,"%lf",&target)!=1) break;

		SKIP_TARGET

		while(sscanf(p,"%d:%lf",&x[i].index,&x[i].value)==2)
		{
			SKIP_ELEMENT;
			++i;
			if(i>=max_nr_attr-1)	// need one more for index = -1
			{
				max_nr_attr *= 2;
				x = (struct svm_node *) realloc(x,max_nr_attr*sizeof(struct svm_node));
			}
		}

		x[i].index = -1;
		v = svm_predict(model,x);
		if(v == target)
			++correct;
		error += (v-target)*(v-target);
		sumv += v;
		sumy += target;
		sumvv += v*v;
		sumyy += target*target;
		sumvy += v*target;
		++total;

		fprintf(output,"%g\n",v);
	}
	printf("Accuracy = %g%% (%d/%d) (classification)\n",
		(double)correct/total*100,correct,total);
	printf("Mean squared error = %g (regression)\n",error/total);
	printf("Squared correlation coefficient = %g (regression)\n",
		((total*sumvy-sumv*sumy)*(total*sumvy-sumv*sumy))/
		((total*sumvv-sumv*sumv)*(total*sumyy-sumy*sumy))
		);
}

int main(int argc, char **argv)
{
	FILE *input, *output;
	
	if(argc!=4)
	{
		fprintf(stderr,"usage: svm-predict test_file model_file output_file\n");
		exit(1);
	}

	input = fopen(argv[1],"r");
	if(input == NULL)
	{
		fprintf(stderr,"can't open input file %s\n",argv[1]);
		exit(1);
	}

	output = fopen(argv[3],"w");
	if(output == NULL)
	{
		fprintf(stderr,"can't open output file %s\n",argv[3]);
		exit(1);
	}

	if((model=svm_load_model(argv[2]))==0)
	{
		fprintf(stderr,"can't open model file %s\n",argv[2]);
		exit(1);
	}
	
	line = (char *) malloc(max_line_len*sizeof(char));
	x = (struct svm_node *) malloc(max_nr_attr*sizeof(struct svm_node));
	predict(input,output);
	svm_destroy_model(model);
	free(line);
	free(x);
	fclose(input);
	fclose(output);
	return 0;
}
