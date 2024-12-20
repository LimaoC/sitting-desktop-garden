#!/bin/bash
ERROR="deploy[\033[1;31mERROR\033[0m]"

sudo apt-get install build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    python3-pip \
    zip

mkdir -p dlib
git clone https://github.com/davisking/dlib.git dlib/
cd ./dlib
if ! sudo python3.10 setup.py install --compiler-flags "-O3"; then
    echo -e "$ERROR Error building dlib"
    exit 1;
fi