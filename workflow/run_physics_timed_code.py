# --------------------------------------------
# PYTHON WRAPPER TO CALL HELENA+LIGKA
# --------------------------------------------

# HCD
shot    = 100001
run_in  = 1
run_out = 11
user_in = 'public'
tokamakname = 'ITER'
tokamakname_out = 'helena_test_loop'

# MHD
#shot    = 130011
#run_in  = 1
#run_out = 31

# NEEDED MODULES
import os,imas,sys,pdb

# IMPORT MODULE(S) FOR SPECIFIC PHYSICS CODE(S)
actor_path = os.path.join(os.getenv('KEPLER'), 'imas/src/org/iter/imas/python')
list_of_actors = ['helena_imas','ligka']
for name in list_of_actors:
  sys.path[:0] = [os.path.join(actor_path,name)]
  globals()[name] = getattr(__import__(name), name)

# LOCAL DATABASE ENVIRONMENT
user = os.getenv('USER')
version = os.getenv('IMAS_VERSION')[0]

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
idx_in= input.core_profiles.getPulseCtx()
# OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
print('=> Create output datafile')
output = imas.ids(shot,run_out,0,0)

# CREATE OUTPUT DATAFILE
output.create_env(user,tokamakname_out,version)
idx_out = output.mhd_linear.getPulseCtx()


#ntime = 1
#iftime = 53
#ntime = 107;

for itime in range(55,57):

    #iftime = itime

    # EXECUTE PHYSICS CODE
    print('Time = ',time[itime],' s, itime = ',itime,'/',ntime)
    input.equilibrium.setPulseCtx(idx_in)
    input.equilibrium.getSlice(time[itime],1)
    input.core_profiles.setPulseCtx(idx_in)
    input.core_profiles.getSlice(time[itime],1)
    #try:
    output.equilibrium = helena_imas(input.equilibrium)
    print('FINISHED HELENA ---------- STARTING LIGKA')
    
    #output.mhd_linear.time[0] = time[itime]
    output.mhd_linear = ligka(output.equilibrium,input.core_profiles,output.mhd_linear,'input/z_ligka.xml')

   
    if itime == 0:
      output.mhd_linear.put()
    else:
      output.mhd_linear.putSlice()


    #output.equilibrium.time[0] = time[itime]
    #print(input.equilibrium.time_slice[0].profiles_2d[0].grid_type.index)
    #print(output.equilibrium.time_slice[0].profiles_2d[0].grid_type.index)
    #pdb.set_trace()
    print('*************************************')
    print('Output time = ',output.mhd_linear.time[0])
    print('*************************************')
    #except:
    #    print('!!!! Equilibrium calculation failed !!!!')
    #    break

input.close()
output.close()
print('Done.')



