import os
import imas
import pdb
import random
import copy
from lxml import etree
import xml.etree.ElementTree as ET
from ep_stability_wf.workflow.functions_wf import parameters_workflow, uri_from_params
from ep_stability_wf.interface.create_workflow_param import (
    save_xml_param_to_file_on_run,
    update_xml_param_on_run,
)
from ep_stability_wf.workflow.workflow_components import actor_call


def print_cond(verbose, *args, **kwargs):
    if verbose:
        print(*args, **kwargs)


def workflow_EP(current_config_folder, verbose=True):
    # IMPORT PARAMETERS FROM WORKFLOW XML--------------------------------------
    param = parameters_workflow(current_config_folder + "/input_workflow_default.xml")
    param = uri_from_params(param)
    # IMPORT SPECIES THRESHOLD FOR LIGKA---------------------------------------
    species_input = parameters_workflow(current_config_folder + "/actor_settings.xml")
    scenario_params = parameters_workflow(current_config_folder + "/scenario.xml")

    curr_str = None  # for avioding error
    # CHECK FOR EXISTING DB
    # output_folder = (
    #     os.getenv("HOME") + "/public/imasdb/" + param["machine_out"] + "/" + str(param['shot_nr']) + "/" + str(param['run_out'])
    # )
    # if os.path.isdir(output_folder) == False:
    #     print_cond(verbose, "-- Create local database for output file " + output_folder)
    #     try:
    #         os.makedirs(output_folder)
    #     except FileExistsError:
    #         # Calling twice in parallel can give this error. Ignore
    #         pass

    # if int(param["pulse_list"]):
    #     with open("shots.dat") as f:
    #         pulse_list = eval(f.read())
    # else:
    #     pulse_list = [(param["shot_nr"], param["run_in"])]

    # for i in pulse_list:
    #     if len(pulse_list) == 1:
    #         print_cond(
    #             verbose,
    #             "The workflow will now run with one shot/run as input: ",
    #             pulse_list,
    #         )
    #     else:
    #         print_cond(
    #             verbose,
    #             (
    #                 "The workflow will run with the same settings (and update the"
    #                 "required ones) for all selected shots/runs as input: "
    #             ),
    #             pulse_list,
    #         )
    #         update_xml_param_on_run(param, "shot_nr", i[0])
    #         save_xml_param_to_file_on_run(
    #             current_config_folder + "/input_workflow_default.xml",
    #             "shot_nr",
    #             str(i[0]),
    #         )
    #         update_xml_param_on_run(param, "run_in", i[1])
    #         save_xml_param_to_file_on_run(
    #             current_config_folder + "/input_workflow_default.xml",
    #             "run_in",
    #             str(i[1]),
    #         )
    #         param = parameters_workflow(
    #             current_config_folder + "/input_workflow_default.xml"
    #         )

    if int(param["ligka_541"]) or int(param["ligka_5412"]):
        if param["Equilibrium_code_chease"] == "Chease":
            print_cond(verbose, "Chease was selected, starting CHEASE....")
            actor_call(
                "Chease",
                current_config_folder,
                param,
                species_input,
                scenario_params,
            )
            print_cond(
                verbose, param["Equilibrium_code_chease"], " done. STARTING HELENA"
            )

        if int(param["ligka_541"]):
            print_cond(
                verbose,
                "=================Starting HELENA and LIGKA mode 5 - 4 - 1=================",
            )
        if int(param["ligka_5412"]):
            print_cond(
                verbose,
                "=================Starting HELENA and LIGKA mode 5 - 4 - 1 - 2 =================",
            )

        if param["Equilibrium_code"] == "Helena":
            print_cond(
                verbose,
                "Now modifying SCENARIO/LIGKA XML by taking the species present in core_profiles IDS",
            )

            actor_call(
                "Helena",
                current_config_folder,
                param,
                species_input,
                scenario_params,
            )

            print_cond(
                verbose, param["Equilibrium_code"], " done. STARTING LIGKA MODE 5"
            )
        else:
            print_cond(
                verbose,
                "Equilibrium code was not selected, skip and run LIGKA MODE 5.",
            )

        # MODIFY LIGKA XML TO TAKE NSPEC automatically!!
        param_ligka = parameters_workflow(current_config_folder + "/z_ligka.xml")
        if not curr_str:
            print_cond(
                verbose,
                "Now modifying LIGKA XML by taking the species present in core_profiles IDS",
            )

        update_xml_param_on_run(param_ligka, "modus", "5")
        save_xml_param_to_file_on_run(
            current_config_folder + "/z_ligka.xml", "modus", "5"
        )
        param_ligka = parameters_workflow(current_config_folder + "/z_ligka.xml")
        if param_ligka["modus"] == 5:
            actor_call("Ligka_m5", current_config_folder, param, species_input)

            print_cond(verbose, "Done LIGKA mode 5, starting mode 4")

        update_xml_param_on_run(param_ligka, "modus", "4")
        save_xml_param_to_file_on_run(
            current_config_folder + "/z_ligka.xml", "modus", "4"
        )
        param_ligka = parameters_workflow(current_config_folder + "/z_ligka.xml")
        if param_ligka["modus"] == 4:
            actor_call("Ligka_m4", current_config_folder, param, species_input)

            print_cond(verbose, "Done LIGKA mode 4, starting mode 1")

        update_xml_param_on_run(param_ligka, "modus", "1")
        save_xml_param_to_file_on_run(
            current_config_folder + "/z_ligka.xml", "modus", "1"
        )
        param_ligka = parameters_workflow(current_config_folder + "/z_ligka.xml")
        if param_ligka["modus"] == 1:
            actor_call("Ligka_m1", current_config_folder, param, species_input)

        if int(param["ligka_541"]):
            print_cond(verbose, "Done WORKFLOW, LIGKA 541.")

        if int(param["ligka_5412"]):
            print_cond(verbose, "Done LIGKA mode 1, starting mode 2")

            update_xml_param_on_run(param_ligka, "modus", "2")
            save_xml_param_to_file_on_run(
                current_config_folder + "/z_ligka.xml", "modus", "2"
            )
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )
            if param_ligka["modus"] == 2:
                actor_call("Ligka_m2", current_config_folder, param, species_input)

                print_cond(verbose, "Done WORKFLOW, LIGKA 5412.")

    else:
        if param["Equilibrium_code_chease"] == "Chease":
            print_cond(verbose, "Chease was selected, starting CHEASE....")
            actor_call(
                "Chease",
                current_config_folder,
                param,
                species_input,
                scenario_params,
            )
            print_cond(
                verbose, param["Equilibrium_code_chease"], " done. STARTING HELENA"
            )

        if param["Equilibrium_code"] == "Helena":
            print_cond(
                verbose,
                "Now modifying SCENARIO by taking the species present in core_profiles IDS",
            )
            actor_call(
                "Helena",
                current_config_folder,
                param,
                species_input,
                scenario_params,
            )

        # MODIFY LIGKA XML TO TAKE NSPEC automatically!!
        if str(param["Stability_code"]) != "0" or str(param["Orbit_Finder"]) != "0":
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )

            if not curr_str:
                print_cond(
                    verbose,
                    "Now modifying LIGKA XML by taking the species present in core_profiles IDS",
                )

        if param["Stability_code"] == "Ligka_m1":
            update_xml_param_on_run(param_ligka, "modus", "1")
            save_xml_param_to_file_on_run(
                current_config_folder + "/z_ligka.xml", "modus", "1"
            )
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )

            actor_call("Ligka_m1", current_config_folder, param, species_input)

        if param["Stability_code"] == "Ligka_m4":
            update_xml_param_on_run(param_ligka, "modus", "4")
            save_xml_param_to_file_on_run(
                current_config_folder + "/z_ligka.xml", "modus", "4"
            )
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )

            actor_call("Ligka_m4", current_config_folder, param, species_input)

        if param["Stability_code"] == "Ligka_m5":
            update_xml_param_on_run(param_ligka, "modus", "5")
            save_xml_param_to_file_on_run(
                current_config_folder + "/z_ligka.xml", "modus", "5"
            )
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )

            actor_call("Ligka_m5", current_config_folder, param, species_input)

        if param["Stability_code"] == "Ligka_m6":
            update_xml_param_on_run(param_ligka, "modus", "6")
            save_xml_param_to_file_on_run(
                current_config_folder + "/z_ligka.xml", "modus", "6"
            )
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )

            actor_call("Ligka_m6", current_config_folder, param, species_input)

        if param["Stability_code"] == "Ligka_m3":
            update_xml_param_on_run(param_ligka, "modus", "3")
            save_xml_param_to_file_on_run(
                current_config_folder + "/z_ligka.xml", "modus", "3"
            )
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )

            actor_call("Ligka_m3", current_config_folder, param, species_input)

        if param["Stability_code"] == "Ligka_m2":
            update_xml_param_on_run(param_ligka, "modus", "2")
            save_xml_param_to_file_on_run(
                current_config_folder + "/z_ligka.xml", "modus", "2"
            )
            param_ligka = parameters_workflow(
                current_config_folder + "/z_ligka.xml"
            )

            actor_call("Ligka_m2", current_config_folder, param, species_input)

        # For now it is moved here, because it runs after LIGKA m 5/4/1.
        # Soon, automatic way of checking who to run first, but after a first version of the wf is ready
        # i.e all actors are established.
        if param["Distributions_1"] == "Hagis_1":
            actor_call("Hagis_1", current_config_folder, param, species_input)

        if param["Distributions_2"] == "Hagis_2":
            actor_call("Hagis_2", current_config_folder, param, species_input)

        if param["Orbit_Finder"] == "Finder":
            print_cond(
                verbose,
                "=====================ADJUSTING FINDER XML===================",
            )
            param_finder = parameters_workflow(
                current_config_folder + "/finder_input.xml"
            )
            # ADD NPSI_OUT
            param_helena = parameters_workflow(
                current_config_folder + "/helena.xml"
            )
            update_xml_param_on_run(
                param_finder, "num_kin_rad", param_ligka["npsi_out"]
            )
            save_xml_param_to_file_on_run(
                current_config_folder + "/finder_input.xml",
                "num_kin_rad",
                str(param_helena["nrmap"]),
            )
            # ADD min/max n/m
            update_xml_param_on_run(
                param_finder, "n_prop_min", param_ligka["min_n_tor"]
            )
            save_xml_param_to_file_on_run(
                current_config_folder + "/finder_input.xml",
                "n_prop_min",
                str(param_ligka["min_n_tor"]),
            )
            update_xml_param_on_run(
                param_finder, "n_prop_max", param_ligka["max_n_tor"]
            )
            save_xml_param_to_file_on_run(
                current_config_folder + "/finder_input.xml",
                "n_prop_max",
                str(param_ligka["max_n_tor"]),
            )
            param_finder["m_min_prop"] = (
                param_ligka["min_m"]
                - param_ligka["sidebands"]
                + param_ligka["sidebands_asy"]
            )
            update_xml_param_on_run(
                param_finder, "m_min_prop", param_finder["m_min_prop"]
            )
            save_xml_param_to_file_on_run(
                current_config_folder + "/finder_input.xml",
                "m_min_prop",
                str(param_finder["m_min_prop"]),
            )
            param_finder["m_max_prop"] = (
                param_ligka["max_m"]
                + param_ligka["sidebands"]
                + param_ligka["sidebands_asy"]
            )
            update_xml_param_on_run(
                param_finder, "m_max_prop", param_finder["m_max_prop"]
            )
            save_xml_param_to_file_on_run(
                current_config_folder + "/finder_input.xml",
                "m_max_prop",
                str(param_finder["m_max_prop"]),
            )
            # MODIFY SPEC_STR AND NSPEC THE SAME AS LIGKA
            update_xml_param_on_run(
                param_finder, "spec_str", param_ligka["spec_str"]
            )
            save_xml_param_to_file_on_run(
                current_config_folder + "/finder_input.xml",
                "spec_str",
                str(param_ligka["spec_str"]),
            )
            update_xml_param_on_run(param_finder, "nspec", param_ligka["nspec"])
            save_xml_param_to_file_on_run(
                current_config_folder + "/finder_input.xml",
                "nspec",
                str(param_ligka["nspec"]),
            )

            print_cond(
                verbose,
                "=====================  STARTING Finder  ========= with m_pol range: ",
                param_finder["m_min_prop"],
                param_finder["m_max_prop"],
            )

            actor_call("Finder", current_config_folder, param, species_input)

    print_cond(verbose, "Workflow Finished.")
