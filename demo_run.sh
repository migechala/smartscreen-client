#!/bin/bash

echo "This demo shows the program without actually installing it. To install, run install.sh."

mkdir -p lib/build

cd lib/build
cmake ..
make
cd ..
./build/smartmirror
