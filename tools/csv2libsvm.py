#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 13:39:26 2020

@author: robogor
"""
import argparse
import numpy as np
import pandas as pd

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
    data = pd.read_csv(args.csvpath)
    data = csv2libsvm(data)
    np.savetxt(args.outpath+'converted_data.txt', data.values, fmt='%s')
    print('\nConverted file saved to {}'.format(args.outpath)+'converted_data.txt')