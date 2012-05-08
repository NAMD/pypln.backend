#!/bin/bash

TMP_DIR=/tmp/pypln-docs
current_branch=$(git branch | grep '*' | cut -d ' ' -f 2)

# Temporary directory to store static files
rm -rf $TMP_DIR
mkdir $TMP_DIR

# Stash changes
git stash save "saved to build doc" || exit 1
git checkout develop

# Make Sphinx documentation
cd doc
make html
cd ..
mv doc/_build/html/* $TMP_DIR/
rm -rf doc/_build

# Make Reference documentation using epydoc
echo "Building Api Docs with EpyDoc..."
epydoc -v -u https://github.com/namd/pypln --debug --graph=all --parse-only --html --no-frames -o $TMP_DIR/reference pypln/ || exit 1

git checkout gh-pages
rm -rf *
mv $TMP_DIR/* .
rm -rf $TMP_DIR
git add .
git commit -m 'Docs build'
git checkout $current_branch
git stash pop
