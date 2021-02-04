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
def read_timestep(user, database, run, current_config_folder):
    param = parameters_workflow(current_config_folder + '/input_workflow_default.xml')
    print('=> Open input datafile and read total equilibrium IDS for timesteps.')
    input_total = imas.ids(param['shot_nr'], run, 0, 0)
    input_total.open_env(user, database, '3')
    time = input_total.equilibrium.partialGet('time')
    ntime = len(time)
    input_total.close()
    return(time, ntime)

def profiles_get(param):
    print('=> Open input datafile and read the numer of species and other neccesary inputs for LIGKA')
    input_species = imas.ids(param['shot_nr'], param['run_in'], 0, 0)
    input_species.open_env(param['user'], param['machine'], '3')
    core_profiles = input_species.core_profiles
    time = core_profiles.partialGet('time')
    ntime = len(time)

    core_profiles.profiles_1d.resize(1)
    if ntime > 1: #if NOT ASTRA shot
      core_profiles.profiles_1d[0] = input_species.core_profiles.partialGet('profiles_1d('+str(int(time[1]))+')')
    else:
      input_species.core_profiles.get()
    nspecies = len(core_profiles.profiles_1d[0].ion)

    species = []
    for ispecies in range(nspecies):
      species.append(core_profiles.profiles_1d[0].ion[ispecies].label)
    volume = core_profiles.profiles_1d[0].grid.volume
    ntot = 0
    species_density = [0] * nspecies
    for ispecies in range(nspecies):
        species_density[ispecies] = sum(volume*core_profiles.profiles_1d[0].ion[ispecies].density)
        ntot = ntot + species_density[ispecies]

    ne = sum(volume*core_profiles.profiles_1d[0].electrons.density)

    nspec_over_ntot = species_density/ntot
    nspec_over_ne   = species_density/ne

    for ispecies in range(nspecies):
      for jspecies in range(nspecies):
          if (species[jspecies] == species[ispecies]) & (jspecies != ispecies):
              nspec_over_ntot[ispecies] = nspec_over_ntot[ispecies] + nspec_over_ntot[jspecies]
              nspec_over_ntot[jspecies] = 0
              nspec_over_ne[ispecies] = nspec_over_ne[ispecies] + nspec_over_ne[jspecies]
              nspec_over_ne[jspecies] = 0
    
    curr_str = 'el'
    nspec = 1
    nback = 1
    nhot = 0

    for ispecies in range(nspecies):
      if nspec_over_ntot[ispecies] > 0. and nspec_over_ne[ispecies] > 0.:
        print('For ion name: ',species[ispecies])
        print('Density over total: ', format('%.10f' % nspec_over_ntot[ispecies]))
        print('Density over electron density: ', format('%.10f' % nspec_over_ne[ispecies]))
        # ALL THERMAL PARTICLES:
        if species[ispecies] == 'H' or species[ispecies] == 'H+':
          if nspec_over_ntot[ispecies] > 2E-2:
            curr_str = curr_str + 'hh'
            nspec = nspec + 1
            nback = nback + 1
        if species[ispecies] == 'D'  or species[ispecies] == 'D+':
          if nspec_over_ntot[ispecies] > 2E-2:
            curr_str = curr_str + 'dd'
            nspec = nspec + 1
            nback = nback + 1
        if species[ispecies] == 'T'  or species[ispecies] == 'T+':
          if nspec_over_ntot[ispecies] > 2E-2:
            curr_str = curr_str + 'tt'
            nspec = nspec + 1
            nback = nback + 1
        if species[ispecies] == 'He3'  or species[ispecies] == 'He3+2':
          if nspec_over_ntot[ispecies] > 2E-2:
            curr_str = curr_str + 'he'
            nspec = nspec + 1
            nback = nback + 1
        # if species[ispecies] == 'Be'  or species[ispecies] == 'Be+':
        #   if nspec_over_ntot[ispecies] > 2E-2:
        #     curr_str = curr_str + 'be'
        #     nspec = nspec + 1
        #     nback = nback + 1
        if species[ispecies] == 'C' or species[ispecies] == 'C+':
          if nspec_over_ntot[ispecies] > 2E-2:
            curr_str = curr_str + 'ca'
            nspec = nspec + 1
            nback = nback + 1
        # if species[ispecies] == 'Ne' or species[ispecies] == 'Ne+':
        #   if nspec_over_ntot[ispecies] > 2E-2:
        #     curr_str = curr_str + 'ca'
        #     nspec = nspec + 1
        #     nback = nback + 1  
        # ALL FAST PARTICLES
    if param['fast_particles'] == 1:
      # if species[ispecies] == 'He4' or species[ispecies] == 'He4+2':
      #   if nspec_over_ntot[ispecies] > 5E-5:
          curr_str = curr_str + 'al'
          nspec = nspec + 1
          nhot = nhot + 1

    # NEED TO IMPLEMENT FAST HYDROGEN NBI, FAST DEUTERIUM NBI, RUNAWAYS ELECTRONS, DT combined

    return curr_str, nspec, nback, nhot
