import os
import imas
import sys
import pdb
import random
import copy
from lxml import etree
import xml.etree.ElementTree as ET
from imas import imasdef
import numpy as np

from helena_imas.wrapper import helena_imas_actor
from ligka.wrapper import ligka_actor
no_actor = {}
try:
    from hagis1.wrapper import hagis1_actor
except:
    no_actor['Hagis_1'] = True
# try:
#    from chease.wrapper import chease_actor
# except:
#    no_actor['chease'] = True
try:
    from hagis2.wrapper import hagis2_actor
except:
    no_actor['Hagis_2'] = True
try:
    from finder9.wrapper import finder9_actor
except:
    no_actor['Finder'] = True
if len(list(no_actor.keys())) > 0:
    print('Cannot import:')
    for key in no_actor:
        print('    {}'.format(key))
    print('Continuing without the above actors')


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

    return(param)

# WF RUNNING FUNCTIONS


def read_timestep(user, database, run, current_config_folder):

    param = parameters_workflow(
        current_config_folder + '/input_workflow_default.xml')
    print('=> Open input datafile and read total equilibrium IDS for timesteps.')
    input = imas.DBEntry(imasdef.HDF5_BACKEND, database,
                         param['shot_nr'], run, user)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)
    time = input.partial_get('equilibrium', 'time')
    ntime = len(time)
    input.close()
    return(time, ntime)


def profiles_get(param, species_input, scenario_input):
    # Needs to be updated to the new AL
    print('=> Open input datafile and read the numer of species and other neccesary inputs for LIGKA')
    # input_species = imas.ids(param['shot_nr'], param['run_in'], 0, 0)
    input_species = imas.DBEntry(imasdef.HDF5_BACKEND, param['machine_out'], param['shot_nr'], param['run_out'], os.getenv('USER'))
    input_species.open()
    core_profiles = input_species.get('core_profiles')
    time = core_profiles.time
    ntime = len(time)

    # core_profiles.profiles_1d.resize(1)
    # if ntime > 1:  # if NOT ASTRA shot
    #     core_profiles.profiles_1d[0] = input_species.partial_get('core_profiles',
    #         'profiles_1d('+str(int(time[1]))+')')
    nspecies = len(core_profiles.profiles_1d[0].ion)

    species = []
    for ispecies in range(nspecies):
        species.append(core_profiles.profiles_1d[0].ion[ispecies].label)
    volume = core_profiles.profiles_1d[0].grid.volume
    ntot = 0
    species_density = [0] * nspecies
    for ispecies in range(nspecies):
        species_density[ispecies] = sum(
            volume*core_profiles.profiles_1d[0].ion[ispecies].density)
        ntot = ntot + species_density[ispecies]

    ne = sum(volume*core_profiles.profiles_1d[0].electrons.density)

    nspec_over_ntot = [val/ntot for val in species_density]
    nspec_over_ne = [val/ne for val in species_density]

    for ispecies in range(nspecies):
        for jspecies in range(nspecies):
            if (species[jspecies] == species[ispecies]) & (jspecies != ispecies):
                nspec_over_ntot[ispecies] = nspec_over_ntot[ispecies] + \
                    nspec_over_ntot[jspecies]
                nspec_over_ntot[jspecies] = 0
                nspec_over_ne[ispecies] = nspec_over_ne[ispecies] + \
                    nspec_over_ne[jspecies]
                nspec_over_ne[jspecies] = 0

    curr_str = 'el'
    nspec = 1
    nback = 1
    nhot = 0

    for ispecies in range(nspecies):
        if nspec_over_ntot[ispecies] > 0. and nspec_over_ne[ispecies] > 0.:
            print('For ion name: ', species[ispecies])
            print('Density over total: ', format(
                '%.10f' % nspec_over_ntot[ispecies]))
            print('Density over electron density: ',
                  format('%.10f' % nspec_over_ne[ispecies]))
            # ALL THERMAL PARTICLES:
            if species[ispecies] == 'H' or species[ispecies] == 'H+':
                if nspec_over_ntot[ispecies] >= float(species_input["H"]):
                    curr_str = curr_str + 'hh'
                    nspec = nspec + 1
                    nback = nback + 1
            if species[ispecies] == 'D' or species[ispecies] == 'D+':
                if scenario_input['DT'] == 1:
                    curr_str = curr_str + 'dt'
                    nspec = nspec + 1
                    nback = nback + 1
                else:
                    if nspec_over_ntot[ispecies] >= float(species_input["D"]):
                        curr_str = curr_str + 'dd'
                        nspec = nspec + 1
                        nback = nback + 1
            if species[ispecies] == 'T' or species[ispecies] == 'T+':
                if scenario_input['DT'] == 0:
                    if nspec_over_ntot[ispecies] >= float(species_input["T"]):
                        curr_str = curr_str + 'tt'
                        nspec = nspec + 1
                        nback = nback + 1
            if species[ispecies] == 'He4' or species[ispecies] == 'He4+2':
                if nspec_over_ntot[ispecies] >= float(species_input["He4_ash"]):
                    curr_str = curr_str + 'he'
                    nspec = nspec + 1
                    nback = nback + 1
            if species[ispecies] == 'Be' or species[ispecies] == 'Be+':
                if nspec_over_ntot[ispecies] > float(species_input["Be"]):
                    curr_str = curr_str + 'be'
                    nspec = nspec + 1
                    nback = nback + 1
            if species[ispecies] == 'C' or species[ispecies] == 'C+':
                if nspec_over_ntot[ispecies] >= float(species_input["C"]):
                    curr_str = curr_str + 'ca'
                    nspec = nspec + 1
                    nback = nback + 1
            if species[ispecies] == 'Ne' or species[ispecies] == 'Ne+':
                if nspec_over_ntot[ispecies] > float(species_input["Ne"]):
                    curr_str = curr_str + 'ne'
                    nspec = nspec + 1
                    nback = nback + 1
            # ALL FAST PARTICLES
    if param['fast_particles'] == 1:
        curr_str = curr_str + 'al'
        nspec = nspec + 1
        nhot = nhot + 1

    # NEED TO IMPLEMENT FAST HYDROGEN NBI, FAST DEUTERIUM NBI, RUNAWAYS ELECTRONS, DT combined
    input_species.close()
    return curr_str, nspec, nback, nhot


