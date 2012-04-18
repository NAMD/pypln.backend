#!/bin/bash

TMP_DIR=/tmp/pypln-docs

# Temporary directory to store static files
rm -rf $TMP_DIR
mkdir $TMP_DIR

# Make Sphinx documentation
cd doc
make html
cd ..
mv doc/_build/html/* $TMP_DIR/
rm -rf doc/_build

# Make Reference documentation using epydoc
epydoc -v -u https://github.com/namd/pypln --graph=all --parse-only --html \
       --no-frames -o $TMP_DIR/reference pypln/

echo 'Now execute:'
echo '  git checkout gh-pages'
echo '  rm -rf *'
echo "  mv $TMP_DIR/* ."
echo "  rm -rf $TMP_DIR"
echo "...and them git add/rm files, commit and push"
