CXX? = g++
SWIG ?= swig

#Windows: see ../README ../Makefile.win
PYTHON_INCLUDEDIR ?= /usr/include/python2.4

CFLAGS = -O3 -I$(PYTHON_INCLUDEDIR) -I..
LDFLAGS = -shared
# Mac OS
# LDFLAGS = -framework Python -bundle

all: svmc.so

svmc.so: svmc_wrap.o svm.o
	$(CXX) $(LDFLAGS) -o svmc.so svmc_wrap.o svm.o

svmc_wrap.o: svmc_wrap.c ../svm.h
	$(CXX) $(CFLAGS) -fPIC -c svmc_wrap.c

svmc_wrap.c: svmc.i
	$(SWIG) -python -noproxy svmc.i

svm.o: ../svm.cpp ../svm.h
	$(CXX) $(CFLAGS) -fPIC -c ../svm.cpp

clean:
	rm -f *~ *.o *.so *.pyc *.pyo svm.o

moreclean:	clean
	rm -f svmc_wrap.c
