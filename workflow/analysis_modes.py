# --------------------------------------------
# Analysis componenet for Python EP workflow
# --------------------------------------------


# NEEDED MODULES
import os,imas,sys,pdb,random,copy
from pyal import ALEnv
from lxml import etree
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from datetime import datetime
from workflow.functions_wf import parameters_workflow
from imas import imasdef

def create_shot_dir(shot_nr, run_out):
    # SEPARATE FOLDERS FOR DIFFERENT RUNS/SHOTS
    # create new directory if none exists
    shot_dir = (os.path.join(os.getcwd(), 'workflow/Analysis/'+str(shot_nr)+'_'+str(run_out)))
    shot_dir_check = os.path.isdir(shot_dir)
    if not shot_dir_check:
        os.makedirs(shot_dir)
        print('Shot + run folder: {} was created'.format(shot_dir))
    return shot_dir

# Directly from ligka output (nyquist array) (as saved in the IDS)
def get_nyq_from_mode(mode):
    nyq_m5 = mode.plasma.velocity_perturbed.coordinate1.coefficients_real
    return nyq_m5

def search_nyq(nyq):
    fnyq = {}
    # convert indices to fortran ordering for convenience (same as nyquist in LIGKA)
    for k in range(nyq.shape[0]):
        fnyq[k+1] = nyq[k]
    q_TAE = fnyq[2]
    r_TAE = fnyq[1]
    return q_TAE,r_TAE


