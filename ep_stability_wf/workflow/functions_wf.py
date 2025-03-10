import os
import imas
import sys
import pdb
import random
import copy
from lxml import etree
import xml.etree.ElementTree as ET
import numpy as np
import re
from ep_stability_wf.workflow.select_ligka_species import select_species_by_density

no_actor = {}
try:
    from chease.actor import chease
    from chease.common.runtime_settings import SandboxLifeTime as SandboxLifeTime_Chease
except ImportError:
    no_actor["Chease"] = True
try:
    from helena.actor import helena
    from helena.common.runtime_settings import SandboxLifeTime as SandboxLifeTime_Helena
except ImportError:
    try:
        from helena_imas.wrapper import helena_imas_actor as helena_actor
    except ImportError:
        no_actor["Helena"] = True
try:
    from ligka.actor import ligka
    from ligka.common.runtime_settings import SandboxLifeTime as SandboxLifeTime_Ligka
except ImportError:
    no_actor["Ligka_m5"] = True
    no_actor["Ligka_m4"] = True
    no_actor["Ligka_m1"] = True
    no_actor["Ligka_m6"] = True
    no_actor["Ligka_m2"] = True
    no_actor["Ligka_m3"] = True
try:
    from hagis1.actor import hagis1
    from hagis1.common.runtime_settings import SandboxLifeTime as SandboxLifeTime_Hagis1
except ImportError:
    no_actor["Hagis_1"] = True
try:
    from hagis2.actor import hagis2
    from hagis2.common.runtime_settings import SandboxLifeTime as SandboxLifeTime_Hagis2
except ImportError:
    no_actor["Hagis_2"] = True
try:
    from finder9.actor import finder9
    from finder9.common.runtime_settings import SandboxLifeTime as SandboxLifeTime_Finder9
except ImportError:
    no_actor["Finder"] = True
try:
    from falcon_wf import falcon_actor
except ImportError:
    no_actor["Falcon"] = True

if len(list(no_actor.keys())) > 0:
    print("Cannot import:")
    for key in no_actor:
        print("    {}".format(key))
    print("Continuing without the above actors")

def uri_from_params(param):
    user = os.getenv("USER")
    if param["hdf5"] == 1:
        backend = "hdf5"
    else:
        backend = "mdsplus"
    # First with inputs
    if param["uri_in"] in [None, ""]:
        # Using legacy
        uri_in = f'imas:{backend}?user={param["user"]};shot={param["shot"]};run={param["run_in"]};database={param["machine_in"]};version=3'
    else:
        # Assume uri is complete!
        if re.match(r'^imas', param["uri_in"]):
            uri_in = param["uri_in"]
        else:
            uri_in = f'imas:{backend}?path={param["uri_in"]}'
    param["uri_in"] = uri_in

    # Outputs
    if param["uri_out"] in [None, ""]:
        # Using legacy
        uri_out = f'imas:{backend}?user={user};shot={param["shot"]};run={param["run_out"]};database={param["machine_out"]};version=3'
    else:
        # Assume uri is complete!
        if re.match(r'^imas', param["uri_out"]):
            uri_out = param["uri_out"]
        else:
            uri_out = f'imas:{backend}?path={param["uri_out"]}'
    param["uri_out"] = uri_out
    return param

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

            param["input_path"] = input_file

    return param


# WF RUNNING FUNCTIONS


def time_str_to_list(input_string):
    """
    Expand a range (e.g. "1-2" -> [1,2]; "1" -> [1]; 1->[1])
    """
    tmp = [int(i) for i in input_string.split("-")]
    return list(range(tmp[0], tmp[-1] + 1))


def time_construction(time_input):
    """
    Take a input, which might be '1', '1,2' or '2-4' or combinations '1,3-6,7,10-11'
    In these 4 cases, correct output should be [1], [1,2], [2,3,4], [1,3,4,5,6,7,10,11]
    """
    time_list = [
        item for elem in str(time_input).split(",") for item in time_str_to_list(elem)
    ]
    return time_list, list(range(len(time_list)))


def read_timestep(uri_in, occurrence):
    print(
        "=> Open input datafile and read total equilibrium IDS for timesteps."
    )
    try:
        input = imas.DBEntry(uri_in, "r")
    except:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)

    time = input.partial_get("equilibrium", "time", occurrence=occurrence)
    ntime = len(time)
    input.close()
    return (time, ntime)


def profiles_get(core_profiles, param, species_input, scenario_param):
    ligka_species_str, nspec, nback, nhot = select_species_by_density(
        core_profiles,
        param=param,
        scenario_param=scenario_param,
        density_cutoff=species_input,
    )
    return ligka_species_str, nspec, nback, nhot


