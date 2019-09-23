#!/bin/bash
set -e
BASEDIR=$(dirname $0)
PYTHON_DIRS="$BASEDIR/../fwd_api"
PYTHON_DIRS="$PYTHON_DIRS $BASEDIR/../test"

ORIG_DIR=`pwd`
for dir in $PYTHON_DIRS; do
    cd $dir
    pep8 .
    cd $ORIG_DIR
done