def mode_analysis_ligka(val_plot,wf_param_folder):


  def data_structure(mhd_linear_in):
    time_list = []
    s_list = mhd_linear_in.time_slice[0].toroidal_mode[0].plasma.grid.dim1
    data = {}
    data_D = {}
    mode_10 = []
    mode_20 = []
    mode_21 = []
    mode_10_D = []
    mode_20_D = []
    mode_21_D = []
    for itime, time_val in enumerate(mhd_linear_in.time):
      if itime >= itbegin and itime <= itend:
        time_list.append(time_val)
        time_slice = mhd_linear_in.time_slice[itime]
        data[time_val] = {}
        data_D[time_val] = {}
        for imode, mode in enumerate(time_slice.toroidal_mode):
          if mode.n_tor <= n_max and mode.n_tor >= n_min:
            if mode.n_tor not in data[time_val]:
              data[time_val][mode.n_tor] = {}
            if mode.n_tor not in data_D[time_val]:
              data_D[time_val][mode.n_tor] = {}
            if mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
              nyq_m5 = get_nyq_from_mode(mode)
              nyq = nyq_m5[:, 0, 0]
              q_TAE, r_TAE = search_nyq(nyq)
              freq = mode.frequency
              damp = mode.growthrate
              if mode.m_pol_dominant not in data[time_val][mode.n_tor]:
                if r_TAE >= s_min and r_TAE <= s_max:
                  data[time_val][mode.n_tor][mode.m_pol_dominant] = [freq, damp, r_TAE, q_TAE]
                  if mode.n_tor == 10 and mode.m_pol_dominant == 11:
                    
                    mode_10.append(r_TAE)
                  if mode.n_tor == 20 and mode.m_pol_dominant == 21:
              
                    mode_20.append(r_TAE)
                   
                  if mode.n_tor == 20 and mode.m_pol_dominant == 22:
                    
                    mode_21.append(r_TAE) 
                else:
                  data[time_val][mode.n_tor][mode.m_pol_dominant] = [None, None, None, None]
              else:
                if r_TAE >= s_min and r_TAE <= s_max:
                  data_D[time_val][mode.n_tor][mode.m_pol_dominant] = [freq, damp, r_TAE, q_TAE]
                  if mode.n_tor == 10 and mode.m_pol_dominant == 11:
                
                    mode_10_D.append(r_TAE)
                  if mode.n_tor == 20 and mode.m_pol_dominant == 21:
            
                    mode_20_D.append(r_TAE)
                  if mode.n_tor == 20 and mode.m_pol_dominant == 22:
                 
                    mode_21_D.append(r_TAE) 
                else: 
                  data_D[time_val][mode.n_tor][mode.m_pol_dominant] = [None, None, None, None]
    return data ,data_D, time_list

  param = parameters_workflow(wf_param_folder+'/analysis.xml')


  user = param['user']
  version = os.getenv('IMAS_VERSION')[0]
  shot_nr = param['shot_number']
  run_out = param['run']
  machine_out = param['machine']
  n_min = param['n_min']
  n_max = param['n_max']
  s_min = param['r_TAE_min']
  s_max = param['r_TAE_max']
  m_min = param['m_min']
  m_max = param['m_max']
  itbegin = param['itbegin']
  itend = param['itend']
  mode = param['mode']

  # Select which LIGKA MODE to plot:
  if mode == 1:
    occurence = 2
  elif mode == 4:
    occurence = 1
  else:
    occurence = 0

  np.set_printoptions(threshold=sys.maxsize)

  # if val_plot == 5:
  #   profiles_q = imas.ids(shot_nr, run_out, 0, 0)
  #   profiles_q.open_env(user, machine_out, '3')
  #   profiles_q.equilibrium.get()

  #   q_list = []

  #   for itime in range(itbegin, itend + 1):
  #     time_slice = profiles_q.equilibrium.time_slice[itime]
  #     q_list.append(time_slice.profiles_1d.q)

  #   profiles_q.close()

  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,machine_out,shot_nr,run_out,user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)
  shot_dir = create_shot_dir(shot_nr, run_out)
  if param['compare_modes'] == 0:
     # if compare_modes is not selected, only one mode (5, 4 or 1)
    mhd_linear_in = input.get("mhd_linear",occurrence=occurence)
    data,data_D, time_list = data_structure(mhd_linear_in)
  else:
    # load all data (3 IDSs) (this might take a while to complete)
    mhd_linear_in_5 = input.get("mhd_linear",occurrence=0)
    data_5, time_list_5, mode_10 = data_structure(mhd_linear_in_5)
    mhd_linear_in_4 = input.get("mhd_linear",occurrence=1)
    data_4, time_list_4, mode_10 = data_structure(mhd_linear_in_4)
    mhd_linear_in_1 = input.get("mhd_linear",occurrence=2)
    data_1, time_list_1,mode_10 = data_structure(mhd_linear_in_1)


  

  # prepare lists
  # METIS CASES:
  # FREQUENCY, DAMPING, RADIAL POSITION:
  fig, ax = plt.subplots()
  # toroidals = []
  # toroidals_index = []
  # poloidals = []
  # poloidals_index = []
  # for i in data:
  #   for j in data[i]:
  #     n = str('m = '+str(int(j)))
  #     if n not in toroidals:
  #       poloidals.append(n)
  #       poloidals_index.append(j)
  for i in data:
    freq_list = []
    damp_list = []
    r_TAE_list = []
    n_modes=[]
    for j in data[i]:
      n = str('n = '+str(int(j)))
      for k in data[i][j]:
        n_modes.append(j)
        freq_list.append(data[i][j][k][0])
        damp_list.append(data[i][j][k][1])
        r_TAE_list.append(data[i][j][k][2])

    # radial position as a function of time and n:
    if val_plot == 6:
      a = np.empty(len(r_TAE_list))
      a.fill(i)
      r_TAE_list_arr = np.array(r_TAE_list)
      plt.scatter(a, r_TAE_list_arr, c=np.array(n_modes), s= len(n_modes), alpha=1, cmap='viridis')
      
  # if val_plot == 6:
  #   if mode_10:
  #     plt.plot(time_list, mode_10, 'go',label='n=10, m=11')
  #   if mode_20:
  #     plt.plot(time_list,mode_20, 'bo',label='n=20, m=21')
  #   if mode_21:
  #     plt.plot(time_list,mode_21, 'ro',label='n=20, m=22')
  #   plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
  #               mode="expand", borderaxespad=0, ncol=6)
  for i in data_D:
    freq_list = []
    damp_list = []
    r_TAE_list = []
    n_modes=[]
    for j in data_D[i]:
      n = str('n = '+str(int(j)))
      for k in data_D[i][j]:
        n_modes.append(j)
        freq_list.append(data_D[i][j][k][0])
        damp_list.append(data_D[i][j][k][1])
        r_TAE_list.append(data_D[i][j][k][2])

    # radial position as a function of time and n:
    if val_plot == 6:
      a = np.empty(len(r_TAE_list))
      a.fill(i)
      r_TAE_list_arr = np.array(r_TAE_list)
      plt.scatter(a, r_TAE_list_arr, c=np.array(n_modes), s= len(n_modes), alpha=1, cmap='viridis')
      
  # if val_plot == 6:
  #   if mode_10_D:
  #     plt.plot(time_list, mode_10_D, 'go',label='n=10, m=11 secondary')
  #   if mode_20_D:
  #     plt.plot(time_list,mode_20_D, 'bo',label='n=20, m=21 secondary')
  #   if mode_21_D:
  #     plt.plot(time_list,mode_21_D, 'ro',label='n=20, m=22 secondary')
  #   plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
  #               mode="expand", borderaxespad=0, ncol=6)
    
  clb = plt.colorbar()
  clb.ax.set_ylabel('Toroidal Mode Number')
  ax.set(xlabel='Time [s]', ylabel='Radial Position')
  plt.show()
    
  # if val_plot == 1:
  #   ax.set(xlabel='Time [s]', ylabel='Mode Frequency [Hz]',
  #       title='Mode Frequency vs Time')
  #   ax.grid()
  #   # plt.legend(poloidals)
  #   plt.show()