def scenario_mod(core_profiles_in, curr_str, scenario_params):
    print('Updating core_profiles according to the scenario modification parameters.')
    curr_str_split = []
    while curr_str:
        curr_str_split.append(curr_str[:2])
        curr_str = curr_str[2:]

    if 'el' in curr_str_split:
        core_profiles_in.profiles_1d[0].electrons.density = np.array(
            core_profiles_in.profiles_1d[0].electrons.density) * scenario_params['n_e']
        core_profiles_in.profiles_1d[0].electrons.temperature = np.array(
            core_profiles_in.profiles_1d[0].electrons.temperature) * scenario_params['T_e']

    for i in range(len(core_profiles_in.profiles_1d[0].ion)):
        if core_profiles_in.profiles_1d[0].ion[i].label == 'H+' or core_profiles_in.profiles_1d[0].ion[i].label == 'H':
            if 'hh' in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_H']
                core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_H']

        if scenario_params['DT'] == 1:
            if core_profiles_in.profiles_1d[0].ion[i].label == 'D+' or core_profiles_in.profiles_1d[0].ion[i].label == 'D':
                core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_D']
                core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_D']
        else:
            if core_profiles_in.profiles_1d[0].ion[i].label == 'D+' or core_profiles_in.profiles_1d[0].ion[i].label == 'D':
                if 'dd' in curr_str_split:
                    core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                        core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_D']
                    core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                        core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_D']

            if core_profiles_in.profiles_1d[0].ion[i].label == 'T+' or core_profiles_in.profiles_1d[0].ion[i].label == 'T':
                if 'tt' in curr_str_split:
                    core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                        core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_T']
                    core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                        core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_T']

        if core_profiles_in.profiles_1d[0].ion[i].label == 'Be+' or core_profiles_in.profiles_1d[0].ion[i].label == 'Be':
            if 'be' in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_Be']
                core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_Be']

        if core_profiles_in.profiles_1d[0].ion[i].label == 'C+' or core_profiles_in.profiles_1d[0].ion[i].label == 'C':
            if 'ca' in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_C']
                core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_C']

        if core_profiles_in.profiles_1d[0].ion[i].label == 'Ne+' or core_profiles_in.profiles_1d[0].ion[i].label == 'Ne':
            if 'ne' in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_Ne']
                core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_Ne']

        if core_profiles_in.profiles_1d[0].ion[i].label == 'He4+2' or core_profiles_in.profiles_1d[0].ion[i].label == 'He4':
            if 'al' in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density_fast = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].density_fast) * scenario_params['n_He4_EP']
                core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_He4_EP']
            if 'he' in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].density) * scenario_params['n_He4_ash']
                core_profiles_in.profiles_1d[0].ion[i].temperature = np.array(
                    core_profiles_in.profiles_1d[0].ion[i].temperature) * scenario_params['T_He4_ash']

    return core_profiles_in


