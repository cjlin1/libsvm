#!/usr/bin/env python

import sys, os
from os import path
from shutil import copyfile, rmtree
from glob import glob

from setuptools import setup, Extension
from distutils.command.clean import clean as clean_cmd

# a technique to build a shared library on windows
from distutils.command.build_ext import build_ext

build_ext.get_export_symbols = lambda x, y: []


PACKAGE_DIR = "libsvm"
PACKAGE_NAME = "libsvm-official"
VERSION = "3.30.0"
cpp_dir = "cpp-source"
# should be consistent with dynamic_lib_name in libsvm/svm.py
dynamic_lib_name = "clib"

# sources to be included to build the shared library
source_codes = [
    "svm.cpp",
]
headers = [
    "svm.h",
    "svm.def",
]

kwargs_for_extension = {
    "sources": [path.join(cpp_dir, f) for f in source_codes],
    "depends": [path.join(cpp_dir, f) for f in headers],
    "include_dirs": [cpp_dir],
    "language": "c++",
}

# see ../Makefile.win
if sys.platform == "win32":
    kwargs_for_extension.update(
        {
            "define_macros": [("_WIN64", ""), ("_CRT_SECURE_NO_DEPRECATE", "")],
            "extra_link_args": ["-DEF:{}\svm.def".format(cpp_dir)],
        }
    )


def create_cpp_source():
    for f in source_codes + headers:
        src_file = path.join("..", f)
        tgt_file = path.join(cpp_dir, f)
        # ensure blas directory is created
        os.makedirs(path.dirname(tgt_file), exist_ok=True)
        copyfile(src_file, tgt_file)


class CleanCommand(clean_cmd):
    def run(self):
        clean_cmd.run(self)
        to_be_removed = ["build/", "dist/", "MANIFEST", cpp_dir, "{}.egg-info".format(PACKAGE_NAME)]
        to_be_removed += glob("./{}/{}.*".format(PACKAGE_DIR, dynamic_lib_name))
        for root, dirs, files in os.walk(os.curdir, topdown=False):
            if "__pycache__" in dirs:
                to_be_removed.append(path.join(root, "__pycache__"))
            to_be_removed += [f for f in files if f.endswith(".pyc")]

        for f in to_be_removed:
            print("remove {}".format(f))
            if f == ".":
                continue
            elif path.isfile(f):
                os.remove(f)
            elif path.isdir(f):
                rmtree(f)

def main():
    if not path.exists(cpp_dir):
        create_cpp_source()

    with open("README") as f:
        long_description = f.read()

    setup(
        name=PACKAGE_NAME,
        packages=[PACKAGE_DIR],
        version=VERSION,
        description="Python binding of LIBSVM",
        long_description=long_description,
        long_description_content_type="text/plain",
        author="ML group @ National Taiwan University",
        author_email="cjlin@csie.ntu.edu.tw",
        url="https://www.csie.ntu.edu.tw/~cjlin/libsvm",
        install_requires=["scipy"],
        ext_modules=[
            Extension(
                "{}.{}".format(PACKAGE_DIR, dynamic_lib_name), **kwargs_for_extension
            )
        ],
        cmdclass={"clean": CleanCommand},
    )


main()

