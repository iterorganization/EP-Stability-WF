# --------------------------------------------
# Analysis componenet for Python EP workflow
# --------------------------------------------


# NEEDED MODULES
import os,imas,sys,pdb,random,copy
from pyal import ALEnv
from lxml import etree
import numpy as np
from scipy.stats import norm
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from datetime import datetime


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

  param = parameters_workflow('workflow/input/input_workflow.xml',0)
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
    for j in range(param_ligka['max_n_tor']-param_ligka['min_n_tor']+1):

      freq = input.mhd_linear.time_slice[i].toroidal_mode[j].plasma.phi_potential_perturbed.real
      
      if len(freq) == 0:
        print('List for timepoint '+str(input.mhd_linear.time[i])+' is empty, skipping this timepoint.')
        continue
    
      # plotting the points  
      plt.figure()

      plt.plot(radius, freq) 
      
    
      # naming the x axis 
      plt.axis([0.55,0.85,0,1])
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

  param = parameters_workflow('workflow/input/input_workflow.xml',0)
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

  param = parameters_workflow('workflow/input/input_workflow.xml',0)
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


