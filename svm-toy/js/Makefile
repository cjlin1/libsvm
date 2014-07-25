CC = ./emscripten/em++
CXX = ./emscripten/emcc

CFLAGS = -Wall -Wconversion -O3 -fPIC

all: libsvm-js-interfaces.js

svm.o: svm.cpp svm.h
	$(CXX) $(CFLAGS) -c svm.cpp

libsvm-js-interfaces.js: js-interfaces.c svm.o svm.h
	$(CC) $(CFLAGS) js-interfaces.c svm.o -o libsvm-js-interfaces.js -s EXPORTED_FUNCTIONS="['_parse_command_line', '_create_svm_nodes', '_add_instance', '_libsvm_train_for_toy', '_libsvm_predict_for_toy', '_get_svr_epsilon', '_svm_free_model_content', '_svm_get_svm_type']" 

clean:
	rm -f *~ js-interfaces.o svm.o libsvm-js-interfaces.js
