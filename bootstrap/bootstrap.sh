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

echo -e $INFO Installing and compiling python3.10
$SSH_PREFIX ssh "$SSHUSER@$SSHTARGET" 'bash -s' < python_install.sh