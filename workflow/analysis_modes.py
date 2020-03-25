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

#SETTINGS:
tokamakname = 'ligka_modes'
user = os.getenv('USER')
version = os.getenv('IMAS_VERSION')[0]
shot    = 130012
run  = 5

print('===Open DB and read the mhd_linear input===')

input = imas.ids(shot,run,0,0)
input.open_env(user,tokamakname,'3')
#idx_in = input.mhd_linear.getPulseCtx()
input.mhd_linear.get()
# LISTS WITH DATA DECLARATION AND FILLING:

freq = []
radius = []
radius.append(input.mhd_linear.time_slice[1].toroidal_mode[0].plasma.grid.dim1)
np.set_printoptions(threshold=sys.maxsize)

for i in range(len(input.mhd_linear.time)):
  for j in range(len(input.mhd_linear.time_slice[0].toroidal_mode)):
    freq.append(input.mhd_linear.time_slice[i].toroidal_mode[j].plasma.phi_potential_perturbed.real)
  
    # plotting the points  
    plt.plot(radius[0], freq[0]) 
  
    # naming the x axis 
    plt.xlabel('x - radius') 
    # naming the y axis 
    plt.ylabel('y - freq') 
  
    # giving a title to my graph 
    plt.title('test_'+str(input.mhd_linear.time[i])) 
  
    # function to show the plot 
    plt.savefig('EF_ANA_n'+str(input.mhd_linear.time_slice[i].toroidal_mode[j].n_tor)+'_'+str(input.mhd_linear.time[i])+'.png') 
input.close()



