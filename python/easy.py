#!/usr/bin/python

import sys
import os

if len(sys.argv) <= 1:
	print 'Usage: %s training_file [testing_file]' % sys.argv[0]
	raise SystemExit

train_pathname = sys.argv[1]
file_name = os.path.split(train_pathname)[1]
scaled_file = file_name + ".scale"
model_file = file_name + ".model"
range_file = file_name + ".range"

if len(sys.argv) > 2:
	test_pathname = sys.argv[2]
	file_name = os.path.split(test_pathname)[1]
	scaled_test_file = file_name + ".scale"
	predict_test_file = file_name + ".predict"

cmd = "../svm-scale -s %s %s > %s" % (range_file, train_pathname, scaled_file)
print 'Scaling training data...'
os.system(cmd)

cmd = "./grid.py %s" % (scaled_file)
print 'Cross validation...'
dummy, f, dummy = os.popen3(cmd)

line = ''
while 1:
	last_line = line
	line = f.readline()
	if not line: break
c,g,rate = map(float,last_line.split())
print 'Best c=%s, g=%s' % (c,g)

cmd = "../svm-train -c %s -g %s %s %s" % (c,g,scaled_file,model_file)
print 'Training...'
os.popen(cmd)

print 'Output model: %s' % model_file
if len(sys.argv) > 2:
	cmd = "../svm-scale -r %s %s > %s" % (range_file, test_pathname, scaled_test_file)
	print 'Scaling testing data...'
	os.system(cmd)

	cmd = "../svm-predict %s %s %s" % (scaled_test_file, model_file, predict_test_file)
	print 'Testing...'
	os.system(cmd)

	print 'Output prediction: %s' % predict_test_file
