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


def analysis_ligka_mode5():

  # IMPORT PARAMETERS FROM WORKFLOW AND LIGKA XML --------------------------------------
  def parameters_workflow(input_file,l):  
    tree = ET.parse(input_file)
    root = tree.getroot()

    param = {}
    param_ligka = {} 
    
    if l != 1:
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

          param['input_path'] = input_file
          print(elem.tag, ' = ', param[elem.tag])
      return(param)
    else:
      print('----- LIGKA PARAMETERS ----')

      for elem in root.iter():
        if len(elem) == 0:
          try:
            param_ligka[elem.tag] = int(elem.text)
          except:
            try:
              param_ligka[elem.tag] = float(elem.text)
            except:
              param_ligka[elem.tag] = elem.text

          param_ligka['input_path'] = input_file
          print(elem.tag, ' = ', param_ligka[elem.tag])
      return(param_ligka)

  param = parameters_workflow('workflow/input/input_workflow_default.xml',0)
  param_ligka = parameters_workflow('workflow/input/z_ligka.xml',1)
  
  #CREATE DIRECTORY IF IS NOT THERE:
  analysis_mode5 = os.path.join(os.getcwd(), 'workflow/Analysis/Ligka_mode5_'+datetime.now().strftime('%d%m_%H%M%S'))
  os.makedirs(analysis_mode5)
  
  #SETTINGS:
  user = os.getenv('USER')
  version = os.getenv('IMAS_VERSION')[0]


  print('===Open DB and read the mhd_linear input===')

  input = imas.ids(param['shot_nr'],param['run_out'],0,0)
  input.open_env(user,param['machine_out'],'3')
  input.mhd_linear.get()
  
  # LISTS WITH DATA DECLARATION AND FILLING:

  radius = input.mhd_linear.time_slice[0].toroidal_mode[0].plasma.grid.dim1
  np.set_printoptions(threshold=sys.maxsize)
  
  
  for i in range(len(input.mhd_linear.time)):
    for j in range(0, 414+1):

      freq = input.mhd_linear.time_slice[i].toroidal_mode[j].plasma.phi_potential_perturbed.real
      
      if len(freq) == 0:
        print('List for timepoint '+str(input.mhd_linear.time[i])+' is empty, skipping this timepoint.')
        continue
    
      # plotting the points  
      plt.figure()

      plt.plot(radius, freq) 
      
    
      # naming the x axis 
      #plt.axis([0.55,0.85,0,1])
      # naming the x axis 
      plt.xlabel('s') 
      
      # naming the y axis 
      plt.ylabel('Electrostatic Potential') 
    
      # giving a title to my graph 
      plt.title('EF_ANA_n'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].n_tor)+'_'+str(input.mhd_linear.time[i]))  
      
      

      # function to save/show the plot 
      plt.savefig(str(analysis_mode5)+'/EF_ANA_n'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].n_tor)+'_m'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].m_pol_dominant)+'_'+str(input.mhd_linear.time[i])+'.png')
      
      print('Analysis for timepoint '+str(input.mhd_linear.time[i])+' data was saved in:',str(analysis_mode5))
  input.close()
  print('Done')
  

