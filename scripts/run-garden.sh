#!/bin/bash

# Usage: ./run.sh [--no-posture-model]

ERROR="[\033[1;31mERROR\033[0m]"

cd build/

if ! type -P python3.10 >/dev/null 2>&1; then
    echo -e "$ERROR python3.10 not found"
    exit 2
fi

if ! type -P python3.11 >/dev/null 2>&1; then
    echo -e "$ERROR python3.11 not found"
    exit 2
fi

if [ -n "$1" ]; then
    if [ $1 = "--no-posture-model" ]; then
        python3.10 client/overlord_overlord.py --no-posture-model
    else
        echo -e "$ERROR Unrecognised first argument: $1"
        exit 1
    fi
else
    python3.10 client/overlord_overlord.py
fi
