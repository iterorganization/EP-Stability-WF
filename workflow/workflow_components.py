import os, imas, sys, pdb, random, copy
from lxml import etree
import xml.etree.ElementTree as ET

from helena_imas.wrapper import helena_imas_actor
from ligka.wrapper import ligka_actor
#from chease.wrapper import chease_actor
from hagis1.wrapper import hagis1_actor
from workflow.functions_wf import parameters_workflow, read_timestep



def helena(param, user):
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(param['user'], param['machine'], param['run_in'])

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  print('Starting HELENA')
  input = imas.ids(param['shot_nr'], param['run_in'], 0, 0)
  input.open_env(param['user'], param['machine'], '3')
  idx_in = input.equilibrium.getPulseCtx()

  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(param['shot_nr'], param['run_out'])
  output.create_env(user, param['machine_out'], '3')

  for itime in range(param['itbegin'], param['itend'] + 1):
      
    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)
    input.equilibrium.setPulseCtx(idx_in)
    input.equilibrium.getSlice(time[itime], 1)
    input.core_profiles.setPulseCtx(idx_in)
    input.core_profiles.getSlice(time[itime], 1)

    idx_out = output.equilibrium.getPulseCtx()

    if param['Equilibrium_code'] == 'Helena':
        output.equilibrium = helena_imas_actor(input.equilibrium)
    #else:
        #output.equilibrium = chease_actor(
            #input.equilibrium, 'workflow/input/chease_input_choices_default.xml')

    output.equilibrium.setPulseCtx(idx_out)
    output.core_profiles.copyValues(input.core_profiles)

    output.core_profiles.setExpIdx(idx_out)

    if itime == param['itbegin']:

        output.equilibrium.put()
        output.core_profiles.put()
    else:

        output.equilibrium.putSlice()
        output.core_profiles.putSlice()
    print('*************************************')
    print('Output time = ', output.equilibrium.time[0])
    print('Saved helena equilibrium and core_profiles')
    print('*************************************')
      
  input.close()
  output.close()

def hagis_1(param, user, time_runs):
  run_out = 4

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'])

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(param['shot_nr'], param['run_out'], 0, 0)
  input.open_env(user, param['machine_out'], '3')
  idx_in = input.equilibrium.getPulseCtx()

  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(param['shot_nr'], run_out)

  input.mhd_linear.ids_properties.homogeneous_time = 1

  # CREATE OUTPUT DATAFILE
  output.create_env(user, param['machine_out'], '3')

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    input.equilibrium.setPulseCtx(idx_in)
    input.equilibrium.getSlice(time[itime], 2)
    idx_out = output.equilibrium.getPulseCtx()

    input.mhd_linear.time = input.equilibrium.time

    output.equilibrium, output.mhd_linear = hagis1_actor(input.equilibrium, input.mhd_linear, 'workflow/input/hagis1.xml')

    input.equilibrium.copyValues(output.equilibrium)
    
    input.equilibrium.setPulseCtx(idx_in)

    if itime == 0:
        input.equilibrium.put(1)
    else:
        input.equilibrium.putSlice(1)

    print('*************************************')
    print('Output time = ', input.equilibrium.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved equilibrium from HAGIS 1 under oc 1')
    print('*************************************')

  input.close()
  output.close()

def ligka_mode_1(param, user, time_runs):
  # SETTINGS
  run_out = 1

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'])

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(param['shot_nr'], param['run_out'], 0, 0)
  input.open_env(user, param['machine_out'], '3')
  idx_in = input.mhd_linear.getPulseCtx()

  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(param['shot_nr'], run_out)

  # CREATE OUTPUT DATAFILE
  output.create_env(user, param['machine_out'], '3')

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)
    
    input.mhd_linear.setPulseCtx(idx_in)
    input.mhd_linear.getSlice(time[itime], 1, 1)
    input.equilibrium.setPulseCtx(idx_in)
    input.equilibrium.getSlice(time[itime], 1)
    input.core_profiles.setPulseCtx(idx_in)
    input.core_profiles.getSlice(time[itime], 1)
    idx_out = output.mhd_linear.getPulseCtx()


    output.mhd_linear = ligka_actor(input.equilibrium, input.core_profiles,input.mhd_linear, 'workflow/input/z_ligka.xml', 'mpi_local', mpi_processes=4)
   
    input.mhd_linear.copyValues(output.mhd_linear)
    input.mhd_linear.setPulseCtx(idx_in)

    if itime == 0:
        input.mhd_linear.put(2)
    else:
        input.mhd_linear.putSlice(2)

    print('*************************************')
    print('Output time = ', input.mhd_linear.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 1 under oc 2')
    print('*************************************')

  input.close()
  output.close()


def ligka_mode_5(param, user, time_runs):
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'])

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(param['shot_nr'], param['run_out'], 0, 0)
  input.open_env(user, param['machine_out'], '3')
  idx_in = input.mhd_linear.getPulseCtx()

  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')

  input.mhd_linear.ids_properties.homogeneous_time = 1

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    input.equilibrium.setPulseCtx(idx_in)
    input.equilibrium.getSlice(time[itime], 1)
    input.core_profiles.setPulseCtx(idx_in)
    input.core_profiles.getSlice(time[itime], 1)

    input.mhd_linear.time = input.equilibrium.time
    idx_out = input.mhd_linear.getPulseCtx()


    input.mhd_linear = ligka_actor(input.equilibrium, input.core_profiles, input.mhd_linear, 'workflow/input/z_ligka.xml', 'mpi_local')

    input.mhd_linear.setPulseCtx(idx_in)

    if itime == 0:
        input.mhd_linear.put()
    else:
        input.mhd_linear.putSlice()

    print('*************************************')
    print('Output time = ', input.mhd_linear.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 5 under oc 0')
    print('*************************************')

  input.close()



def ligka_mode_4(param, user, time_runs):
  # SETTINGS
  run_out = 4

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'])

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(param['shot_nr'], param['run_out'], 0, 0)
  input.open_env(user, param['machine_out'], '3')
  idx_in = input.mhd_linear.getPulseCtx()

  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(param['shot_nr'], run_out)

  # CREATE OUTPUT DATAFILE
  output.create_env(user, param['machine_out'], '3')

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    input.mhd_linear.setPulseCtx(idx_in)
    input.mhd_linear.getSlice(time[itime], 1)
    input.equilibrium.setPulseCtx(idx_in)
    input.equilibrium.getSlice(time[itime], 1)
    input.core_profiles.setPulseCtx(idx_in)
    input.core_profiles.getSlice(time[itime], 1)
    idx_out = output.mhd_linear.getPulseCtx()

    output.mhd_linear = ligka_actor(input.equilibrium, input.core_profiles, input.mhd_linear, 'workflow/input/z_ligka.xml', 'mpi_local', mpi_processes=4)
    
    input.mhd_linear.copyValues(output.mhd_linear)
    input.mhd_linear.setPulseCtx(idx_in)

    if itime == 0:
        input.mhd_linear.put(1)
    else:
        input.mhd_linear.putSlice(1)

    print('*************************************')
    print('Output time = ', input.mhd_linear.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 4 under oc 1')
    print('*************************************')

  input.close()
  output.close()