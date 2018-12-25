# This Makefile is used under Linux

MATLABDIR ?= /usr/local/matlab
# for Mac
# MATLABDIR ?= /opt/local/matlab

CXX ?= g++
#CXX = g++-4.1
CFLAGS = -Wall -Wconversion -O3 -fPIC -I$(MATLABDIR)/extern/include -I..

MEX = $(MATLABDIR)/bin/mex
MEX_OPTION = CC="$(CXX)" CXX="$(CXX)" CFLAGS="$(CFLAGS)" CXXFLAGS="$(CFLAGS)"
# comment the following line if you use MATLAB on 32-bit computer
MEX_OPTION += -largeArrayDims
MEX_EXT = $(shell $(MATLABDIR)/bin/mexext)

all:	matlab

matlab:	binary

octave:
	@echo "please type make under Octave"

binary: svmpredict.$(MEX_EXT) svmtrain.$(MEX_EXT) libsvmread.$(MEX_EXT) libsvmwrite.$(MEX_EXT)

svmpredict.$(MEX_EXT):     svmpredict.c ../svm.h ../svm.cpp svm_model_matlab.c
	$(MEX) $(MEX_OPTION) svmpredict.c ../svm.cpp svm_model_matlab.c

svmtrain.$(MEX_EXT):       svmtrain.c ../svm.h ../svm.cpp svm_model_matlab.c
	$(MEX) $(MEX_OPTION) svmtrain.c ../svm.cpp svm_model_matlab.c

libsvmread.$(MEX_EXT):	libsvmread.c
	$(MEX) $(MEX_OPTION) libsvmread.c

libsvmwrite.$(MEX_EXT):	libsvmwrite.c
	$(MEX) $(MEX_OPTION) libsvmwrite.c

clean:
	rm -f *~ *.o *.mex* *.obj
