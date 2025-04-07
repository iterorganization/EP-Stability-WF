#!/bin/bash
# Bamboo Run script
# Stage 1: Test Helena + Ligka 5/4/1
set -e

job_name=02-hl5_x2

# Set up environment
. ./ci-plans/st00-header.sh || exit 1
# Check Flake8 & Cerberus are installed (in venv)
. ./ci-plans/st00a-header_venv.sh || exit 1
set -v

# Display some info
module list -t --no-pager

# If we're in a SLURM job, pwd is repo, since $0 will be the temp batch script
if [ ! -z ${SLURM_JOB_UID} ]; then
    basedir=$(pwd)
else
    basedir=$(readlink -f $(dirname ${0})/..)
fi
use_tmp_dir=${use_tmp_dir:-1}

## If we need to do something different when running in Bamboo
if [ ! -z ${bamboo_buildKey} ]; then
  # imasdb TEST
    use_tmp_dir=0
fi

if [ ${use_tmp_dir} -eq 1 ]; then
    tmpdir=$(mktemp -d)
    cd $tmpdir
    cp -R ${basedir}/ci-plans/files/${job_name} ./
    data_dir=./
else
    data_dir=ci-plans/files/
fi

python ${basedir}/ep_nogui -c ${data_dir}/02-hl5_x2

# Test the output
# python ${basedir}/ci-plans/files/03-output/output_test.py -o 0 -v ${basedir}/ci-plans/files/03-output/validation-02-hl5_x2.yaml || echo 1


if [ ${use_tmp_dir} -eq 1 ]; then
    cd -
    rm -r ${tmpdir}
fi
