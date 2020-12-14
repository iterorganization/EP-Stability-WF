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
# from scipy.interpolate import sproot, splrep
from workflow.functions_wf import parameters_workflow


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


# def find_rationals_n(ntor, q_sgrid, q_data, mlist=None, half_rationals = False):
#     tck     = splrep(q_sgrid, q_data, k=3, s=0)
#     qmin    = np.min(q_data)
#     qmax    = np.max(q_data)
#     result  = {}
#     qdiff = 0 + half_rationals * 0.5
#     for m in [i for i in range(np.floor(ntor*qmin).astype(np.int)-1, np.ceil(ntor*qmax).astype(np.int)+1) if (i+qdiff)>=ntor*qmin and (i+qdiff)<=ntor*qmax]:
#         if mlist is not None:
#             if m not in mlist:
#                 continue
#         q = (m+qdiff)/ntor
#         tck_mod = (tck[0], tck[1]-q, tck[2])
#         result[m] = sproot(tck_mod)
#     return result

def mode_analysis_ligka(val_plot):

  param = parameters_workflow('workflow/input/analysis.xml')


  user = param['user']
  version = os.getenv('IMAS_VERSION')[0]
  shot_nr = param['shot_number']
  run_out = param['run']
  machine_out = param['machine']
  n = param['n']
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

  if val_plot == 5:
    profiles_q = imas.ids(shot_nr, run_out, 0, 0)
    profiles_q.open_env(user, machine_out, '3')
    profiles_q.equilibrium.get()

    q_list = []

    for itime in range(itbegin, itend + 1):
      time_slice = profiles_q.equilibrium.time_slice[itime]
      q_list.append(time_slice.profiles_1d.q)

    profiles_q.close()

  input = imas.ids(shot_nr, run_out, 0, 0)
  input.open_env(user, machine_out, '3')
  input.mhd_linear.get(occurence)

  shot_dir = create_shot_dir(shot_nr, run_out)
  ntime = len(input.mhd_linear.time)

  
  time_list = []
  s_list = input.mhd_linear.time_slice[0].toroidal_mode[0].plasma.grid.dim1
  if itend - itbegin > 0: # IF NOT ASTRA SHOT (or analysis of 1 timepoint only)
    if val_plot == 1 or val_plot == 2 or val_plot == 3:
      mpol = {}
      for itime, time_val in enumerate(input.mhd_linear.time):
        if itime >= itbegin and itime <= itend:
          time_slice = input.mhd_linear.time_slice[itime]
          mpol[time_val] = {}
          for imode, mode in enumerate(time_slice.toroidal_mode):
            if mode.n_tor == n:
              if mode.m_pol_dominant not in mpol[time_val] and mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
                nyq_m5 = get_nyq_from_mode(mode)
                nyq = nyq_m5[:, 0, 0]
                q_TAE, r_TAE = search_nyq(nyq)
                freq = mode.frequency
                damp = mode.growthrate
                if r_TAE >= s_min and r_TAE <= s_max:
                  mpol[time_val][mode.m_pol_dominant] = [freq, damp, r_TAE, q_TAE]
                else:
                  print('For time ',time_val,' m = ',mode.m_pol_dominant,' no mode was found between r = ',s_min,' and ',s_max)
                  mpol[time_val][mode.m_pol_dominant] = [None, None, None, None]
                
  # prepare lists
  # METIS CASES:
  # FREQUENCY, DAMPING, RADIAL POSITION:
    if val_plot == 1 or val_plot == 2 or val_plot == 3:
      fig, ax = plt.subplots()
      poloidals = []
      poloidals_index = []
      time_list = []
      for i in mpol:
        time_list.append(i)
        for j in mpol[i]:
          m = str('m = '+str(int(j)))
          if m not in poloidals:
            poloidals.append(m)
            poloidals_index.append(j)

      for j in poloidals_index:
        freq_list = []
        damp_list = []
        r_TAE_list = []
        for i in mpol:
          if j not in mpol[i]:
            freq_list.append(None)
            damp_list.append(None)
            r_TAE_list.append(None)
          else:
            freq_list.append(mpol[i][j][0])
            damp_list.append(mpol[i][j][1])
            r_TAE_list.append(mpol[i][j][2])

        if val_plot == 1:
          ax.plot(time_list, freq_list)
        elif val_plot == 2:
          ax.plot(time_list, damp_list)
        else:
          ax.plot(time_list, r_TAE_list)
    
    if val_plot == 1:
      ax.set(xlabel='Time [s]', ylabel='Mode Frequency [Hz]',
          title='Mode Frequency vs Time for n = '+str(n))
      ax.grid()
      plt.legend(poloidals)
      fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_n_'+str(n)+'_freq_.png')
      plt.show()
      print('Plot of Frequency vs time is saved in',str(shot_dir))
    elif val_plot == 2:
      ax.set(xlabel='Time [s]', ylabel='Mode Damping',
          title='Mode Damping vs Time for n = '+str(n))
      ax.grid()
      plt.legend(poloidals)
      fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_n_'+str(n)+'_damp.png')
      print('Plot of Damping vs Time is saved in',str(shot_dir))
      plt.show()
    else:
      ax.set(xlabel='Time [s]', ylabel='Mode Radial Position',
          title='Mode Radial Position vs Time for n = '+str(n))
      ax.grid()
      plt.legend(poloidals)
      fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_n_'+str(n)+'_r_TAE.png')
      print('Plot of Radial Position vs Time is saved in',str(shot_dir))
      plt.show()

  if val_plot == 4:
    # THIS WORKS FOR BOTH METIS AND ASTRA (due to time - independence of the plots)
    fig, ax = plt.subplots()
    for itime, time_val in enumerate(input.mhd_linear.time):
      if itime >= itbegin and itime <= itend:
        time_slice = input.mhd_linear.time_slice[itime]
        mpol = []
        for imode, mode in enumerate(time_slice.toroidal_mode):
          if mode.n_tor == n:
            if mode.m_pol_dominant not in mpol and mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
              mpol.append(mode.m_pol_dominant)
              nyq_m5 = get_nyq_from_mode(mode)
              nyq = nyq_m5[:, 0, 0]
              q_TAE, r_TAE = search_nyq(nyq)
              if r_TAE >= s_min and r_TAE <= s_max:
                poloidals = []
                potential = mode.plasma.phi_potential_perturbed.real
                m_list = mode.plasma.grid.dim2
                for k in m_list:
                  poloidals.append(str('m = '+str(int(k))))
                ax.clear()
                ax.plot(s_list, potential)
                ax.set(xlabel='s', ylabel='Electrostatic Potential', title='Mode Structure for Time = ' + str(time_val))
                ax.grid()
                plt.legend(poloidals)
                fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_n_'+str(n)+'_m_'+str(mode.m_pol_dominant)+'_t_'+str(time_val)+'_structure.png')
                #plt.show()
              else:
                print('For time ',time_val,' m = ',mode.m_pol_dominant,' no mode was found between r = ',s_min,' and ',s_max)

  # ASTRA CASES (or when choosing 1 timepoint from METIS)              
  if itend - itbegin == 0:
    ntor = {}
    time_slice = input.mhd_linear.time_slice[0]
    for imode, mode in enumerate(time_slice.toroidal_mode):
      if mode.n_tor not in ntor:
        ntor[mode.n_tor] = {}
        if mode.m_pol_dominant == mode.n_tor:
          if mode.m_pol_dominant not in ntor[mode.n_tor] and mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
            nyq_m5 = get_nyq_from_mode(mode)
            nyq = nyq_m5[:, 0, 0]
            q_TAE, r_TAE = search_nyq(nyq)
            freq = mode.frequency
            damp = mode.growthrate
            if r_TAE >= s_min and r_TAE <= s_max:
              ntor[mode.n_tor][mode.m_pol_dominant] = [freq, damp, r_TAE, q_TAE]
            else:
              print('For n = ',mode.n_tor,' m = ',mode.m_pol_dominant,' no mode was found between r = ',s_min,' and ',s_max)
              ntor[mode.n_tor][mode.m_pol_dominant] = [None, None, None, None]

    # FREQUENCY, DAMPING, RADIAL POSITION:
    if val_plot == 1 or val_plot == 2 or val_plot == 3:
      fig, ax = plt.subplots()
      poloidals = []
      poloidals_index = []
      n_list = []
      for i in ntor:
        # n_list.append(i)
        for j in ntor[i]:
          m = str('m = '+str(int(j)))
          if m not in poloidals:
            poloidals.append(m)
            poloidals_index.append(j)
      freq_list = []
      damp_list = []
      r_TAE_list = []
      for j in poloidals_index:
        # freq_list = []
        # damp_list = []
        # r_TAE_list = []
        for i in ntor:
          # if j not in ntor[i]:
          #   freq_list.append(None)
          #   damp_list.append(None)
          #   r_TAE_list.append(None)
          # else:
          if j in ntor[i]:
            n_list.append(i)
            freq_list.append(ntor[i][j][0])
            damp_list.append(ntor[i][j][1])
            r_TAE_list.append(ntor[i][j][2])
      print(freq_list)
      if val_plot == 1:
        ax.plot(n_list, freq_list)
      elif val_plot == 2:
        ax.plot(n_list, damp_list)
      else:
        ax.plot(n_list, r_TAE_list)
    
    if val_plot == 1:
      ax.set(xlabel='Toroidal Mode Number', ylabel='Mode Frequency [Hz]',
          title='Mode Frequency vs Toroidal Mode Number')
      ax.grid()
      plt.legend(poloidals)
      fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_freq_1time.png')
      plt.show()
      print('Plot of Frequency vs n is saved in',str(shot_dir))
    elif val_plot == 2:
      ax.set(xlabel='Toroidal Mode Number', ylabel='Mode Damping',
          title='Mode Damping vs Toroidal Mode Number')
      ax.grid()
      plt.legend(poloidals)
      fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_damp_1time.png')
      print('Plot of Damping vs Toroidal Mode Number is saved in',str(shot_dir))
      plt.show()
    else:
      ax.set(xlabel='Toroidal Mode Number', ylabel='Mode Radial Position',
          title='Mode Radial Position vs Toroidal Mode Number')
      ax.grid()
      plt.legend(poloidals)
      fig.savefig(str(shot_dir)+'/'+str(shot_nr)+'_'+str(run_out)+'_r_TAE_1time.png')
      print('Plot of Radial Position vs Toroidal Mode Number is saved in',str(shot_dir))
      plt.show()
