CXX? = g++
CFLAGS = -Wall -O3 -DQT_THREAD_SUPPORT
BIN = $(QTDIR)/bin
INCLUDE = $(QTDIR)/include
LIB = $(QTDIR)/lib
#BIN = /usr/bin
#INCLUDE = /usr/include/qt3
#LIB = /usr/lib/qt3

svm-toy: svm-toy.cpp svm-toy.moc ../../svm.o
	$(CXX) -I$(INCLUDE) $(CFLAGS) svm-toy.cpp ../../svm.o -o svm-toy -L$(LIB) -lqt-mt 
# add -pthread for bsd

svm-toy.moc: svm-toy.cpp
	$(BIN)/moc svm-toy.cpp -o svm-toy.moc
../../svm.o:
	cd ../..; make svm.o
clean:
	rm -f *~ svm-toy svm-toy.moc ../../svm.o
