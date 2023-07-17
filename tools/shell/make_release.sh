#!/bin/bash

set -v

if [ $# -lt 1 ]; then
    echo "At least 1 argument required. Usage:"
    echo "$0 tagname [commit message]"
    exit 1
fi
USE_MESSAGE=0
if [ $# -gt 1 ]; then
    USE_MESSAGE=1
fi

VER=$1
shift

if [ $USE_MESSAGE -eq 1 ]; then
    MESSAGE="$@"
fi

sed -i -r "s/(version[ ]*=[ ]*).*$/\1\"${VER}\",/" setup.py
git add setup.py

if [ ${USE_MESSAGE} -eq 1 ]; then
    git commit -m "${VER}: ${MESSAGE}"
    git tag -a ${VER} -m "${MESSAGE}"
else
    git commit -m "${VER} release"
    git tag -a ${VER}
fi

echo "Now please check, and then: git push origin develop; git push origin ${VER}"
