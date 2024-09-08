#!/bin/bash

WARN="[\033[1;33mWARN\033[0m]"
INFO="[\033[1;32mINFO\033[0m]"
ERROR="[\033[1;31mERROR\033[0m]"

SSHTARGET=$1
SSHUSER=$2

if ! nc -z $SSHTARGET 22 2>/dev/null; then
	echo -e "$ERROR Cannot find target"
	exit 1
fi

# Check for sshpass
command -v sshpass > /dev/null
SSHPASS=$?

if [ $SSHPASS == 1 ]; then
    echo -e "$WARN sshpass not found. I will continue but will need you to reenter your password often"
    SSH_PREFIX=""
else 
    PASSWORD="USER INPUT"
    echo -e "$INFO I'll use sshpass to manage your password"
    read -sp "Enter password: " PASSWORD
    echo ""
    SSH_PREFIX="sshpass -p $PASSWORD"
fi

if $SSH_PREFIX ssh "$SSHUSER@$SSHTARGET" 'command -v python3.10 > /dev/null'; then
    echo -e "$WARN It appears Python3.10 already exists on target. I won't compile it again."
else
    echo -e $INFO Installing and Compiling Python
    if ! $SSH_PREFIX ssh "$SSHUSER@$SSHTARGET" 'bash -s' < python_install.sh; then
        echo -e $ERROR Something went wrong... please check above.
        exit 1
    fi
    echo -e $INFO Python successfully installed!
fi
