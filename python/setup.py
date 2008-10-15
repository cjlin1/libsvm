#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name = "LIBSVM",
      version = "2.88",
      author="Chih-Chung Chang and Chih-Jen Lin",
      maintainer="Chih-Jen Lin",
      maintainer_email="cjlin@csie.ntu.edu.tw",
      url="http://www.csie.ntu.edu.tw/~cjlin/libsvm/",
      description = "LIBSVM Python Interface",
      ext_modules = [Extension("svmc",
                               ["../svm.cpp", "svmc_wrap.c"],
                               extra_compile_args=["-O3", "-I../"]
                               )
                     ],
      py_modules=["svm"],
      )
