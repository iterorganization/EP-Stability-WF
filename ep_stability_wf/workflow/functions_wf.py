import os
import imas
import sys
import pdb
import random
import copy
from lxml import etree
import xml.etree.ElementTree as ET
import numpy as np
from ep_stability_wf.workflow.select_ligka_species import select_species_by_density

no_actor = {}
try:
    from chease.wrapper import chease_actor
except ImportError:
    no_actor['Chease'] = True
try:
    from helena.wrapper import helena_actor
except ImportError:
    try:
        from helena_imas.wrapper import helena_imas_actor as helena_actor
    except ImportError:
        no_actor['Helena'] = True
try:
    from ligka.wrapper import ligka_actor
except ImportError:
    no_actor['Ligka_m5'] = True
    no_actor['Ligka_m4'] = True
    no_actor['Ligka_m1'] = True
    no_actor['Ligka_m6'] = True
    no_actor['Ligka_m2'] = True
    no_actor['Ligka_m3'] = True
try:
    from hagis1.wrapper import hagis1_actor
except ImportError:
    no_actor['Hagis_1'] = True
try:
    from hagis2.wrapper import hagis2_actor
except ImportError:
    no_actor['Hagis_2'] = True
try:
    from finder9.wrapper import finder9_actor
except ImportError:
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


def time_str_to_list(input_string):
    """
    Expand a range (e.g. "1-2" -> [1,2]; "1" -> [1]; 1->[1])
    """
    tmp = [int(i) for i in input_string.split("-")]
    return list(range(tmp[0], tmp[-1]+1))


def time_construction(time_input):
    """
    Take a input, which might be '1', '1,2' or '2-4' or combinations '1,3-6,7,10-11'
    In these 4 cases, correct output should be [1], [1,2], [2,3,4], [1,3,4,5,6,7,10,11]
    """
    time_list = [item for elem in str(time_input).split(
        ',') for item in time_str_to_list(elem)]
    return time_list, list(range(len(time_list)))


def read_timestep(user, database, run, current_config_folder, backend, occurrence):

    param = parameters_workflow(
        os.path.join(current_config_folder, 'input_workflow_default.xml')
    )
    print('=> Open input datafile and read total equilibrium IDS for timesteps.')
    input = imas.DBEntry(backend, database,
                         param['shot_nr'], run, user)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)
    time = input.partial_get('equilibrium', 'time', occurrence=occurrence)
    ntime = len(time)
    input.close()
    return(time, ntime)


def profiles_get(core_profiles, param, species_input, scenario_param):

    ligka_species_str, nspec, nback, nhot = select_species_by_density(core_profiles, param=param, scenario_param=scenario_param,
                                                                      density_cutoff=species_input)
    return ligka_species_str, nspec, nback, nhot


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

        if int(scenario_params['DT']):
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


def chease_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in_1,
                            distributions_in_2,
                            config_file_path,
                            mpi_processes):

    equilibrium_out = chease_actor(equilibrium_in,
                                   config_file_path)

    return equilibrium_out, None, core_profiles_in, None


def helena_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in_1,
                            distributions_in_2,
                            config_file_path,
                            mpi_processes):

    equilibrium_out = helena_actor(equilibrium_in,
                                   config_file_path)

    return equilibrium_out, None, core_profiles_in, None


def hagis1_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in_1,
                            distributions_in_2,
                            config_file_path,
                            mpi_processes):

    equilibrium_out, mhd_linear_out = hagis1_actor(
        equilibrium_in, mhd_linear_in, config_file_path)

    return equilibrium_out, mhd_linear_out, None, None


def hagis2_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in_1,
                            distributions_in_2,
                            config_file_path,
                            mpi_processes):

    mhd_linear_out, distributions_out = hagis2_actor(
        equilibrium_in, mhd_linear_in, core_profiles_in, distributions_in_1, config_file_path, 'mpi_local', mpi_processes=mpi_processes)

    return None, mhd_linear_out, None, distributions_out


def ligka_actor_wf_wrapper(equilibrium_in,
                           core_profiles_in,
                           mhd_linear_in,
                           distributions_in_1,
                           distributions_in_2,
                           config_file_path,
                           mpi_processes):

    mhd_linear_out = ligka_actor(equilibrium_in, core_profiles_in, mhd_linear_in, distributions_in_1,
                                 distributions_in_2, config_file_path, 'mpi_local', mpi_processes=mpi_processes)

    return None, mhd_linear_out, None, None


def finder_actor_wf_wrapper(equilibrium_in,
                            core_profiles_in,
                            mhd_linear_in,
                            distributions_in_1,
                            distributions_in_2,
                            config_file_path,
                            mpi_processes):

    distributions_out = finder9_actor(
        equilibrium_in, config_file_path, 'mpi_local', mpi_processes=mpi_processes)

    return None, None, None, distributions_out


def actor_settings(actor):
    actor_params = {}
    input_ids = {}
    output_ids = {}
    if actor == "Chease":
        actor_params["entrypoint_actor"] = True
        actor_params["wrapper"] = chease_actor_wf_wrapper
        actor_params["config_file_name"] = "chease_input_choices.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0, "distributions": 0}
        output_ids = {"equilibrium": 2, "core_profiles": 0, "distributions": 0}
    if actor == "Helena":
        actor_params["entrypoint_actor"] = True
        actor_params["wrapper"] = helena_actor_wf_wrapper
        actor_params["config_file_name"] = "helena.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0}
        output_ids = {"equilibrium": 0, "core_profiles": 0}
    if actor == "Ligka_m5":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0}
        output_ids = {"mhd_linear": 0}
    if actor == "Ligka_m4":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0,
                     "mhd_linear": 0, "distributions": 0, "distributions": 1}
        output_ids = {"mhd_linear": 1}
    if actor == "Ligka_m1":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0,
                     "mhd_linear": 1, "distributions": 0, "distributions": 1}
        output_ids = {"mhd_linear": 2}
    if actor == "Ligka_m6":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0, "mhd_linear": 0}
        output_ids = {"mhd_linear": 5}
    if actor == "Ligka_m2":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0,
                     "mhd_linear": 2, "distributions": 0, "distributions": 1}
        output_ids = {"mhd_linear": 6}
    if actor == "Ligka_m3":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {"equilibrium": 0, "core_profiles": 0,
                     "mhd_linear": 0, "distributions": 0, "distributions": 1}
        output_ids = {"mhd_linear": 7}
    if actor == "Hagis_1":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = hagis1_actor_wf_wrapper
        actor_params["config_file_name"] = "hagis1.xml"
        input_ids = {"equilibrium": 0, "mhd_linear": 0}
        output_ids = {"equilibrium": 1, "mhd_linear": 3}
    if actor == "Hagis_2":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = hagis2_actor_wf_wrapper
        actor_params["config_file_name"] = "hagis2.xml"
        input_ids = {"equilibrium": 1, "mhd_linear": 3,
                     "core_profiles": 0, 'distributions': 0}
        output_ids = {"distributions": 0, "mhd_linear": 4}
    if actor == "Finder":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = finder_actor_wf_wrapper
        actor_params["config_file_name"] = "finder_input.xml"
        input_ids = {"equilibrium": 1}
        output_ids = {"distributions": 1}

    actor_params["input_ids"] = input_ids
    actor_params["output_ids"] = output_ids

    return actor_params