#       print('Plot of Frequency vs time is saved in',str(shot_dir))
#     elif val_plot == 2:
#       ax.set(xlabel='Time [s]', ylabel='Mode Damping',
#           title='Mode Damping vs Time for n = '+str(n))
#       ax.grid()
#       plt.legend(poloidals)
#       fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_n_'+str(n)+'_damp.png')
#       print('Plot of Damping vs Time is saved in',str(shot_dir))
#       plt.show()
#     else:
#       ax.set(xlabel='Time [s]', ylabel='Mode Radial Position',
#           title='Mode Radial Position vs Time for n = '+str(n))
#       ax.grid()
#       plt.legend(poloidals)
#       fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_n_'+str(n)+'_r_TAE.png')
#       print('Plot of Radial Position vs Time is saved in',str(shot_dir))
#       plt.show()

#   if val_plot == 4:
#     # THIS WORKS FOR BOTH METIS AND ASTRA (due to time - independence of the plots)
#     fig, ax = plt.subplots()
#     for itime, time_val in enumerate(input.mhd_linear.time):
#       if itime >= itbegin and itime <= itend:
#         time_slice = input.mhd_linear.time_slice[itime]
#         mpol = []
#         for imode, mode in enumerate(time_slice.toroidal_mode):
#           if mode.n_tor == n:
#             if mode.m_pol_dominant not in mpol and mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
#               mpol.append(mode.m_pol_dominant)
#               nyq_m5 = get_nyq_from_mode(mode)
#               nyq = nyq_m5[:, 0, 0]
#               q_TAE, r_TAE = search_nyq(nyq)
#               if r_TAE >= s_min and r_TAE <= s_max:
#                 poloidals = []
#                 potential = mode.plasma.phi_potential_perturbed.real
#                 m_list = mode.plasma.grid.dim2
#                 for k in m_list:
#                   poloidals.append(str('m = '+str(int(k))))
#                 ax.clear()
#                 ax.plot(s_list, potential)
#                 ax.set(xlabel='s', ylabel='Electrostatic Potential', title='Mode Structure for Time = ' + str(time_val))
#                 ax.grid()
#                 plt.legend(poloidals)
#                 fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_n_'+str(n)+'_m_'+str(mode.m_pol_dominant)+'_t_'+str(time_val)+'_structure.png')
#                 #plt.show()
#               else:
#                 print('For time ',time_val,' m = ',mode.m_pol_dominant,' no mode was found between r = ',s_min,' and ',s_max)

#   # ASTRA CASES (or when choosing 1 timepoint from METIS)              
#   if itend - itbegin == 0:
#     ntor = {}
#     time_slice = input.mhd_linear.time_slice[0]
#     for imode, mode in enumerate(time_slice.toroidal_mode):
#       if mode.n_tor not in ntor:
#         ntor[mode.n_tor] = {}
#         if mode.m_pol_dominant == mode.n_tor:
#           if mode.m_pol_dominant not in ntor[mode.n_tor] and mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
#             nyq_m5 = get_nyq_from_mode(mode)
#             nyq = nyq_m5[:, 0, 0]
#             q_TAE, r_TAE = search_nyq(nyq)
#             freq = mode.frequency
#             damp = mode.growthrate
#             if r_TAE >= s_min and r_TAE <= s_max:
#               ntor[mode.n_tor][mode.m_pol_dominant] = [freq, damp, r_TAE, q_TAE]
#             else:
#               print('For n = ',mode.n_tor,' m = ',mode.m_pol_dominant,' no mode was found between r = ',s_min,' and ',s_max)
#               ntor[mode.n_tor][mode.m_pol_dominant] = [None, None, None, None]

