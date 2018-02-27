#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FTYPE=moving

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --nofix)
        FTYPE=nofix
        shift # past argument
        ;;
        --stillfix)
        FTYPE=stillfix
        shift # past argument
        ;;
        -h|--help)
        echo "USAGE: runfake.sh [--nofix|--stillfix]"
        exit 1
        ;;
    esac
done

gpsfake -S ${DIR}/gpsd/bu303-${FTYPE}.log
