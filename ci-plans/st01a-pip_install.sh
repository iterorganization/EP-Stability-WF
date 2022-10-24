#!/bin/bash
# Bamboo Run script
# Stage 1: Test Helena + Ligka 5/4/1
set -e

# Set up environment
. ./ci-plans/st00-header.sh || exit 1
# Check flake8 is installed
pip install --user flake8
export PATH=${PATH}:~/.local/bin

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
python -m pip install --user ${basedir}

# Test
python -c "import ep_stability_wf"

# Uninstall
python -m pip uninstall --yes EP-Stability-WF

if [ ${use_tmp_dir} -eq 1 ]; then
    cd -
    rm -r ${tmpdir}
fi
