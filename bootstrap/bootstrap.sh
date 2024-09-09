#!/bin/bash

WARN="[\033[1;33mWARN\033[0m]"
INFO="[\033[1;32mINFO\033[0m]"
ERROR="[\033[1;31mERROR\033[0m]"

SSHTARGET=$1
SSHUSER=$2

if ! nc -z $SSHTARGET 22 2> /dev/null; then
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

SSH_GO="$SSH_PREFIX ssh $SSHUSER@$SSHTARGET"

echo -e $INFO Installing and Compiling Python
if $SSH_GO 'command -v python3.10 > /dev/null'; then
    echo -e "$INFO It appears Python3.10 already exists on target. I won't compile it again."
else
    if ! $SSH_GO 'bash -s' < python_install.sh; then
        echo -e $ERROR Something went wrong... please check above.
        exit 1
    fi
    echo -e $INFO Python3.10 installed
fi

echo -e $INFO Installing uv
if $SSH_GO 'test -f ~/.cargo/bin/uv'; then
    echo -e "$INFO uv already installed"
else
    if ! $SSH_GO 'curl -LsSf https://astral.sh/uv/install.sh | sh'; then
        echo -e $ERROR uv installation failed
        exit 1
    fi
    echo -e $INFO uv installed
fi

echo -e $INFO Copying Dependency Data
$SSH_PREFIX scp ../{pyproject.toml,requirements_uvonly.in,README.md} ./apt_packages.txt $SSHUSER@$SSHTARGET:~/
echo -e $INFO Installing apt packages
$SSH_GO "xargs -a apt_packages.txt sudo apt-get install -y"
echo -e $INFO Compiling dependencies
$SSH_GO "~/.cargo/bin/uv pip compile pyproject.toml requirements_uvonly.in -o requirements.txt"
echo -e $INFO Installing dependencies
$SSH_GO "sudo ~/.cargo/bin/uv pip install --system --python 3.10 -r requirements.txt"
