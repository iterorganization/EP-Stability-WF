#!/bin/bash
# Bamboo Run script
# Stage 1: Test Helena + Ligka 5/4/1
set -e

# Set up environment
. ./ci-plans/st00-header.sh || exit 1

set -v

# Display some info
module list -t --no-pager


file_list="$(find -iname '*.py' | tr '\n' ' ') ep_gui ep_nogui"
for filename in ${file_list}; do
  python -m py_compile ${filename}
done