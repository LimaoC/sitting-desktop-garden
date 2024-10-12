#!/bin/bash
WARN="bootstrap[\033[1;33mWARN\033[0m]"
INFO="bootstrap[\033[1;32mINFO\033[0m]"
ERROR="bootstrap[\033[1;31mERROR\033[0m]"

if ! sudo swapoff /var/swap; then
    echo -e $WARN Error with swapoff 
fi

if ! sudo fallocate -l 2G /var/swap; then
    echo -e $ERROR Error with fallocate
    exit 1
fi

if ! sudo mkswap /var/swap; then
    echo -e $ERROR Error with mkswap
    exit 1
fi

if ! sudo swapon /var/swap; then
    echo -e $ERROR Error with swapon
    exit 1
fi