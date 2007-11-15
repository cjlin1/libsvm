#!/usr/bin/env python

#
# A format checker for LIBSVM
#

#
# Copyright (c) 2007, Rong-En Fan
#
# All rights reserved.
#
# This program is distributed under the same license of the LIBSVM package.
# 

from sys import argv, exit
import os.path

def err(line_no, msg):
	print "line %d: %s" % (line_no, msg)

# works like float() but does not accept nan and inf
def my_float(x):
	if x.lower().find("nan") != -1 or x.lower().find("inf") != -1:
		raise ValueError

	return float(x)

def main():
	if len(argv) != 2:
		print "Usage: %s dataset" % (argv[0])
		exit(1)

	dataset = argv[1]

	if not os.path.exists(dataset):
		print "dataset %s not found" % (dataset)
		exit(1)

	line_no = 1
	error_line_count = 0
	for line in open(dataset, 'r'):
		line_error = False

		# each line must end with a newline character
		if line[-1] != '\n':
			err(line_no, "missing a newline character in the end")
			line_error = True

		nodes = line.split()

		# check label
		try:
			label = nodes.pop(0)
			
			if label.find(',') != -1:
				# multi-label format
				try:
					for l in label.split(','):
						label = my_float(label)
				except:
					err(line_no, "label %s is not a valid multi-label form" % label)
					line_error = True
			else:
				try:
					label = my_float(label)
				except:
					err(line_no, "label %s is not a number" % label)
					line_error = True
		except:
			err(line_no, "missing label, perhaps an empty line?")
			line_error = True

		# check features
		prev_index = -1
		for i in range(len(nodes)):
			try:
				(index, value) =  nodes[i].split(':')

				index = int(index)
				value = my_float(value)

				# precomputed kernel's index starts from 0 and LIBSVM
				# checks it. Hence, don't treat index 0 as an error.
				if index < 0:
					err(line_no, "feature index must be positive; wrong feature %s" % nodes[i])
					line_error = True
				elif index < prev_index:
					err(line_no, "feature indices must be in an ascending order, previous/current features %s %s" % (nodes[i-1], nodes[i]))
					line_error = True
				prev_index = index
			except:
				err(line_no, "feature '%s' not an <index>:<value> pair, <index> integer, <value> real number " % nodes[i])
				line_error = True

		line_no += 1

		if line_error:
			error_line_count += 1
	
	if error_line_count > 0:
		print "Found %d lines with error." % (error_line_count)
	else:
		print "No error."

main()

