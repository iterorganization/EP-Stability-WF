# --------------------------------------------
# PYTHON WRAPPER TO CALL HELENA + LIGKA
# --------------------------------------------


# NEEDED MODULES
import os,imas,sys,pdb,random,copy
from pyal import ALEnv
from lxml import etree
import xml.etree.ElementTree as ET


 # IMPORT PARAMETERS FROM XML --------------------------------------
  
tree = ET.parse('input/z_ligka.xml')
root = tree.getroot()

param = {}
  
print('----- WORKFLOW PARAMETERS ----')

for elem in root.iter():
  if len(elem) == 0:
    try:
      param[elem.tag] = int(elem.text)
    except:
      try:
        param[elem.tag] = float(elem.text)
      except:
        param[elem.tag] = elem.text

    param['input_path'] = 'input/z_ligka.xml'
    print(elem.tag, ' = ', param[elem.tag])

# IMPORT MODULE(S) FOR SPECIFIC PHYSICS CODE(S)
actor_path = os.path.join(os.getenv('KEPLER'), 'imas/src/org/iter/imas/python')
list_of_actors = ['helena_imas', 'ligka']
for name in list_of_actors:
  sys.path[:0] = [os.path.join(actor_path,name)]
  globals()[name] = getattr(__import__(name), name)

#TIME SETTINGS FOR RUNS
begin_time = 12 # initial begin time for mode 5
end_time = 14 #end time for mode 5 (steps from transport code)
time_runs = end_time - begin_time # runs for mode 4,1,...




# PUBLIC and LOCAL DATABASE ENVIRONMENT
# SETTINGS
user_in = 'public'
tokamakname = 'ITER'
user = os.getenv('USER')
version = os.getenv('IMAS_VERSION')[0]


if param['modus'] == 10:
  print('MODE 10 START')
  # SETTINGS
  shot    = 130012
  run_in  = 1
  run_out = 5
  tokamakname_out = 'ligka_modes'
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  print('=> Open input datafile and read total equilibrium IDS for time.')
  input_total = imas.ids(shot,run_in,0,0)
  input_total.open_env(user_in,tokamakname,version)
  input_total.equilibrium.get()
  ntime = len(input_total.equilibrium.time)
  time = input_total.equilibrium.time
  input_total.close()

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(shot,run_in,0,0)
  input.open_env(user_in,tokamakname,'3')
  idx_in = input.equilibrium.getPulseCtx()


  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(shot,run_out)
  output.create_env(user,tokamakname_out,version)
  
 

  for itime in range(begin_time,end_time + 1):

      # EXECUTE PHYSICS CODE
      print('Time = ',time[itime],' s, itime = ',itime,'/',ntime)
      input.equilibrium.setPulseCtx(idx_in)
      input.equilibrium.getSlice(time[itime],1)
      input.core_profiles.setPulseCtx(idx_in)
      input.core_profiles.getSlice(time[itime],1)
 
      idx_out = output.equilibrium.getPulseCtx()
      output.equilibrium = helena_imas(input.equilibrium)
      #print('FINISHED HELENA ---------- STARTING LIGKA')

      #output.mhd_linear = ligka(output.equilibrium,input.core_profiles,input.mhd_linear,'input/z_ligka.xml','mpi_local',mpi_processes=2)
   
      output.equilibrium.setPulseCtx(idx_out)
      #output.mhd_linear.setExpIdx(idx_out)
      output.core_profiles = copy.deepcopy(input.core_profiles)
      output.core_profiles.setExpIdx(idx_out)

      if itime == begin_time:
       #output.mhd_linear.put()
       output.equilibrium.put()
       output.core_profiles.put()
      else:
       #output.mhd_linear.putSlice()
       output.equilibrium.putSlice()
       output.core_profiles.putSlice()
      print('*************************************')
      print('Output time = ',output.equilibrium.time[0])
      print('Saved helena equilibrium and core_profiles')
      print('*************************************')
      
  input.close()
  output.close()
  print('Done.')



if param['modus'] == 5:
  print('MODE 5 START')
  # SETTINGS
  shot    = 130012
  run_in  = 5
  #run_out = 4
  tokamakname_out = 'ligka_modes'
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  print('=> Open input datafile and read total equilibrium IDS for time.')
  input_total = imas.ids(shot,run_in)
  input_total.open_env(user,tokamakname_out,version)
  input_total.equilibrium.get()
  ntime = len(input_total.equilibrium.time)
  time = input_total.equilibrium.time
  input_total.close()

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(shot,run_in,0,0)
  input.open_env(user,tokamakname_out,'3')
  idx_in = input.mhd_linear.getPulseCtx()
  


  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  #output = imas.ids(shot,run_out)

  # CREATE OUTPUT DATAFILE
  #output.create_env(user,tokamakname_out,version)
  input.mhd_linear.ids_properties.homogeneous_time = 1

  for itime in range(0,time_runs + 1):

      # EXECUTE PHYSICS CODE
      print('Time = ',time[itime],' s, itime = ',itime,'/',ntime)
      #idx_in = input.mhd_linear.getPulseCtx()
      input.equilibrium.setPulseCtx(idx_in)
      input.equilibrium.getSlice(time[itime],1)
      input.core_profiles.setPulseCtx(idx_in)
      input.core_profiles.getSlice(time[itime],1)
      #input.mhd_linear.ids_properties.homogeneous_time = 1
      input.mhd_linear.time = input.equilibrium.time
      idx_out = input.mhd_linear.getPulseCtx()
    
      #NEED TO TAKE FROM THE PROF PARAMETER TO CHECK HELENA RAN OR NOT
      print('==========ENDING HELENA OR ALREADY RUN ------STARTING LIGKA===========')
    
      input.mhd_linear = ligka(input.equilibrium,input.core_profiles,input.mhd_linear,'input/z_ligka.xml','mpi_local')
      #input.mhd_linear = copy.deepcopy(output.mhd_linear)
      input.mhd_linear.setPulseCtx(idx_in)
      
   
      if itime == 0:
        input.mhd_linear.put()
      else:
        input.mhd_linear.putSlice()

      print('*************************************')
      print('Output time = ',input.mhd_linear.time[0])
      print('OUTPUT ITIME = ',itime)
      print('Saved mhd_linear mode 5 under oc 0')
      print('*************************************')

  input.close()
  #output.close()
  print('Done.')

 
  
