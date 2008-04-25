CXX? = g++
CFLAGS = -Wall -O3 -DQT_THREAD_SUPPORT

BIN = /usr/bin

FLAGS:=$(CFLAGS)  -DQT3_SUPPORT -DQT_INCLUDE_COMPAT `pkg-config --cflags --libs Qt3Support QtGui`

svm-toy: svm-toy.cpp svm-toy.moc ../../svm.o
	$(CXX) $(FLAGS) svm-toy.cpp ../../svm.o -o svm-toy

svm-toy.moc: svm-toy.cpp
	$(BIN)/moc svm-toy.cpp -o svm-toy.moc

../../svm.o:
	cd ../..; make svm.o

clean:
	rm -f *~ svm-toy svm-toy.moc ../../svm.o

