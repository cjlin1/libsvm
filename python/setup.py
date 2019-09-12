# coding=utf-8
"""Setup file for distutils / pypi."""
try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass

from setuptools import setup


setup(
    name='libsvm',
    version='3.23',
    author='Chih-Chung Chang and Chih-Jen Lin',
    py_modules=['svm', 'svmutil', 'commonutil'],
    url='https://www.csie.ntu.edu.tw/~cjlin/libsvm/',
    description=('Python binding for libsvm ('
                 'https://www.csie.ntu.edu.tw/~cjlin/libsvm/).'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

    ]
)