#     # FREQUENCY, DAMPING, RADIAL POSITION:
#     if val_plot == 1 or val_plot == 2 or val_plot == 3:
#       fig, ax = plt.subplots()
#       poloidals = []
#       poloidals_index = []
#       n_list = []
#       for i in ntor:
#         # n_list.append(i)
#         for j in ntor[i]:
#           m = str('m = '+str(int(j)))
#           if m not in poloidals:
#             poloidals.append(m)
#             poloidals_index.append(j)
#       freq_list = []
#       damp_list = []
#       r_TAE_list = []
#       for j in poloidals_index:
#         # freq_list = []
#         # damp_list = []
#         # r_TAE_list = []
#         for i in ntor:
#           # if j not in ntor[i]:
#           #   freq_list.append(None)
#           #   damp_list.append(None)
#           #   r_TAE_list.append(None)
#           # else:
#           if j in ntor[i]:
#             n_list.append(i)
#             freq_list.append(ntor[i][j][0])
#             damp_list.append(ntor[i][j][1])
#             r_TAE_list.append(ntor[i][j][2])
#       print(freq_list)
#       if val_plot == 1:
#         ax.plot(n_list, freq_list)
#       elif val_plot == 2:
#         ax.plot(n_list, damp_list)
#       else:
#         ax.plot(n_list, r_TAE_list)
    
#     if val_plot == 1:
#       ax.set(xlabel='Toroidal Mode Number', ylabel='Mode Frequency [Hz]',
#           title='Mode Frequency vs Toroidal Mode Number')
#       ax.grid()
#       plt.legend(poloidals)
#       fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_freq_1time.png')
#       plt.show()
#       print('Plot of Frequency vs n is saved in',str(shot_dir))
#     elif val_plot == 2:
#       ax.set(xlabel='Toroidal Mode Number', ylabel='Mode Damping',
#           title='Mode Damping vs Toroidal Mode Number')
#       ax.grid()
#       plt.legend(poloidals)
#       fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_damp_1time.png')
#       print('Plot of Damping vs Toroidal Mode Number is saved in',str(shot_dir))
#       plt.show()
#     else:
#       ax.set(xlabel='Toroidal Mode Number', ylabel='Mode Radial Position',
#           title='Mode Radial Position vs Toroidal Mode Number')
#       ax.grid()
#       plt.legend(poloidals)
#       fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_r_TAE_1time.png')
#       print('Plot of Radial Position vs Toroidal Mode Number is saved in',str(shot_dir))
#       plt.show()



def export_data(wf_param_folder):
  param = parameters_workflow(wf_param_folder+'/analysis.xml')


  user = param['user']
  version = os.getenv('IMAS_VERSION')[0]
  shot_nr = param['shot_number']
  run_out = param['run']
  machine_out = param['machine']
  n_min = param['n_min']
  n_max = param['n_max']
  s_min = param['r_TAE_min']
  s_max = param['r_TAE_max']
  m_min = param['m_min']
  m_max = param['m_max']
  itbegin = param['itbegin']
  itend = param['itend']
  mode = param['mode']

  if mode == 1:
      occurence = 2
  elif mode == 4:
      occurence = 1
  else:
      occurence = 0                  


  now = datetime.now()
  date_time = now.strftime("%m%d%Y_%H_%M_%S")
  filename = (os.path.join(os.getcwd(), 'workflow/Analysis/exported_'+str(shot_nr)+'_'+str(run_out)+'_'+str(date_time)+'.txt'))
  f = open(filename, 'w+')

  f.write(str(user)+" "+str(shot_nr)+" "+str(run_out)+" "+str(machine_out)+" "+str(occurence) + "\n")

  input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,machine_out,shot_nr,run_out,user)
  status,_ = input.open()
  if status!=0:
      print("Can't open the selected dataset!", file=sys.stderr)
      sys.exit(1)
  shot_dir = create_shot_dir(shot_nr, run_out)
   
  mhd_linear_in = input.get("mhd_linear",occurrence=occurence)

  for itime, time_val in enumerate(mhd_linear_in.time):
    if itime >= itbegin and itime <= itend:
      time_slice = mhd_linear_in.time_slice[itime]
      for imode, mode in enumerate(time_slice.toroidal_mode):
        if mode.n_tor <= n_max and mode.n_tor >= n_min:
          if mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
            nyq_m5 = get_nyq_from_mode(mode)
            nyq = nyq_m5[:, 0, 0]
            q_TAE, r_TAE = search_nyq(nyq)
            if r_TAE >= s_min and r_TAE <= s_max:
              f.write(str(time_val) + " " + str(itime) + " ")
              f.write(" ".join(map(str, nyq))+"\n")
            

# TODO: CHECK THE FORMATTING OF THE FILE BEING SAVED


  f.close()
  print('Done, file is saved in Analysis folder')


