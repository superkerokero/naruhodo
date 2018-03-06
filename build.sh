#!/bin/bash

# set default commit message
# if [ ! -z $1 ]; then
#     msg=$1
# else
#     msg="Default git commit message used."
# fi

# Install develop version of the repo
pip uninstall -y naruhodo
pip install -e .

# Create API documentation to docs folder using pdoc
rm -rf docs
mkdir tempdoc
pdoc --html --html-dir tempdoc naruhodo
mv tempdoc/naruhodo docs
rm -rf tempdoc

# Remove legacy dist
rm -rf dist
rm -rf build
rm -rf naruhodo.egg-info

# Build dist and wheel for distribution
python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*

# Clean up
rm -rf dist
rm -rf build
rm -rf naruhodo.egg-info

# Push to github repo
git add -A
git commit
git push origin dev