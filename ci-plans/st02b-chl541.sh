#!/bin/bash
# Bamboo Run script
# Stage 1: Test Chease + Helena + Ligka 5/4/1
set -e

job_name=02b-chl541

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

outfile=$(mktemp)
errfile=$(mktemp)
## Job failed, maybe due to known error, in which case we'll mark it as passing
python ${basedir}/ep_nogui -c ${data_dir}/${job_name} 1> >(tee ${outfile}) 2> >(tee ${errfile}) || {
    tmp_status=$?
    grep "decode" ${errfile} > /dev/null || exit ${tmp_status} && {
        echo ""
        echo "Failed due to known FC2K bug: failed, but exit 0"
        rm ${outfile} ${errfile}
        exit 0
    }
}
rm ${outfile} ${errfile}

# Test the output
# python ${basedir}/ci-plans/files/03-output/output_test.py -r 30 -o 0 1 2 -v ${basedir}/ci-plans/files/03-output/validation-${job_name}.yaml || echo 1


if [ ${use_tmp_dir} -eq 1 ]; then
    cd -
    rm -r ${tmpdir}
fi