def scenario_mod(core_profiles_in, curr_str, scenario_params):
    print("Updating core_profiles according to the scenario modification parameters.")
    curr_str_split = []
    while curr_str:
        curr_str_split.append(curr_str[:2])
        curr_str = curr_str[2:]

    if "el" in curr_str_split:
        core_profiles_in.profiles_1d[0].electrons.density = (
            np.array(core_profiles_in.profiles_1d[0].electrons.density)
            * scenario_params["n_e"]
        )
        core_profiles_in.profiles_1d[0].electrons.temperature = (
            np.array(core_profiles_in.profiles_1d[0].electrons.temperature)
            * scenario_params["T_e"]
        )

    for i in range(len(core_profiles_in.profiles_1d[0].ion)):
        if (
            core_profiles_in.profiles_1d[0].ion[i].label == "H+"
            or core_profiles_in.profiles_1d[0].ion[i].label == "H"
        ):
            if "hh" in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                    * scenario_params["n_H"]
                )
                core_profiles_in.profiles_1d[0].ion[i].temperature = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                    * scenario_params["T_H"]
                )

        if int(scenario_params["DT"]):
            if (
                core_profiles_in.profiles_1d[0].ion[i].label == "D+"
                or core_profiles_in.profiles_1d[0].ion[i].label == "D"
            ):
                core_profiles_in.profiles_1d[0].ion[i].density = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                    * scenario_params["n_D"]
                )
                core_profiles_in.profiles_1d[0].ion[i].temperature = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                    * scenario_params["T_D"]
                )
        else:
            if (
                core_profiles_in.profiles_1d[0].ion[i].label == "D+"
                or core_profiles_in.profiles_1d[0].ion[i].label == "D"
            ):
                if "dd" in curr_str_split:
                    core_profiles_in.profiles_1d[0].ion[i].density = (
                        np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                        * scenario_params["n_D"]
                    )
                    core_profiles_in.profiles_1d[0].ion[i].temperature = (
                        np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                        * scenario_params["T_D"]
                    )

            if (
                core_profiles_in.profiles_1d[0].ion[i].label == "T+"
                or core_profiles_in.profiles_1d[0].ion[i].label == "T"
            ):
                if "tt" in curr_str_split:
                    core_profiles_in.profiles_1d[0].ion[i].density = (
                        np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                        * scenario_params["n_T"]
                    )
                    core_profiles_in.profiles_1d[0].ion[i].temperature = (
                        np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                        * scenario_params["T_T"]
                    )

        if (
            core_profiles_in.profiles_1d[0].ion[i].label == "Be+"
            or core_profiles_in.profiles_1d[0].ion[i].label == "Be"
        ):
            if "be" in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                    * scenario_params["n_Be"]
                )
                core_profiles_in.profiles_1d[0].ion[i].temperature = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                    * scenario_params["T_Be"]
                )

        if (
            core_profiles_in.profiles_1d[0].ion[i].label == "C+"
            or core_profiles_in.profiles_1d[0].ion[i].label == "C"
        ):
            if "ca" in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                    * scenario_params["n_C"]
                )
                core_profiles_in.profiles_1d[0].ion[i].temperature = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                    * scenario_params["T_C"]
                )

        if (
            core_profiles_in.profiles_1d[0].ion[i].label == "Ne+"
            or core_profiles_in.profiles_1d[0].ion[i].label == "Ne"
        ):
            if "ne" in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                    * scenario_params["n_Ne"]
                )
                core_profiles_in.profiles_1d[0].ion[i].temperature = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                    * scenario_params["T_Ne"]
                )

        if (
            core_profiles_in.profiles_1d[0].ion[i].label == "He4+2"
            or core_profiles_in.profiles_1d[0].ion[i].label == "He4"
        ):
            if "al" in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density_fast = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].density_fast)
                    * scenario_params["n_He4_EP"]
                )
                core_profiles_in.profiles_1d[0].ion[i].temperature = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                    * scenario_params["T_He4_EP"]
                )
            if "he" in curr_str_split:
                core_profiles_in.profiles_1d[0].ion[i].density = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].density)
                    * scenario_params["n_He4_ash"]
                )
                core_profiles_in.profiles_1d[0].ion[i].temperature = (
                    np.array(core_profiles_in.profiles_1d[0].ion[i].temperature)
                    * scenario_params["T_He4_ash"]
                )

    return core_profiles_in


def imports_check(actor_name):
    if actor_name in no_actor:
        print(actor_name + " is not imported, cannot continue.")
        return 0
    
def modify_xml(xml_file):
    # Load the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Remove the 'display' attribute from the root element, if it exists
    if 'display' in root.attrib:
        del root.attrib['display']

    output_file_path = xml_file.split('.')[0]+'_run.xml'
    
    # Save the updated XML back to the file or keep it in memory
    tree.write(output_file_path, encoding='utf-8', xml_declaration=True)
    return output_file_path

