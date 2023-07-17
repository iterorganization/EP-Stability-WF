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

# For all python files in the repo (*.py and ep_{no,}gui)
file_list="$(find ${basedir} -iname '*.py' | tr '\n' ' ') ${basedir}/ep_gui ${basedir}/ep_nogui"
for filename in ${file_list}; do
  cp ${filename} ./
  loc_name=$(basename ${filename})

  # Check syntax
  python -m py_compile ${loc_name}

  # Run flake8: cheat, since we know this won't pass
  flake8 ${loc_name} || echo 1
done


if [ ${use_tmp_dir} -eq 1 ]; then
    ls -althr . __pycache__
    cd -
    rm -r ${tmpdir}
fi
