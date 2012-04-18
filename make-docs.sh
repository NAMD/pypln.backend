#!/bin/bash

# Temporary directory to store static files
rm -rf tmp-docs
mkdir tmp-docs
touch tmp-docs/.nojekyll

# Make Sphinx documentation
cd doc
make html
cd ..
mv doc/_build/html/* tmp-docs/
rm -rf doc/_build

# Make Reference documentation using epydoc
epydoc -v -u https://github.com/namd/pypln --graph=all --parse-only --html --no-frames -o tmp-docs/reference pypln/
