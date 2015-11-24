'''
Copyright(C) 2015 Intel Corporation and Jaak Simm KU Leuven
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import struct
import numpy
import chemo_db
import sys
import os
import shutil
import time
import datetime
import argparse

def main():
	parser = argparse.ArgumentParser(description='chemo db converter: dense to libsvm bin format.')
	parser.add_argument('ids',metavar='IDs',type=str,help='input ids text file path')
	parser.add_argument('dense',metavar='DENSE',type=str,help='input dense bin file path')
	parser.add_argument('bin',metavar='BIN',type=str,help='output bin file path')
	parser.add_argument('-f',help='overwrite bin file',default=False, action='store_const', const=True)
	parser.add_argument('--progress',metavar='prg_time',type=int,help='show progress every <prg_time> seconds, \'0\' - disable progress output',default=2)
	args = parser.parse_args()

	dense_bin_path=args.dense
	ids_txt_path=args.ids
	db_out_path=args.bin

	start_time=time.time()
	print_time=time.time()
	print_interval=args.progress # in seconds

	print('start time:',time.strftime('%H:%M:%S %d/%m/%Y',time.localtime()))
	print('input dense bin:',dense_bin_path)
	print('input ids txt:',ids_txt_path)
	print('output bin db:',db_out_path)

	if(not args.f and os.path.lexists(db_out_path)):
		print('ERROR: File',db_out_path,'exists; use \'-f\' parameter to overwrite file',file=sys.stderr)
		exit(1)

	print('reading \"'+ids_txt_path+'\" file...')
	ids=[]
	with open(ids_txt_path,'r') as ids_file:
		for id in ids_file:
			id=id.strip()
			ids.append(id)
	print('ids count:',len(ids))

	with open(dense_bin_path,'rb') as in_file, chemo_db.BinDb(db_out_path,'w') as db:
		nrows = numpy.fromfile(in_file, dtype='int64', count=1)[0]
		ncols = numpy.fromfile(in_file, dtype='int64', count=1)[0]
		print(nrows,ncols)
		values = numpy.fromfile(in_file, dtype=numpy.float32, count=nrows*ncols)
		print(values.shape)
		values = values.reshape((ncols, nrows), order='C')
		print(len(values), len(values[0]), values.shape, values.shape[0], values.shape[1])

		total_compounds=0
		features = [i for i in range(values.shape[1])]
		for i in range(values.shape[0]):
			id_str=ids[i]
			compound=chemo_db.Compound(id_str,features,list(values[i]))
			db.write(compound)
			total_compounds+=1
			
			if(print_interval and time.time()-print_time>=print_interval):
				print("{0} ( {1:.2%} ) compounds processed in {2}...".format(total_compounds, i/int(values.shape[0]), time.strftime("%H:%M:%S", time.gmtime(time.time()-start_time))))
				print_time=time.time()

		print(total_compounds,'compounds processed in',time.strftime("%H:%M:%S", time.gmtime(time.time()-start_time)),'.')
		print('end time:',time.strftime('%H:%M:%S %d/%m/%Y',time.localtime()))

if __name__=='__main__':
	main()