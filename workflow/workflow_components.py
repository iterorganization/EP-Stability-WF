import os
import imas
import sys

from workflow.functions_wf import read_timestep, actor_settings, imports_check, scenario_mod, time_construction
from imas import imasdef


def actor_call(actor_name, config_folder_path, system_params, curr_str=None, scenario_params=None):
    ''' This method initializes and runs an workflow actor
        Params:
          actor_name: str - name of the actor to run
          config_folder_path: str - path to the general config folder
          system_params: Dict - I/O system configuration
    '''

    # Check if the actor exists (properly imported):
    if imports_check(actor_name) == 0:
        return

    print('*************************************')
    print('Starting ' + actor_name)
    print('*************************************')

    actor_params = actor_settings(actor_name)

    input_ids = actor_params['input_ids']
    output_ids = actor_params['output_ids']

    database = None
    run = None
    user = None
    shot_no = system_params['shot_nr']

    if system_params['hdf5'] == 1:
        backend = imasdef.HDF5_BACKEND
    else:
        backend = imasdef.MDSPLUS_BACKEND

    if actor_name == 'Ligka_m5':
        mpi_processes = 1
    else:
        mpi_processes = system_params['mpi_processes']

    if actor_params['entrypoint_actor']:
        database = system_params['machine']
        database_out = system_params['machine_out']
        run = system_params['run_in']
        run_out = system_params['run_out']
        user = system_params['user']
        time_index_list, _ = time_construction(system_params['itime'])
    else:
        database = system_params['machine_out']
        run = system_params['run_out']
        user = os.getenv('USER')
        _, time_index_list = time_construction(system_params['itime'])

    # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
    # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
    time, ntime = read_timestep(user=user,
                                database=database,
                                run=run,
                                current_config_folder=config_folder_path, backend=backend)

    # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
    input = imas.DBEntry(backend, database, shot_no, run, user)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)

    if actor_params['entrypoint_actor']:
        # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
        print('=> Create output datafile')
        output = imas.DBEntry(backend,
                              database_out, shot_no, run_out, os.getenv('USER'))
        output.create()
    else:
        output = input
        for ids_name, ids_occ in output_ids.items():
            input.delete_data(ids_name, occurrence=ids_occ)

    for i, itime in enumerate(time_index_list):
        # EXECUTE PHYSICS CODE
        print(f'Time = {time[itime]} s, itime = {i}/{ntime-1}')

        equilibrium_in = imas.equilibrium()
        equilibrium_occ = 0
        core_profiles_in = imas.core_profiles()
        core_profiles_occ = 0
        mhd_linear_in = imas.mhd_linear()
        mhd_linear_in.ids_properties.homogeneousTime = 1
        mhd_linear_occ = 0
        distributions_in = imas.distributions()
        distributions_occ = 0

        for ids_name, ids_occ in input_ids.items():
            if ids_name == 'equilibrium':
                equilibrium_in = input.get_slice(
                    ids_name, time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=ids_occ)
                equilibrium_occ = ids_occ
            if ids_name == 'mhd_linear':
                mhd_linear_in = input.get_slice(
                    ids_name, time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=ids_occ)
                mhd_linear_occ = ids_occ
            if ids_name == 'core_profiles':
                core_profiles_in = input.get_slice(
                    ids_name, time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=ids_occ)
                core_profiles_occ = ids_occ
                if actor_params['entrypoint_actor']:
                    core_profiles_in = scenario_mod(
                        core_profiles_in, curr_str, scenario_params)

        equilibrium_out, mhd_linear_out, core_profiles_out, distributions_out = actor_params['wrapper'](equilibrium_in,
                                                                                                        core_profiles_in,
                                                                                                        mhd_linear_in,
                                                                                                        distributions_in,
                                                                                                        config_folder_path +
                                                                                                        actor_params['config_file_name'],
                                                                                                        mpi_processes=mpi_processes)

        if equilibrium_out:
            output.put_slice(
                equilibrium_out, occurrence=output_ids['equilibrium'])
            print('*************************************')
            print('Output time = ', equilibrium_out.time[0])
            print('Saved ' + actor_name +
                  ' equilibrium under occurrence ' + str(output_ids['equilibrium']))
            print('*************************************')

        if mhd_linear_out:
            if itime == 0:  # Fix until mhd_linear is also independent of put/put_slice PR #600
                output.put(
                    mhd_linear_out, occurrence=output_ids['mhd_linear'])
                print('*************************************')
                print('Initial Output')
                print('Saved ' + actor_name +
                      ' mhd_linear under occurrence ' + str(output_ids['mhd_linear']))
                print('*************************************')
            else:
                output.put_slice(
                    mhd_linear_out, occurrence=output_ids['mhd_linear'])
                print('*************************************')
                print('Output time = ', mhd_linear_out.time[0])
                print('Saved ' + actor_name +
                      ' mhd_linear under occurrence ' + str(output_ids['mhd_linear']))
                print('*************************************')

        if core_profiles_out:
            output.put_slice(core_profiles_out,
                             occurrence=output_ids['core_profiles'])
            print('*************************************')
            print('Output time = ', core_profiles_out.time[0])
            print('Saved ' + actor_name +
                  ' core_profiles under occurrence ' + str(output_ids['core_profiles']))
            print('*************************************')

        if distributions_out:
            output.put_slice(distributions_out,
                             occurrence=output_ids['distributions'])
            print('*************************************')
            print('Output time = ', distributions_out.time[0])
            print('Saved ' + actor_name +
                  ' distributions under occurrence ' + str(output_ids['distributions']))
            print('*************************************')

    input.close()
    output.close()
