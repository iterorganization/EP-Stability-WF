#!/bin/bash
# Bamboo Run script
# Stage 1: Test Helena + Ligka 5/4/1
set -e

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
use_tmp_dir=1

if [ ${use_tmp_dir} -eq 1 ]; then
    tmpdir=$(mktemp -d)
    cd $tmpdir
fi

# TODO: run in venv

# Build python module
# Add --user if not using venv
#user_flag=--user
user_flag=
python3 -m pip install ${user_flag} ${basedir}

# Test
python3 -c "import ep_stability_wf"

# Uninstall
python3 -m pip uninstall --yes EP-Stability-WF

if [ ${use_tmp_dir} -eq 1 ]; then
    cd -
    rm -r ${tmpdir}
fi