if param['modus'] == 4:
  print('MODE 4 START')
  # SETTINGS
  shot    = 130012
  run_in  = 5
  run_out = 4
  tokamakname_out = 'ligka_modes'
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  print('=> Open input datafile and read total equilibrium IDS for time.')
  input_total = imas.ids(shot,run_in)
  input_total.open_env(user,tokamakname_out,version)
  input_total.equilibrium.get()
  ntime = len(input_total.equilibrium.time)
  time = input_total.equilibrium.time
  input_total.close()

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(shot,run_in,0,0)
  input.open_env(user,tokamakname_out,'3')
  idx_in = input.mhd_linear.getPulseCtx()
  


  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(shot,run_out)

  # CREATE OUTPUT DATAFILE
  output.create_env(user,tokamakname_out,version)


  for itime in range(0,time_runs + 1):

      # EXECUTE PHYSICS CODE
      print('Time = ',time[itime],' s, itime = ',itime,'/',ntime)
      #idx_in = input.mhd_linear.getPulseCtx()
      input.mhd_linear.setPulseCtx(idx_in)
      input.mhd_linear.getSlice(time[itime],1)
      input.equilibrium.setPulseCtx(idx_in)
      input.equilibrium.getSlice(time[itime],1)
      input.core_profiles.setPulseCtx(idx_in)
      input.core_profiles.getSlice(time[itime],1)
      idx_out = output.mhd_linear.getPulseCtx()
    
      #NEED TO TAKE FROM THE PROF PARAMETER TO CHECK HELENA RAN OR NOT
      print('==========ENDING HELENA OR ALREADY RUN ------STARTING LIGKA===========')
    
      output.mhd_linear = ligka(input.equilibrium,input.core_profiles,input.mhd_linear,'input/z_ligka.xml','mpi_local',mpi_processes=1)
      input.mhd_linear = copy.deepcopy(output.mhd_linear)
      input.mhd_linear.setPulseCtx(idx_in)
      
   
      if itime == 0:
        input.mhd_linear.put(1)
      else:
        input.mhd_linear.putSlice(1)

      print('*************************************')
      print('Output time = ',input.mhd_linear.time[0])
      print('OUTPUT ITIME = ',itime)
      print('Saved mhd_linear mode 4 under oc 1')
      print('*************************************')

  input.close()
  output.close()
  print('Done.')

if param['modus'] == 1:
  print('MODE 1 START')
  # SETTINGS
  shot    = 130012
  run_in  = 5
  run_out = 1
  tokamakname_out = 'ligka_modes'
  # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
  # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
  print('=> Open input datafile and read total equilibrium IDS for time.')
  input_total = imas.ids(shot,run_in)
  input_total.open_env(user,tokamakname_out,version)
  input_total.equilibrium.get()
  ntime = len(input_total.equilibrium.time)
  time = input_total.equilibrium.time
  input_total.close()

  # OPEN INPUT IDS'S AGAIN TO PROCEED WITH GETSLICE
  # NOTE: WE CANNOT USE THE SAME INPUT STRUCTURE FOR BOTH GET AND GETSLICE!!!
  # IF WE DO SO: GETSLICE ALWAYS GET THE FIRST TIME SLICE WHATEVER IS ASKED
  input = imas.ids(shot,run_in,0,0)
  input.open_env(user,tokamakname_out,'3')
  idx_in = input.mhd_linear.getPulseCtx()
  


  # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
  print('=> Create output datafile')
  output = imas.ids(shot,run_out)

  # CREATE OUTPUT DATAFILE
  output.create_env(user,tokamakname_out,version)


  for itime in range(0,time_runs + 1):

      # EXECUTE PHYSICS CODE
      print('Time = ',time[itime],' s, itime = ',itime,'/',ntime)
      #idx_in = input.mhd_linear.getPulseCtx()
      input.mhd_linear.setPulseCtx(idx_in)
      input.mhd_linear.getSlice(time[itime],1,1)
      input.equilibrium.setPulseCtx(idx_in)
      input.equilibrium.getSlice(time[itime],1)
      input.core_profiles.setPulseCtx(idx_in)
      input.core_profiles.getSlice(time[itime],1)
      idx_out = output.mhd_linear.getPulseCtx()
    
      #NEED TO TAKE FROM THE PROF PARAMETER TO CHECK HELENA RAN OR NOT
      print('==========ENDING HELENA OR ALREADY RUN ------STARTING LIGKA===========')
    
      output.mhd_linear = ligka(input.equilibrium,input.core_profiles,input.mhd_linear,'input/z_ligka.xml','mpi_local',mpi_processes=4)
      input.mhd_linear = copy.deepcopy(output.mhd_linear)
      input.mhd_linear.setPulseCtx(idx_in)
      
   
      if itime == 0:
        input.mhd_linear.put(2)
      else:
        input.mhd_linear.putSlice(2)

      print('*************************************')
      print('Output time = ',input.mhd_linear.time[0])
      print('OUTPUT ITIME = ',itime)
      print('Saved mhd_linear mode 1 under oc 2')
      print('*************************************')

  input.close()
  output.close()
  print('Done.')