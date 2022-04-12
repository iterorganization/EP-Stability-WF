#!/bin/bash
# Bamboo Run script
# Stage 1: Test Helena + Ligka 5/4/1
set -e

# Set up environment
. ./ci-plans/st00-header.sh || exit 1

set -v

# Display some info
module list -t --no-pager


python ep_nogui -c ./ci-plans/files/01-hl5