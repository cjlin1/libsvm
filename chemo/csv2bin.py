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

import array
import sys
import os
import shutil
import time
import datetime
import argparse
from chemo_db import BinDb, Compound


def main():
	parser = argparse.ArgumentParser(description='chemo db converter: csv to libsvm bin format.')
	parser.add_argument('csv',metavar='CSV',type=str,help='input csv file path')
	parser.add_argument('bin',metavar='BIN',type=str,help='bin output file path')
	parser.add_argument('-f',help='overwrite bin file',default=False, action='store_const', const=True)
	parser.add_argument('--progress',metavar='prg_time',type=int,help='show progress every <prg_time> seconds, \'0\' - disable progress output',default=2)
	args = parser.parse_args()

	print('start time:',time.strftime('%H:%M:%S %d/%m/%Y',time.localtime()))
	print('input text db:',args.csv)
	print('output bin db:',args.bin)

	if(not args.f and os.path.lexists(args.bin)):
		print('ERROR: File',args.bin,'exists; use \'-f\' parameter to overwrite file',file=sys.stderr)
		exit(1)

	with BinDb(args.bin,'w') as db, open(args.csv,'r') as cvs_file:
		start_time=time.time()
		total_compounds=0
		print_time=time.time()
		print_interval=args.progress # in seconds

		for line in cvs_file:
			c=Compound.from_jns_string(line)
			db.write(c)

			total_compounds+=1
			if(print_interval and time.time()-print_time>=print_interval):
				print(total_compounds,'compounds processed in',time.strftime("%H:%M:%S", time.gmtime(time.time()-start_time)),'...')
				print_time=time.time()

		print(total_compounds,'compounds processed in',time.strftime("%H:%M:%S", time.gmtime(time.time()-start_time)),'.')
		print('end time:',time.strftime('%H:%M:%S %d/%m/%Y',time.localtime()))

if __name__=='__main__':
	main()
