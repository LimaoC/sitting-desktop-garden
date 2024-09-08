#!/bin/bash

WARN="[\033[1;33mWARN\033[0m]"
INFO="[\033[1;32mINFO\033[0m]"
ERROR="[\033[1;31mERROR\033[0m]"

NUMCORES=$(lscpu -p | wc -l)
NUMCORES=$((NUMCORES - 4))
echo -e "$INFO Your Pi has $NUMCORES cores"

# This script follows from https://hub.tcno.co/pi/software/python-update/ pretty closely

echo -e "$INFO Updating machine and installing dependencies"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

echo -e "$INFO Downloading from source"
if ! wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz; then
    exit 1
fi

sudo tar zxf Python-3.10.12.tgz
cd Python-3.10.12
echo -e "$INFO Configuring compilation"
if ! sudo ./configure; then
    exit 1
fi

echo -e "$INFO Compiling (this may take a while)"
if ! sudo make -j $NUMCORES; then
    exit 1
fi

echo -e "$INFO Installing"
if ! sudo make altinstall; then
    exit 1
fi

echo -e "Cleaning up"
sudo rm Python-3.10.12.tgz
sudo rm -r Python-3.10.12
