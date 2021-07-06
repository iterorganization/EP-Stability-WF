import os, imas, sys, pdb, random, copy
from lxml import etree
import xml.etree.ElementTree as ET

from workflow.functions_wf import parameters_workflow, read_timestep, actor_settings, imports_check
from interface.create_workflow_param import create_xml_param_from_file
from imas import imasdef


def actor_call(actor_name, config_folder_path, system_params):
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
  slice_begin = 0
  slice_end = system_params['itend'] - system_params['itbegin']
  shot_no = system_params['shot_nr']

  if actor_params['entrypoint_actor']:
    database = system_params['machine']
    database_out = system_params['machine_out']
    run = system_params['run_in']
    run_out = system_params['run_out']
    user = system_params['user']
    slice_begin = system_params['itbegin']
    slice_end = system_params['itend']
  else:
    database = system_params['machine_out']
    run = system_params['run_out']
    user = os.getenv('USER')

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user = user,
                              database = database,
                              run = run,
                              current_config_folder = config_folder_path)

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND, database, shot_no, run , user)
  status, _ = input.open()
  if status!=0:
    print("Can't open the selected dataset!", file=sys.stderr)
    sys.exit(1)

  if actor_params['entrypoint_actor']:
    # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
    print('=> Create output datafile')
    output = imas.DBEntry(imasdef.MDSPLUS_BACKEND, database_out, shot_no, run_out, os.getenv('USER'))
    output.create()
  else:
    output = input
    for ids_name, ids_occ in output_ids.items():
      input.delete_data(ids_name ,occurrence=ids_occ)

  
  for itime in range(slice_begin, slice_end + 1):
    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    equilibrium_in = imas.equilibrium()
    equilibrium_occ = 0
    core_profiles_in = imas.core_profiles()
    core_profiles_occ = 0
    mhd_linear_in = imas.mhd_linear()
    mhd_linear_occ = 0
    distributions_in = imas.distributions()
    distributions_occ = 0

    for ids_name, ids_occ in input_ids.items():
      if ids_name == 'equilibrium':
        equilibrium_in = input.get_slice(ids_name, time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=ids_occ)
        equilibrium_occ = ids_occ
      if ids_name == 'mhd_linear':
        mhd_linear_in = input.get_slice(ids_name, time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=ids_occ)
        mhd_linear_occ = ids_occ
      if ids_name == 'core_profiles':
        core_profiles_in = input.get_slice(ids_name, time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=ids_occ)
        core_profiles_occ = ids_occ

    
    equilibrium_out, mhd_linear_out, core_profiles_out, distributions_out = actor_params['wrapper'](equilibrium_in,
                                                              core_profiles_in,
                                                              mhd_linear_in,
                                                              distributions_in,
                                                              config_folder_path + actor_params['config_file_name'],
                                                              'mpi_local',
                                                              mpi_processes = system_params['mpi_processes'])

    if equilibrium_out:
      output.put_slice(equilibrium_out, occurrence=equilibrium_occ)
      print('*************************************')
      print('Output time = ', equilibrium_out.time[0])
      print('Saved '+ actor_name +' equilibrium under occurrence ' + str(equilibrium_occ))
      print('*************************************')
      
    if mhd_linear_out:
      output.put_slice(mhd_linear_out, occurrence=mhd_linear_occ)
      print('*************************************')
      print('Output time = ', mhd_linear_out.time[0])
      print('Saved '+ actor_name +' mhd_linear under occurrence ' + str(mhd_linear_occ))
      print('*************************************')

    if core_profiles_out:
      output.put_slice(core_profiles_out, occurrence=core_profiles_occ)
      print('*************************************')
      print('Output time = ', core_profiles_out.time[0])
      print('Saved '+ actor_name +' core_profiles under occurrence ' + str(core_profiles_occ))
      print('*************************************')

    if distributions_out:
      output.put_slice(distributions_out, occurrence=distributions_occ)
      print('*************************************')
      print('Output time = ', distributions_out.time[0])
      print('Saved '+ actor_name +' distributions under occurrence ' + str(distributions_occ))
      print('*************************************')

  input.close()