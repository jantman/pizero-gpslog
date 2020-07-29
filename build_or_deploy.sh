#!/bin/bash -x

set -x
set -e

if [ -z "$1" ]; then
    >&2 echo "USAGE: build_or_deploy.sh [build|dockerbuild|push]"
    exit 1
fi

function gettag {
    # if it's a build of a tag, return that right away
    [ ! -z "$TRAVIS_TAG" ] && { echo $TRAVIS_TAG; return 0; }
    # otherwise, prefix with PR number if available
    prefix=''
    [ ! -z "$TRAVIS_PULL_REQUEST" ] && [[ "$TRAVIS_PULL_REQUEST" != "false" ]] && prefix="PR${TRAVIS_PULL_REQUEST}_"
    ref="test_${prefix}$(git rev-parse --short HEAD)_$(date +%s)"
    echo "${ref}"
}

function getversion {
    python -c 'from jiveapi.version import VERSION; print(VERSION)'
}

function pythonbuild {
    rm -Rf dist
    python setup.py sdist bdist_wheel
    ls -l dist
}

function pythonpush {
    pip install twine
    twine upload dist/*
}

if [[ "$1" == "build" ]]; then
    pythonbuild
elif [[ "$1" == "push" ]]; then
    pythonpush
else
    >&2 echo "USAGE: build_or_deploy.sh [build|push]"
    exit 1
fi
