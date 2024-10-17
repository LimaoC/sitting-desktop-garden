#!/bin/bash

WARN="[\033[1;33mWARN\033[0m]"
INFO="[\033[1;32mINFO\033[0m]"
ERROR="[\033[1;31mERROR\033[0m]"

SSHTARGET=$1
SSHUSER=$2

# Ready to rock
cd scripts

echo -e $INFO Bootstrapping the Pi
if ! ./bootstrap.sh $SSHTARGET $SSHUSER; then
    exit 1;
fi

echo -e $INFO Deploying codebase
if ! ./deploy.sh ../deploypaths.txt $SSHTARGET $SSHUSER; then
    exit 1;
fi

echo -e $INFO 
ssh $SSHUSER@$SSHTARGET 'bash -s' < run_garden.sh
