#dependencies:
#	Intel tbb library: https://www.threadingbuildingblocks.org

#CXX ?= g++
CXX = icpc

ifeq ($(CXX),icpc)
	VECREPORT = -qopt-report5 -qopt-report-phase=vec -qopt-report-file=stdout
	VECREPORT = 
	CFLAGS = -Wall -Wconversion -O3 -std=c++11  -tbb -g $(VECREPORT) -xHost -debug inline-debug-info -I./
	LDFLAGS = -ltbbmalloc_proxy -lm -lrt
else
	#-fPIC
	CFLAGS = -Wall -Wconversion -O3 -std=c++11  -g -march=native -I./
	LDFLAGS = -ltbb -ltbbmalloc_proxy -lm -lrt
endif 

SHVER = 2
OS = $(shell uname)

all: svm-train svm-predict svm-scale chemo_test

lib: svm.o
	if [ "$(OS)" = "Darwin" ]; then \
		SHARED_LIB_FLAG="-dynamiclib -Wl,-install_name,libsvm.so.$(SHVER)"; \
	else \
		SHARED_LIB_FLAG="-shared -Wl,-soname,libsvm.so.$(SHVER)"; \
	fi; \
	$(CXX) $${SHARED_LIB_FLAG} svm.o -o libsvm.so.$(SHVER)

chemo_test: chemo/chemo_test.cpp chemo/chemo_test.h
	$(CXX) $(CFLAGS) chemo/chemo_test.cpp svm.o -o chemo_test $(LDFLAGS)
svm-predict: svm-predict.c svm.o
	$(CXX) $(CFLAGS) svm-predict.c svm.o -o svm-predict $(LDFLAGS)
svm-train: svm-train.c svm.o
	$(CXX) $(CFLAGS) svm-train.c svm.o -o svm-train $(LDFLAGS)
svm-scale: svm-scale.c
	$(CXX) $(CFLAGS) svm-scale.c -o svm-scale
svm.o: svm.cpp svm.h svm_o.h
	$(CXX) $(CFLAGS) -c svm.cpp
clean:
	rm -f *~ svm.o svm-train svm-predict svm-scale chemo_test libsvm.so.$(SHVER)
