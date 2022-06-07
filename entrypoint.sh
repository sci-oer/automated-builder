#!/bin/bash

if [[ "$1" == "bash" ]]; then
    bash --init-file <(echo "ls; pwd")
    exit 0
else
    echo "run builder and pass through all options '$@'"
    scioer-builder "$@"
    exit $?
fi
