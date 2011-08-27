% This make.m is for MATLAB and OCTAVE under Windows, Mac, and Unix

Type = ver;
% This part is for OCTAVE
if(strcmp(Type(1).Name, 'Octave') == 1)
    mex libsvmread.c
    mex libsvmwrite.c
    mex svmtrain.c ../svm.cpp svm_model_matlab.c
    mex svmpredict.c ../svm.cpp svm_model_matlab.c
% This part is for MATLAB
% Add -largeArrayDims on 64-bit machines of MATLAB
else
    mex -O CFLAGS="\$CFLAGS -std=c99" -largeArrayDims libsvmread.c
    mex -O CFLAGS="\$CFLAGS -std=c99" -largeArrayDims libsvmwrite.c
    mex -O CFLAGS="\$CFLAGS -std=c99" -largeArrayDims svmtrain.c ../svm.cpp svm_model_matlab.c
    mex -O CFLAGS="\$CFLAGS -std=c99" -largeArrayDims svmpredict.c ../svm.cpp svm_model_matlab.c
end

