#!/bin/bash
# Bamboo Run script

nlines=$(git grep -in "[ 	]\+$" | grep -v "\.patch" | tee /dev/stderr | wc -l || echo ""); exit $nlines