def analysis_ligka_mode1():

  # IMPORT PARAMETERS FROM WORKFLOW AND LIGKA XML --------------------------------------
  def parameters_workflow(input_file,l):  
    tree = ET.parse(input_file)
    root = tree.getroot()

    param = {}
    param_ligka = {} 
    
    if l != 1:
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

          param['input_path'] = input_file
          print(elem.tag, ' = ', param[elem.tag])
      return(param)
    else:
      print('----- LIGKA PARAMETERS ----')

      for elem in root.iter():
        if len(elem) == 0:
          try:
            param_ligka[elem.tag] = int(elem.text)
          except:
            try:
              param_ligka[elem.tag] = float(elem.text)
            except:
              param_ligka[elem.tag] = elem.text

          param_ligka['input_path'] = input_file
          print(elem.tag, ' = ', param_ligka[elem.tag])
      return(param_ligka)

  param = parameters_workflow('workflow/input/input_workflow_default.xml',0)
  param_ligka = parameters_workflow('workflow/input/z_ligka.xml',1)
  
  #CREATE DIRECTORY IF IS NOT THERE:
  analysis_mode1 = os.path.join(os.getcwd(), 'workflow/Analysis/Ligka_mode1_'+datetime.now().strftime('%d%m_%H%M%S'))
  os.makedirs(analysis_mode1)
  
  #SETTINGS:
  user = os.getenv('USER')
  version = os.getenv('IMAS_VERSION')[0]


  print('===Open DB and read the mhd_linear input===')

  input = imas.ids(param['shot_nr'],param['run_out'],0,0)
  input.open_env(user,param['machine_out'],'3')
  input.mhd_linear.get(2)
  
  # LISTS WITH DATA DECLARATION AND FILLING:

  
  radius = input.mhd_linear.time_slice[1].toroidal_mode[0].plasma.grid.dim1
  print(len(radius))
  np.set_printoptions(threshold=sys.maxsize)
  
  
  for i in range(len(input.mhd_linear.time)):
    for j in range(param_ligka['max_n_tor']-param_ligka['min_n_tor']+1):

      freq = input.mhd_linear.time_slice[i].toroidal_mode[j].plasma.phi_potential_perturbed.real
      #freq_list = []
      if len(freq) == 0:
        print('List for timepoint '+str(input.mhd_linear.time[i])+' is empty, skipping this timepoint.')
        continue
      #for pos in freq:
        #freq_list.append(pos[1])
      print(len(freq)) 
      # plotting the points  
      plt.figure()
      #plt.plot(radius, freq_list) 
      plt.plot(radius, freq)
      
      #plt.axis([0,2,-10,20])
    
      # naming the x axis 
      plt.xlabel('s') 
      
      # naming the y axis 
      plt.ylabel('Electrostatic Potential')  
    
      # giving a title to my graph 
      plt.title('EF_phi_n'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].n_tor)+'_'+str(input.mhd_linear.time[i]))  
      

      # function to save/show the plot 
      plt.savefig(str(analysis_mode1)+'/EF_PHI_n'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].n_tor)+'_m'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].m_pol_dominant)+'_'+str(input.mhd_linear.time[i])+'.png')
      
      print('Analysis for timepoint '+str(input.mhd_linear.time[i])+' data was saved in:',str(analysis_mode1))
  input.close()
  print('Done')
  
def analysis_ligka_mode2():

  # IMPORT PARAMETERS FROM WORKFLOW AND LIGKA XML --------------------------------------
  def parameters_workflow(input_file,l):  
    tree = ET.parse(input_file)
    root = tree.getroot()

    param = {}
    param_ligka = {} 
    
    if l != 1:
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

          param['input_path'] = input_file
          print(elem.tag, ' = ', param[elem.tag])
      return(param)
    else:
      print('----- LIGKA PARAMETERS ----')

      for elem in root.iter():
        if len(elem) == 0:
          try:
            param_ligka[elem.tag] = int(elem.text)
          except:
            try:
              param_ligka[elem.tag] = float(elem.text)
            except:
              param_ligka[elem.tag] = elem.text

          param_ligka['input_path'] = input_file
          print(elem.tag, ' = ', param_ligka[elem.tag])
      return(param_ligka)

  param = parameters_workflow('workflow/input/input_workflow_default.xml',0)
  param_ligka = parameters_workflow('workflow/input/z_ligka.xml',1)
  
  #CREATE DIRECTORY IF IS NOT THERE:
  analysis_mode2 = os.path.join(os.getcwd(), 'workflow/Analysis/Ligka_mode2_'+datetime.now().strftime('%d%m_%H%M%S'))
  os.makedirs(analysis_mode2)
  
  #SETTINGS:
  user = os.getenv('USER')
  version = os.getenv('IMAS_VERSION')[0]


  print('===Open DB and read the mhd_linear input===')

  input = imas.ids(param['shot_nr'],param['run_out'],0,0)
  input.open_env(user,param['machine_out'],'3')
  input.mhd_linear.get(3)
  
  # LISTS WITH DATA DECLARATION AND FILLING:

  
  radius = input.mhd_linear.time_slice[1].toroidal_mode[0].plasma.grid.dim1
  print(len(radius))
  np.set_printoptions(threshold=sys.maxsize)
  
  
  for i in range(len(input.mhd_linear.time)):
    for j in range(param_ligka['max_n_tor']-param_ligka['min_n_tor']+1):

      freq = input.mhd_linear.time_slice[i].toroidal_mode[j].plasma.phi_potential_perturbed.real
      freq_list = []
      if len(freq) == 0:
        print('List for timepoint '+str(input.mhd_linear.time[i])+' is empty, skipping this timepoint.')
        continue
      #for pos in freq:
        #freq_list.append(pos[1])
      print(len(freq)) 
      # plotting the points  
      plt.figure()
      #plt.plot(radius, freq_list) 
      plt.plot(radius, freq)
      
      #plt.axis([0,2,-10,20])
    
      # naming the x axis 
      plt.xlabel('s') 
      
      # naming the y axis 
      plt.ylabel('Electrostatic Potential') 
    
      # giving a title to my graph 
      plt.title('EF_phi_n'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].n_tor)+'_'+str(input.mhd_linear.time[i])) 
      
      

      # function to save/show the plot 
      plt.savefig(str(analysis_mode2)+'/EF_PHI_n'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].n_tor)+'_m'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].m_pol_dominant)+'_'+str(input.mhd_linear.time[i])+'.png')
      
      print('Analysis for timepoint '+str(input.mhd_linear.time[i])+' data was saved in:',str(analysis_mode2))
  input.close()
  print('Done')


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
    #w_TAE = fnyq[16]
    return q_TAE,r_TAE

