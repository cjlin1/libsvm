/*
	scale attributes to [lower,upper]
	usage: scale [-l lower] [-u upper] [-y y_lower y_upper] 
		     [-s filename] [-r filename] filename
*/
#include <float.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

char *line;
int max_line_len = 1024;
double lower=-1.0,upper=1.0,y_lower,y_upper;
int y_scaling = 0;
double *feature_max;
double *feature_min;
double y_max = -DBL_MAX;
double y_min = DBL_MAX;
int max_index;

#define max(x,y) ((x>y)?x:y)
#define min(x,y) ((x<y)?x:y)

void output_target(double value);
void output(int index, double value);
char* readline(FILE *input);

int main(int argc,char **argv)
{
	int i,index;
	FILE *fp;
	char *save_filename = NULL;
	char *restore_filename = NULL;

	for(i=1;i<argc;i++)
	{
		if(argv[i][0] != '-') break;
		++i;
		switch(argv[i-1][1])
		{
			case 'l': lower = atof(argv[i]); break;
			case 'u': upper = atof(argv[i]); break;
			case 'y':
				y_lower = atof(argv[i]);
				++i;
				y_upper = atof(argv[i]);
				y_scaling = 1;
				break;
			case 's': save_filename = argv[i]; break;
			case 'r': restore_filename = argv[i]; break;
			default:
				fprintf(stderr,"unknown option\n");
				exit(1);
		}
	}

	if(!(upper > lower) || (y_scaling && !(y_upper > y_lower)))
	{
		fprintf(stderr,"inconsistent lower/upper specification\n");
		exit(1);
	}
	
	if(argc != i+1) 
	{
		fprintf(stderr,"usage: %s [-l lower] [-u upper] [-y y_lower y_upper]\n",argv[0]);
		fprintf(stderr,"      [-s save_filename] [-r restore_filename] filename\n");
		fprintf(stderr,"(default: lower = -1, upper = 1, no y scaling)\n");
		exit(1);
	}

	fp=fopen(argv[i],"r");
	
	if(fp==NULL)
	{
		fprintf(stderr,"can't open file %s\n", argv[i]);
		exit(1);
	}

	line = (char *) malloc(max_line_len*sizeof(char));

#define SKIP_TARGET\
	while(isspace(*p)) ++p;\
	while(!isspace(*p)) ++p;

#define SKIP_ELEMENT\
	while(*p!=':') ++p;\
	++p;\
	while(isspace(*p)) ++p;\
	while(*p && !isspace(*p)) ++p;
	
	/* assumption: min index of attributes is 1 */
	/* pass 1: find out max index of attributes */
	max_index = 0;
	while(readline(fp)!=NULL)
	{
		char *p=line;

		SKIP_TARGET

		while(sscanf(p,"%d:%*f",&index)==1)
		{
			max_index = max(max_index, index);
			SKIP_ELEMENT
		}		
	}
	
	feature_max = (double *)malloc((max_index+1)* sizeof(double));
	feature_min = (double *)malloc((max_index+1)* sizeof(double));
	
	if(feature_max == NULL || feature_min == NULL)
	{
		fprintf(stderr,"can't allocate enough memory\n");
		exit(1);
	}

	for(i=0;i<=max_index;i++)
	{
		feature_max[i]=-DBL_MAX;
		feature_min[i]=DBL_MAX;
	}

	rewind(fp);

	/* pass 2: find out min/max value */
	while(readline(fp)!=NULL)
	{
		char *p=line;
		int next_index=1;
		double target;
		double value;

		sscanf(p,"%lf",&target);
		y_max = max(y_max,target);
		y_min = min(y_min,target);
		
		SKIP_TARGET

		while(sscanf(p,"%d:%lf",&index,&value)==2)
		{
			for(i=next_index;i<index;i++)
			{
				feature_max[i]=max(feature_max[i],0);
				feature_min[i]=min(feature_min[i],0);
			}
			
			feature_max[index]=max(feature_max[index],value);
			feature_min[index]=min(feature_min[index],value);

			SKIP_ELEMENT
			next_index=index+1;
		}		

		for(i=next_index;i<=max_index;i++)
		{
			feature_max[i]=max(feature_max[i],0);
			feature_min[i]=min(feature_min[i],0);
		}	
	}

	rewind(fp);

	/* pass 2.5: save/restore feature_min/feature_max */
	
	if(restore_filename)
	{
		FILE *fp = fopen(restore_filename,"r");
		int idx;
		double fmin, fmax;
		
		if(fp==NULL)
		{
			fprintf(stderr,"can't open file %s\n", restore_filename);
			exit(1);
		}
		fscanf(fp, "%lf %lf\n", &lower, &upper);
		while(fscanf(fp,"%d %lf %lf\n",&idx,&fmin,&fmax)==3)
		{
			if(idx<=max_index)
			{
				feature_min[idx] = fmin;
				feature_max[idx] = fmax;
			}
		}
		fclose(fp);
	}
	
	if(save_filename)
	{
		FILE *fp = fopen(save_filename,"w");
		if(fp==NULL)
		{
			fprintf(stderr,"can't open file %s\n", save_filename);
			exit(1);
		}
		fprintf(fp, "%g %g\n", lower, upper);
		for(i=1;i<=max_index;i++)
		{
			if(feature_min[i]!=feature_max[i])
				fprintf(fp,"%d %g %g\n",i,feature_min[i],feature_max[i]);
		}
		fclose(fp);
	}
	
	/* pass 3: scale */
	while(readline(fp)!=NULL)
	{
		char *p=line;
		int next_index=1;
		int index;
		double target;
		double value;
		
		sscanf(p,"%lf",&target);
		output_target(target);

		SKIP_TARGET

		while(sscanf(p,"%d:%lf",&index,&value)==2)
		{
			for(i=next_index;i<index;i++)
				output(i,0);
			
			output(index,value);

			SKIP_ELEMENT
			next_index=index+1;
		}		

		for(i=next_index;i<=max_index;i++)
			output(i,0);

		printf("\n");
	}

	free(line);
	fclose(fp);
	return 0;
}

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

void output_target(double value)
{
	if(y_scaling)
	{
		if(value == y_min)
			value = y_lower;
		else if(value == y_max)
			value = y_upper;
		else value = y_lower + (y_upper-y_lower) *
			     (value - y_min)/(y_max-y_min);
	}
	printf("%g ",value);
}

void output(int index, double value)
{
	/* skip single-valued attribute */
	if(feature_max[index] == feature_min[index])
		return;

	if(value == feature_min[index])
		value = lower;
	else if(value == feature_max[index])
		value = upper;
	else
		value = lower + (upper-lower) * 
			(value-feature_min[index])/
			(feature_max[index]-feature_min[index]);

	if(value != 0)
		printf("%d:%g ",index, value);
}
