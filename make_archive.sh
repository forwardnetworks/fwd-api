#!/bin/bash
# Script depends on the git-archive-all Python script being installed.
# Get it from:
# https://github.com/Kentzo/git-archive-all
VERSION=`python setup.py --version`
TEMPDIR='export_temp'
./git_archive_all.py --prefix 'fwd-api/' fwd-api-${VERSION}.tar
mkdir -p $TEMPDIR
tar -C $TEMPDIR -xf fwd-api-${VERSION}.tar
cd $TEMPDIR
zip -r fwd-api-${VERSION}.zip .
cd ..
mv ${TEMPDIR}/fwd-api-${VERSION}.zip .
rm -rf $TEMPDIR
rm fwd-api-${VERSION}.tar