def mode_analysis_ligka(val_plot):

  param = parameters_workflow('workflow/input/analysis.xml')


  user = param['user']
  version = os.getenv('IMAS_VERSION')[0]
  shot_nr = param['shot_number']
  run_out = param['run']
  machine_out = param['machine']
  n = param['n']
  mode = param['mode']

  if mode == 1:
    occurence = 2
  elif mode == 4:
    occurence = 1
  else:
    occurence = 0
  np.set_printoptions(threshold=sys.maxsize)



  input = imas.ids(shot_nr, run_out, 0, 0)
  input.open_env(user, machine_out, '3')
  input.mhd_linear.get(occurence)

  shot_dir = create_shot_dir(shot_nr, run_out)
  ntime = len(input.mhd_linear.time)

  time_list = []
  mpol_check = []
  
  # check how many poloidals we have
  for itime, time_val in enumerate(input.mhd_linear.time):
    time_slice = input.mhd_linear.time_slice[itime]
    for imode, mode in enumerate(time_slice.toroidal_mode):
      if mode.n_tor == n:
        if mode.m_pol_dominant not in mpol_check:
        #if mode.n_tor == n:
          mpol_check.append(mode.m_pol_dominant)

  freq = [[None] * ntime for i in range(len(mpol_check))]
  damp = [[None] * ntime for i in range(len(mpol_check))]
  q_TAE = [[None] * ntime for i in range(len(mpol_check))]
  r_TAE = [[None] * ntime for i in range(len(mpol_check))]

  for itime, time_val in enumerate(input.mhd_linear.time):
    time_slice = input.mhd_linear.time_slice[itime]
    time_list.append(time_val)
    mpol = []
    i = 0
    for imode, mode in enumerate(time_slice.toroidal_mode):
      if mode.n_tor == n:
        if mode.m_pol_dominant not in mpol:
          mpol.append(mode.m_pol_dominant)
          nyq_m5 = get_nyq_from_mode(mode)
          nyq = nyq_m5[:, 0, 0]
          q_TAE[i][itime], r_TAE[i][itime] = search_nyq(nyq)
          freq[i][itime] = mode.frequency
          damp[i][itime] = mode.growthrate
          i = i + 1

  fig, ax = plt.subplots()

  poloidals = []
  for i in mpol_check:
    poloidals.append(str('m = '+str(int(i))))
  for i in range(len(mpol_check)):
    if val_plot == 1:
      ax.plot(time_list, freq[i])
    elif val_plot == 2:
      ax.plot(time_list, damp[i])
    else:
      ax.plot(time_list, r_TAE[i])
  
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