def chease_actor_wf_wrapper(
    equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks,
):
    chease_actor = chease()
    code_parameters = chease_actor.get_code_parameters()
    config_file_path = modify_xml(config_file_path)
    code_parameters.parameters_path = config_file_path
    runtime_settings = chease_actor.get_runtime_settings()
    runtime_settings.sandbox.life_time = SandboxLifeTime_Chease.PERSISTENT
    chease_actor.initialize(code_parameters=code_parameters, runtime_settings=runtime_settings)

    equilibrium_out = chease_actor.run(equilibrium_in)

    chease_actor.finalize()

    return equilibrium_out, None, core_profiles_in, None


def helena_actor_wf_wrapper(
    equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks,
):
    helena_actor = helena()
    code_parameters = helena_actor.get_code_parameters()
    config_file_path = modify_xml(config_file_path)
    code_parameters.parameters_path = config_file_path
    runtime_settings = helena_actor.get_runtime_settings()
    runtime_settings.sandbox.life_time = SandboxLifeTime_Helena.PERSISTENT
    helena_actor.initialize(code_parameters=code_parameters, runtime_settings=runtime_settings)

    equilibrium_out = helena_actor.run(equilibrium_in)

    helena_actor.finalize()

    return equilibrium_out, None, core_profiles_in, None


def hagis1_actor_wf_wrapper(
    equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks,
):
    hagis1_actor = hagis1()
    code_parameters = hagis1_actor.get_code_parameters()
    config_file_path = modify_xml(config_file_path)
    code_parameters.parameters_path = config_file_path
    runtime_settings = hagis1_actor.get_runtime_settings()
    runtime_settings.sandbox.life_time = SandboxLifeTime_Hagis1.PERSISTENT
    hagis1_actor.initialize(code_parameters=code_parameters, runtime_settings=runtime_settings)

    equilibrium_out, mhd_linear_out = hagis1_actor(
        equilibrium_in, mhd_linear_in
    )

    hagis1_actor.finalize()
    

    return equilibrium_out, mhd_linear_out, None, None


def hagis2_actor_wf_wrapper(
    equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks,
):
    hagis2_actor = hagis2()
    code_parameters = hagis2_actor.get_code_parameters()
    config_file_path = modify_xml(config_file_path)
    code_parameters.parameters_path = config_file_path
    runtime_settings = hagis2_actor.get_runtime_settings()
    #configures runtime settings
    runtime_settings.mpi.mpi_processes = mpi_ranks
    # runtime_settings.mpi.mpi_runner = 'mpirun'
    # runtime_settings.mpi.mpi_options = '-tv'
    runtime_settings.sandbox.life_time = SandboxLifeTime_Hagis2.PERSISTENT
    hagis2_actor.initialize(code_parameters=code_parameters, runtime_settings=runtime_settings)

    
    mhd_linear_out, distributions_out = hagis2_actor(
        equilibrium_in,
        mhd_linear_in,
        core_profiles_in,
        distributions_in_1
    )
    hagis2_actor.finalize()
    return None, mhd_linear_out, None, distributions_out


def ligka_actor_wf_wrapper(
    equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks,
):
    
    ligka_actor = ligka()
    code_parameters = ligka_actor.get_code_parameters()
    config_file_path = modify_xml(config_file_path)
    code_parameters.parameters_path = config_file_path
    runtime_settings = ligka_actor.get_runtime_settings()
    #configures runtime settings
    runtime_settings.mpi.mpi_processes = mpi_ranks
    # runtime_settings.mpi.mpi_runner = 'mpirun'
    # runtime_settings.mpi.mpi_options = '-tv'
    runtime_settings.sandbox.life_time = SandboxLifeTime_Ligka.PERSISTENT
    ligka_actor.initialize(code_parameters=code_parameters, runtime_settings=runtime_settings)

    mhd_linear_out = ligka_actor.run(
        equilibrium_in,
        core_profiles_in,
        mhd_linear_in,
        distributions_in_1,
        distributions_in_2
    )

    ligka_actor.finalize()
    return None, mhd_linear_out, None, None


def finder_actor_wf_wrapper(
    equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks,
):
    finder9_actor = finder9()
    code_parameters = finder9_actor.get_code_parameters()
    config_file_path = modify_xml(config_file_path)
    code_parameters.parameters_path = config_file_path
    runtime_settings = finder9_actor.get_runtime_settings()
    #configures runtime settings
    runtime_settings.mpi.mpi_processes = mpi_ranks
    # runtime_settings.mpi.mpi_runner = 'mpirun'
    # runtime_settings.mpi.mpi_options = '-tv'
    runtime_settings.sandbox.life_time = SandboxLifeTime_Finder9.PERSISTENT
    finder9_actor.initialize(code_parameters=code_parameters, runtime_settings=runtime_settings)

    
    distributions_out = finder9_actor(
        equilibrium_in,
        core_profiles_in,
        mhd_linear_in,
        distributions_in_1,
        distributions_in_2
    )
    finder9_actor.finalize()
    return None, None, None, distributions_out

