import os, imas, sys, pdb, random, copy
from lxml import etree
import xml.etree.ElementTree as ET

# IMPORT PARAMETERS FROM WORKFLOW AND LIGKA XML --------------------------------------
def parameters_workflow(input_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    param = {}

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
    
# WF RUNNING FUNCTIONS
def read_timestep(user, database, run):
    param = parameters_workflow('workflow/input/input_workflow.xml')
    print('=> Open input datafile and read total equilibrium IDS for timesteps.')
    input_total = imas.ids(param['shot_nr'], run, 0, 0)
    input_total.open_env(user, database, '3')
    time = input_total.equilibrium.partialGet('time')
    ntime = len(time)
    input_total.close()
    return(time, ntime)
