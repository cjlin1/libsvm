CXX ?= g++
CFLAGS = -Wall -Wconversion -O3 -fPIC
SHVER = 5
OS = $(shell uname)
ifeq ($(OS),Darwin)
	SHARED_LIB_FLAG = -dynamiclib -Wl,-install_name,libsvm.so.$(SHVER)
else
	SHARED_LIB_FLAG = -shared -Wl,-soname,libsvm.so.$(SHVER)
endif

# Uncomment the following lines to enable parallelization with OpenMP
# CFLAGS += -fopenmp
# SHARED_LIB_FLAG += -fopenmp

all: svm-train svm-predict svm-scale

lib: svm.o
	$(CXX) $(SHARED_LIB_FLAG) svm.o -o libsvm.so.$(SHVER)
svm-predict: svm-predict.c svm.o
	$(CXX) $(CFLAGS) svm-predict.c svm.o -o svm-predict -lm
svm-train: svm-train.c svm.o
	$(CXX) $(CFLAGS) svm-train.c svm.o -o svm-train -lm
svm-scale: svm-scale.c
	$(CXX) $(CFLAGS) svm-scale.c -o svm-scale
svm.o: svm.cpp svm.h
	$(CXX) $(CFLAGS) -c svm.cpp
clean:
	rm -f *~ svm.o svm-train svm-predict svm-scale libsvm.so.$(SHVER)
