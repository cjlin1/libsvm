FILES =	libsvm/svm.class libsvm/svm_model.class libsvm/svm_node.class \
	libsvm/svm_parameter.class libsvm/svm_problem.class \
	svm_train.class svm_predict.class svm_toy.class

#JAVAC = jikes
#JAVAC_FLAGS = -classpath /opt/IBMJava2-13/jre/lib/rt.jar
JAVAC = javac
JAVAC_FLAGS =

all: $(FILES)
	jar cvf libsvm.jar *.class libsvm/*.class
	
%.class: %.java
	$(JAVAC) $(JAVAC_FLAGS) $<

libsvm/svm.java: libsvm/svm.m4
	m4 libsvm/svm.m4 > libsvm/svm.java

clean:
	rm -f libsvm/*.class *.class *.jar libsvm/*~ *~ libsvm/svm.java

dist: clean all
	rm *.class libsvm/*.class
