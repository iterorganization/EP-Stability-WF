import os, imas, sys, pdb, random, copy
from lxml import etree
import xml.etree.ElementTree as ET

from helena_imas.wrapper import helena_imas_actor
from ligka.wrapper import ligka_actor
#from chease.wrapper import chease_actor
from hagis1.wrapper import hagis1_actor
from hagis2.wrapper import hagis2_actor
from finder9.wrapper import finder9_actor
from workflow.functions_wf import parameters_workflow, read_timestep
from interface.create_workflow_param import create_xml_param_from_file
from imas import imasdef



def helena(current_config_folder, param, user):
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(param['user'], param['machine'], param['run_in'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine'],param['shot_nr'], param['run_in'],param['user'])
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  output.create()

  for itime in range(param['itbegin'], param['itend'] + 1):
      
    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE)
    core_profiles_in = input.get_slice("core_profiles",time[itime],imasdef.PREVIOUS_SAMPLE)

    if param['Equilibrium_code'] == 'Helena':
        equilibrium_out = helena_imas_actor(equilibrium_in, current_config_folder+'/helena.xml')
    #else:
        #output.equilibrium = chease_actor(
            #input.equilibrium, current_config_folder+'/chease_input_choices_default.xml')

    output.put_slice(equilibrium_out)
    output.put_slice(core_profiles_in)

    print('*************************************')
    print('Output time = ', equilibrium_out.time[0])
    print('Saved helena equilibrium and core_profiles')
    print('*************************************')
  output.close()   
  input.close()

def hagis_1(current_config_folder,param, user, time_runs):

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  input.delete_data("mhd_linear",occurrence=3)
  input.delete_data("equilibrium",occurrence=1)

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE)
    mhd_linear_in = input.get_slice("mhd_linear",time[itime],imasdef.PREVIOUS_SAMPLE,occurrence=0) #Load either Mode 5 data or Mode 1 data


    equilibrium_out, mhd_linear_out = hagis1_actor(equilibrium_in, mhd_linear_in, current_config_folder+'/hagis1.xml')

    
    input.put_slice(equilibrium_out,occurrence=1)
    input.put_slice(mhd_linear_out,occurrence=3)

    print('*************************************')
    print('Output time = ', equilibrium_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved equilibrium from HAGIS 1 under oc 1')
    print('Saved mhd_linear from HAGIS 1 under oc 3')
    print('*************************************')

  input.close()

def hagis_2(current_config_folder,param, user, time_runs):

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)
  
  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  input.delete_data("distributions")
  input.delete_data("mhd_linear",occurrence=4)

  

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE,occurrence=1)
    mhd_linear_in = input.get_slice("mhd_linear",time[itime],imasdef.PREVIOUS_SAMPLE,occurrence=3) #Load mhd_linear(3) from hagis 1
    core_profiles_in = input.get_slice("core_profiles",time[itime],imasdef.PREVIOUS_SAMPLE)

    distributions_in = imas.distributions()

    mhd_linear_out, distributions_out  = hagis2_actor(equilibrium_in, mhd_linear_in, core_profiles_in, distributions_in, current_config_folder+'/hagis2.xml','mpi_local', mpi_processes = param['mpi_processes'])

    input.put_slice(distributions_out)
    input.put_slice(mhd_linear_out,occurrence=4)

    print('*************************************')
    print('Output time = ', mhd_linear_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved distributions from HAGIS 2 under oc 0')
    print('Saved mhd_linear from HAGIS 2 under oc 5')
    print('*************************************')

  input.close()

def ligka_mode_1(current_config_folder,param, user, time_runs):

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  input.delete_data("mhd_linear",occurrence=2)

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)
    
    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE)
    core_profiles_in = input.get_slice("core_profiles",time[itime],imasdef.PREVIOUS_SAMPLE)
    mhd_linear_in = input.get_slice("mhd_linear",time[itime],imasdef.PREVIOUS_SAMPLE,occurrence=1)


    mhd_linear_out = ligka_actor(equilibrium_in, core_profiles_in, mhd_linear_in, current_config_folder+'/z_ligka.xml', 'mpi_local', mpi_processes= param['mpi_processes'])


    input.put_slice(mhd_linear_out,occurrence=2)

    print('*************************************')
    print('Output time = ', mhd_linear_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 1 under oc 2')
    print('*************************************')

  input.close()

def ligka_mode_2(current_config_folder,param, user, time_runs):

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  input.delete_data("mhd_linear",occurrence=6)

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)
    
    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE)
    core_profiles_in = input.get_slice("core_profiles",time[itime],imasdef.PREVIOUS_SAMPLE)
    mhd_linear_in = input.get_slice("mhd_linear",time[itime],imasdef.PREVIOUS_SAMPLE,occurrence=1)


    mhd_linear_out = ligka_actor(equilibrium_in, core_profiles_in, mhd_linear_in, current_config_folder+'/z_ligka.xml', 'mpi_local', mpi_processes= param['mpi_processes'])


    input.put_slice(mhd_linear_out,occurrence=6)

    print('*************************************')
    print('Output time = ', mhd_linear_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 2 under oc 6')
    print('*************************************')

  input.close()

def ligka_mode_5(current_config_folder,param, user, time_runs):
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  input.delete_data("mhd_linear",occurrence=0)

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE)
    core_profiles_in = input.get_slice("core_profiles",time[itime],imasdef.PREVIOUS_SAMPLE)

    mhd_linear_in = imas.mhd_linear()

    mhd_linear_out = ligka_actor(equilibrium_in, core_profiles_in, mhd_linear_in, current_config_folder+'/z_ligka.xml', 'mpi_local', mpi_processes= param['mpi_processes'])

    input.put_slice(mhd_linear_out)

    print('*************************************')
    print('Output time = ', mhd_linear_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 5 under oc 0')
    print('*************************************')

  input.close()

def ligka_mode_6(current_config_folder,param, user, time_runs):
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  input.delete_data("mhd_linear",occurrence=5)

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE)
    core_profiles_in = input.get_slice("core_profiles",time[itime],imasdef.PREVIOUS_SAMPLE)
    mhd_linear_in = input.get_slice("mhd_linear",time[itime],imasdef.PREVIOUS_SAMPLE)

    mhd_linear_out = ligka_actor(equilibrium_in, core_profiles_in, mhd_linear_in, current_config_folder+'/z_ligka.xml', 'mpi_local', mpi_processes= param['mpi_processes'])

    input.put_slice(mhd_linear_out,occurrence=5)

    print('*************************************')
    print('Output time = ', mhd_linear_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 6 under oc 5')
    print('*************************************')

  input.close()



def ligka_mode_4(current_config_folder,param, user, time_runs):

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)

  input.delete_data("mhd_linear",occurrence=1)

  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)


    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE)
    core_profiles_in = input.get_slice("core_profiles",time[itime],imasdef.PREVIOUS_SAMPLE)
    mhd_linear_in = input.get_slice("mhd_linear",time[itime],imasdef.PREVIOUS_SAMPLE)

    mhd_linear_out = ligka_actor(equilibrium_in, core_profiles_in, mhd_linear_in, current_config_folder+'/z_ligka.xml', 'mpi_local', mpi_processes= param['mpi_processes'])


    input.put_slice(mhd_linear_out,occurrence=1)

    print('*************************************')
    print('Output time = ', mhd_linear_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved mhd_linear mode 4 under oc 1')
    print('*************************************')

  input.close()

def finder(current_config_folder,param, user, time_runs):

  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  time, ntime = read_timestep(user, param['machine_out'], param['run_out'], current_config_folder)

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,param['machine_out'],param['shot_nr'], param['run_out'],user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)


  for itime in range(0, time_runs + 1):

    # EXECUTE PHYSICS CODE
    print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

    equilibrium_in = input.get_slice("equilibrium",time[itime],imasdef.PREVIOUS_SAMPLE,occurrence=1)
   
    distributions_out = finder9_actor(equilibrium_in, current_config_folder+'/finder_input.xml', 'mpi_local', mpi_processes= param['mpi_processes'])

    input.put_slice(distributions_out,occurrence=1)

    print('*************************************')
    print('Output time = ', distributions_out.time[0])
    print('OUTPUT ITIME = ', itime)
    print('Saved data from finder9 under oc 1')
    print('*************************************')

  input.close()
