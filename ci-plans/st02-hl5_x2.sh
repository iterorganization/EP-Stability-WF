#!/bin/bash
# Bamboo Run script
# Stage 1: Test Helena + Ligka 5/4/1
set -e

# Set up environment
. ./ci-plans/st00-header.sh || exit 1
# Check Cerberus is installed
pip install --user cerberus
set -v

# Display some info
module list -t --no-pager

# If we're in a SLURM job, pwd is repo, since $0 will be the temp batch script
if [ ! -z ${SLURM_JOB_UID} ]; then
    basedir=$(pwd)
else
    basedir=$(readlink -f $(dirname ${0})/..)
fi
use_tmp_dir=1

## If we need to do something different when running in Bamboo
#if [ ! -z ${bamboo_buildKey} ]; then
#  # imasdb TEST
#fi

if [ ${use_tmp_dir} -eq 1 ]; then
    tmpdir=$(mktemp -d)
    cd $tmpdir
    cp -R ${basedir}/ci-plans/files/01-hl5 ./
fi

python ${basedir}/ep_nogui -c 01-hl5

# Test the output

python ${basedir}/ci-plans/03-output/output_test -o 0 -v ${basedir}/ci-plans/files/03-output/validation-01-hl5.yaml


if [ ${use_tmp_dir} -eq 1 ]; then
    cd -
    rm -r ${tmpdir}
fi
