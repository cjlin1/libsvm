CXX ?= g++
CFLAGS = -Wall -Wconversion -O3 -fPIC
SHVER = 2
OS := $(shell uname)

all: svm-train svm-predict svm-scale lib

ifeq ($(OS),Darwin)
  DLLEXT := dylib
  SHARED_LIB_FLAG = -dynamiclib
else
  DLLEXT := so
  SHARED_LIB_FLAG = -shared
endif

libsvm.$(DLLEXT): svm.o
	$(CXX) $(SHARED_LIB_FLAG) $^ -o $@

libsvm.$(DLLEXT).$(SHVER): libsvm.$(DLLEXT)
	ln $< $@

libsvm.a: svm.o
	ar rc $@ $^ 
	ranlib $@ 

.PHONY: lib
lib: libsvm.$(DLLEXT).$(SHVER) libsvm.a

svm-predict: svm-predict.c svm.o
	$(CXX) $(CFLAGS) $^ -o $@ -lm
svm-train: svm-train.c svm.o
	$(CXX) $(CFLAGS) $^ -o $@ -lm
svm-scale: svm-scale.c
	$(CXX) $(CFLAGS) $^ -o svm-scale
svm.o: svm.cpp svm.h
	$(CXX) $(CFLAGS) -c $<
clean:
	rm -f *~ svm.o svm-train svm-predict svm-scale libsvm.$(DLLEXT).$(SHVER) libsvm.a
