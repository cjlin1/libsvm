CC = g++
SWIG ?= swig
PYTHON_INCLUDEDIR ?= /usr/include/python2.2
CFLAGS = -O2 -I$(PYTHON_INCLUDEDIR) -I..
LDFLAGS = -shared

all: svmc.so

svmc.so: svmc_wrap.o ../svm.o
	$(CC) $(LDFLAGS) -o svmc.so svmc_wrap.o ../svm.o

svmc_wrap.o: svmc_wrap.c ../svm.h
	$(CC) $(CFLAGS) -c svmc_wrap.c

svmc_wrap.c: svmc.i
	$(SWIG) -python svmc.i

../svm.o:	
	cd ..; make svm.o

clean:
	rm -f *~ *.o *.so *.pyc *.pyo svmc_wrap.doc

moreclean:	clean
	rm -f svmc_wrap.c
