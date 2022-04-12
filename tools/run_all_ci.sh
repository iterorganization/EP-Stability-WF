#!/bin/bash

for script_file in ci-plans/st?{1,2}*.sh
do
    [ -e ${script_file} ] || continue
    output_file=$(basename ${script_file} | cut -d"-" -f1)
    {
    {
       mpi_procs=1
       [ "${output_file}" == st02a ] && mpi_procs=4
       sbatch --wait -t 00:05:00 -J EPWF_CI_${output_file} -n 1 -c${mpi_procs} -o ${output_file}.out -e ${output_file}.err -D $(pwd) ${script_file}
       ex_st=$?
       [ $ex_st -ne 0 ] && [ $ex_st -ne 127 ] && echo "${script_file} ${ex_st} ${output_file}.err"
    } &
    }
done

wait < <(jobs -p)
