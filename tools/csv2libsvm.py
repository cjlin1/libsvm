#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: dasmehdix
Required library versions are:

Numpy = 1.19.0
Pandas = 1.0.5
"""
import argparse
import numpy as np
import pandas as pd
"""
In this code, we write  a basic script to convert a csv file to libsvm format. This example done for this type of csv file:

classs	accelX	accelY	accelZ	gyroX	gyroY	gyroZ
1	-0.329013	1.111466	9.943973	0.064446	-0.0759	-0.095295
1	-0.329013	1.111466	9.943973	0.064446	-0.0759	-0.095295

which 'class'(label) column of the dataframe is the first column.

Converted format is like:
1 1:-0.329013 2:1.111466 3:9.943973 4:0.064446 5:-0.0759 6:-0.095295
1 1:-0.329013 2:1.111466 3:9.943973 4:0.064446 5:-0.0759 6:-0.095295

which makes enable to use libsvm.

Also, example data uploaded to test script 

Usage is like:

python3 csv2libsvm.py -c path_of_input_csv -o path_of_output_folder

For my enviroment I used like:

python3 csv2libsvm.py -c /home/robogor/Desktop/workshop/muhur/data.csv -o /home/robogor/Desktop/
to save file on desktop.

You can change some input arguments to handle your csv data.
"""
def csv2libsvm(full_data):
    for i in range(0,full_data.shape[0]):
        for j in range(1,full_data.shape[1]):
            full_data.iloc[i,j] = '{}'.format(j)+':'+str(full_data.iloc[i,j])
    return full_data

parser = argparse.ArgumentParser(description='A script to convert a csv file to libsvm format')
parser.add_argument('-c','--csvpath',type=str,required=True, help = 'Path of csv file')
parser.add_argument('-o','--outpath',type=str,required=True, help = 'Path to save converted file')
args = parser.parse_args()

if __name__ == '__main__':
    # data reading line, if your csv data do not include headers, please add header=None as input argument)
    data = pd.read_csv(args.csvpath)
    # converter line
    data = csv2libsvm(data)
    # data save line, be sure that your path= {/path_to_file/} ends with '/'
    np.savetxt(args.outpath+'converted_data.txt', data.values, fmt='%s')
    print('\nConverted file saved to {}'.format(args.outpath)+'converted_data.txt')