def imports_check(actor_name):
    if actor_name in no_actor:
        print(actor_name + ' is not imported, cannot continue.')
        return 0


def helena_imas_actor_wf_wrapper(equilibrium_in,
                                 core_profiles_in,
                                 mhd_linear_in,
                                 distributions_in,
                                 config_file_path,
                                 run_mode,
                                 mpi_processes):

    equilibrium_out = helena_imas_actor(equilibrium_in,
                                        config_file_path)

    return equilibrium_out, None, core_profiles_in, None


def hagis1_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in,
                            config_file_path,
                            run_mode,
                            mpi_processes):

    equilibrium_out, mhd_linear_out = hagis1_actor(
        equilibrium_in, mhd_linear_in, config_file_path)

    return equilibrium_out, mhd_linear_out, None, None


def hagis2_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in,
                            config_file_path,
                            run_mode,
                            mpi_processes):

    mhd_linear_out, distributions_out = hagis2_actor(
        equilibrium_in, mhd_linear_in, core_profiles_in, distributions_in, config_file_path, 'mpi_local', mpi_processes=mpi_processes)

    return None, mhd_linear_out, None, distributions_out


def ligka_actor_wf_wrapper(equilibrium_in,
                           core_profiles_in,
                           mhd_linear_in,
                           distributions_in,
                           config_file_path,
                           run_mode,
                           mpi_processes):

    mhd_linear_out = ligka_actor(equilibrium_in, core_profiles_in, mhd_linear_in,
                                 config_file_path, 'mpi_local', mpi_processes=mpi_processes)

    return None, mhd_linear_out, None, None


def finder_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in,
                            config_file_path,
                            run_mode,
                            mpi_processes):

    distributions_out = finder9_actor(
        equilibrium_in, config_file_path, 'mpi_local', mpi_processes=mpi_processes)

    return None, None, None, distributions_out


def actor_settings(actor):
    actor_params = {}
    input_ids = {}
    output_ids = {}
    if actor == "Helena":
        actor_params["entrypoint_actor"] = True
        actor_params["wrapper"] = helena_imas_actor_wf_wrapper
        actor_params["config_file_name"] = "/helena.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0}
        output_ids = {"equilibrium": 0, "core_profiles": 0}
    if actor == "Ligka_m5":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "/z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0}
        output_ids = {"mhd_linear": 0}
    if actor == "Ligka_m4":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "/z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0, "mhd_linear": 0}
        output_ids = {"mhd_linear": 1}
    if actor == "Ligka_m1":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "/z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0, "mhd_linear": 1}
        output_ids = {"mhd_linear": 2}
    if actor == "Ligka_m6":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "/z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0, "mhd_linear": 0}
        output_ids = {"mhd_linear": 5}
    if actor == "Ligka_m2":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "/z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0, "mhd_linear": 1}
        output_ids = {"mhd_linear": 6}
    if actor == "Ligka_m3":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "/z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0, "mhd_linear": 0}
        output_ids = {"mhd_linear": 7}
    if actor == "Hagis_1":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = hagis1_actor_wf_wrapper
        actor_params["config_file_name"] = "/hagis1.xml"
        input_ids = {"equilibrium": 0, "mhd_linear": 0}
        output_ids = {"equilibrium": 1, "mhd_linear": 3}
    if actor == "Hagis_2":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = hagis2_actor_wf_wrapper
        actor_params["config_file_name"] = "/hagis2.xml"
        input_ids = {"equilibrium": 1, "mhd_linear": 3, "core_profiles": 0}
        output_ids = {"distributions": 0, "mhd_linear": 4}
    if actor == "Finder":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = finder_actor_wf_wrapper
        actor_params["config_file_name"] = "/finder_input.xml"
        input_ids = {"equilibrium": 1}
        output_ids = {"distributions": 1}

    actor_params["input_ids"] = input_ids
    actor_params["output_ids"] = output_ids

    return actor_params
