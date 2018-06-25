#!/bin/bash
mkdir .tempcmake && cd .tempcmake 

sudo apt-get -y install build-essential

wget https://cmake.org/files/v3.9/cmake-3.9.4.tar.gz

tar xf cmake-3.9.4.tar.gz && cd cmake-3.9.4

bash configure --prefix=/usr

sudo make -j3

sudo make install

cd .. && rm -rf .tempcmake