# Different because non Iwrap actor (python actor)
def falcon_actor_wf_wrapper_full(equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks):

    mhd_linear_out = falcon_actor(
        equilibrium_in, core_profiles_in, config_file_path)
    return None, mhd_linear_out, None, None

def falcon_actor_wf_wrapper_slow(equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks):

    mhd_linear_out = falcon_actor(
        equilibrium_in, core_profiles_in, config_file_path, slow=True)
    return None, mhd_linear_out, None, None

def falcon_actor_wf_wrapper_daeps(equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks):

    mhd_linear_out = falcon_actor(
        equilibrium_in, core_profiles_in, config_file_path, daeps=True)
    return None, mhd_linear_out, None, None

def falcon_actor_wf_wrapper_daeps_eigen(equilibrium_in,
    core_profiles_in,
    mhd_linear_in,
    distributions_in_1,
    distributions_in_2,
    config_file_path,
    mpi_ranks):

    mhd_linear_out = falcon_actor(
        equilibrium_in, core_profiles_in, config_file_path, eigen=True)
    return None, mhd_linear_out, None, None

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
        input_ids = {
            "equilibrium": 0,
            "core_profiles": 0,
            "mhd_linear": 0,
            "distributions": 0,
            "distributions": 1,
        }
        output_ids = {"mhd_linear": 1}
    if actor == "Ligka_m1":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {
            "equilibrium": 0,
            "core_profiles": 0,
            "mhd_linear": 1,
            "distributions": 0,
            "distributions": 1,
        }
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
        input_ids = {
            "equilibrium": 0,
            "core_profiles": 0,
            "mhd_linear": 2,
            "distributions": 0,
            "distributions": 1,
        }
        output_ids = {"mhd_linear": 6}
    if actor == "Ligka_m3":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = ligka_actor_wf_wrapper
        actor_params["config_file_name"] = "z_ligka.xml"
        input_ids = {
            "equilibrium": 0,
            "core_profiles": 0,
            "mhd_linear": 0,
            "distributions": 0,
            "distributions": 1,
        }
        output_ids = {"mhd_linear": 7}
    if actor == "Hagis_1":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = hagis1_actor_wf_wrapper
        actor_params["config_file_name"] = "hagis1.xml"
        input_ids = {"equilibrium": 0, "mhd_linear": 6}
        output_ids = {"equilibrium": 1, "mhd_linear": 3}
    if actor == "Hagis_2":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = hagis2_actor_wf_wrapper
        actor_params["config_file_name"] = "hagis2.xml"
        input_ids = {
            "equilibrium": 1,
            "mhd_linear": 3,
            "core_profiles": 0,
            "distributions": 0,
        }
        output_ids = {"distributions": 0, "mhd_linear": 4}
    if actor == "Finder":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = finder_actor_wf_wrapper
        actor_params["config_file_name"] = "finder_input.xml"
        input_ids = {
            "equilibrium": 1,
            "core_profiles": 0,
            "mhd_linear": 3,
            "distributions": 0,
            "distributions": 1,
        }
        output_ids = {"distributions": 1}
    if actor == "Falcon_full":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = falcon_actor_wf_wrapper_full
        actor_params["config_file_name"] = "falcon.xml"
        input_ids = {"equilibrium": 2, "core_profiles": 0}
        output_ids = {"mhd_linear": 8}
    if actor == "Falcon_slow":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = falcon_actor_wf_wrapper_slow
        actor_params["config_file_name"] = "falcon.xml"
        input_ids = {"equilibrium": 2, "core_profiles": 0}
        output_ids = {"mhd_linear": 9}
    if actor == "DAEPS":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = falcon_actor_wf_wrapper_daeps
        actor_params["config_file_name"] = "falcon.xml"
        input_ids = {"equilibrium": 2, "core_profiles": 0}
        output_ids = {"mhd_linear": 10}
    if actor == "DAEPS_eigen":
        actor_params["entrypoint_actor"] = False
        actor_params["wrapper"] = falcon_actor_wf_wrapper_daeps_eigen
        actor_params["config_file_name"] = "falcon.xml"
        input_ids = {"equilibrium": 2, "core_profiles": 0}
        output_ids = {"mhd_linear": 11}

    actor_params["input_ids"] = input_ids
    actor_params["output_ids"] = output_ids

    return actor_params
