CXXC = g++
CFLAGS = -Wall -O3 -g
BIN = $(QTDIR)/bin
INCLUDE = $(QTDIR)/include
LIB = $(QTDIR)/lib
#BIN = /usr/bin
#INCLUDE = /usr/include/qt
#LIB = /usr/lib/qt

svm-toy: svm-toy.cpp svm-toy.moc ../../svm.o
	$(CXXC) -I$(INCLUDE) $(CFLAGS) svm-toy.cpp ../../svm.o -o svm-toy -L$(LIB) -lqt
svm-toy.moc: svm-toy.cpp
	$(BIN)/moc svm-toy.cpp -o svm-toy.moc
../../svm.o:
	cd ../..; make svm.o
clean:
	rm -f *~ svm-toy svm-toy.moc
