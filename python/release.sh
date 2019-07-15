#!/bin/bash

python setup.py sdist

if [ $1 == "test" ];
 then
    echo TEST RELEASE;
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
else
    echo PROD RELEASE;
    twine upload dist/*.tar.gz
fi
