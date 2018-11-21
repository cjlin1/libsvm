# use  ``export QT_SELECT=qt5'' in a command window for using qt5
# may need to adjust the path of header files
CXX? = g++
INCLUDE = /usr/include/x86_64-linux-gnu/qt5
CFLAGS = -Wall -O3 -I$(INCLUDE) -I$(INCLUDE)/QtWidgets -I$(INCLUDE)/QtGui -I$(INCLUDE)/QtCore -fPIC -std=c++11
LIB = -lQt5Widgets -lQt5Gui -lQt5Core
MOC = /usr/bin/moc

svm-toy: svm-toy.cpp svm-toy.moc ../../svm.o
	$(CXX) $(CFLAGS) svm-toy.cpp ../../svm.o -o svm-toy $(LIB)

svm-toy.moc: svm-toy.cpp
	$(MOC) svm-toy.cpp -o svm-toy.moc

../../svm.o: ../../svm.cpp ../../svm.h
	make -C ../.. svm.o

clean:
	rm -f *~ svm-toy svm-toy.moc ../../svm.o
