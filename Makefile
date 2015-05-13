CXX ?= g++
CFLAGS = -Wall -Wconversion -O3 -fPIC
SHVER = 2
OS := $(shell uname)

all: svm-train svm-predict svm-scale

ifeq ($(OS),Darwin)
  LIBEXT := dylib
  SHARED_LIB_FLAG = -dynamiclib
else
  LIBEXT := so
  SHARED_LIB_FLAG = -shared
endif

libsvm.$(LIBEXT): svm.o
	$(CXX) $(SHARED_LIB_FLAG) $^ -o $@

libsvm.$(LIBEXT).$(SHVER): libsvm.$(LIBEXT)
	ln $< $@ 

.PHONY: lib
lib: libsvm.$(LIBEXT).$(SHVER)

svm-predict: svm-predict.c svm.o
	$(CXX) $(CFLAGS) $^ -o $@ -lm
svm-train: svm-train.c svm.o
	$(CXX) $(CFLAGS) $^ -o $@ -lm
svm-scale: svm-scale.c
	$(CXX) $(CFLAGS) $^ -o svm-scale
svm.o: svm.cpp svm.h
	$(CXX) $(CFLAGS) -c $<
clean:
	rm -f *~ svm.o svm-train svm-predict svm-scale libsvm.$(LIBEXT).$(SHVER)
