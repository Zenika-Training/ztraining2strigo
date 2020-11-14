#!/bin/sh

# Install pypa build
pip --quiet install build

# Build wheel
mkdir --parent build/
python3 -m build --wheel .
