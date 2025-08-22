import os
import imas
import sys

from ep_stability_wf.workflow.functions_wf import (
    read_timestep,
    actor_settings,
    imports_check,
    scenario_mod,
    time_construction,
    profiles_get,
    actor_sandbox_folder
)
from ep_stability_wf.interface.create_workflow_param import (
    save_xml_param_multiple_to_file_on_run,
)


def actor_call(
    actor_name, config_folder_path, system_params, species_input, scenario_params=None
):
    """
    This method initializes and runs an workflow actor
    Params:
      actor_name: str - name of the actor to run
      config_folder_path: str - path to the general config folder
      system_params: Dict - I/O system configuration
    """

    # Check if the actor exists (properly imported):
    if imports_check(actor_name) == 0:
        return

    print("*************************************")
    print("Starting " + actor_name)
    print("*************************************")

    actor_params = actor_settings(actor_name)

    input_ids = actor_params["input_ids"]
    output_ids = actor_params["output_ids"]

    uri_in = None
    uri_out = None
    config_file = os.path.join(config_folder_path, actor_params["config_file_name"])
    sandbox_folder = actor_sandbox_folder(actor_name, config_folder_path)
    actor_sandbox_options = [sandbox_folder, None]
 
    if actor_name == "Ligka_m5":
        mpi_processes = 1
    else:
        mpi_processes = system_params["mpi_processes"]

    if actor_name == "Helena":
        if system_params["Equilibrium_code_chease"] == "Chease":
            actor_params["entrypoint_actor"] = False
            input_ids["equilibrium"] = 2
            # If CHEASE is run first, we remove the input/output from helena to chease actor (i.e delete the entries of the dict)
            del input_ids["core_profiles"]
            del output_ids["core_profiles"]

    if actor_params["entrypoint_actor"]:
        uri_in = system_params["uri_in"]
        uri_out = system_params["uri_out"]
        time_index_list, _ = time_construction(system_params["itime"])
    else:
        uri_in = system_params["uri_out"]
        uri_out = system_params["uri_out"]
        _, time_index_list = time_construction(system_params["itime"])

    # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
    # AND READ FULL TIME VECTOR OF EQUILIBRIUM IDS TO GET THE TIME BASE
    time, ntime = read_timestep(
        uri_in,
        occurrence=input_ids["equilibrium"],
    )

    # OPEN INPUT DATAFILE TO GET DATA FROM IMAS SCENARIO DATABASE
    try:
        input = imas.DBEntry(uri_in, "r")
    except:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)

    if actor_params["entrypoint_actor"]:
        # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
        print("=> Create output datafile")
        try:
            output = imas.DBEntry(uri_out, "w")
        except:
            print("Can't create the dataset!", file=sys.stderr)
            sys.exit(1)
    else:
        output = input
        if actor_name != "Helena":
            for ids_name, ids_occ in output_ids.items():
                input.delete_data(ids_name, occurrence=ids_occ)

    for i, itime in enumerate(time_index_list):
        # EXECUTE PHYSICS CODE
        print(
            f"Time = {time[itime]} s, itime = {itime}/{ntime-1}, slice number ={i}/{len(time_index_list)}"
        )
        actor_sandbox_options[1] = time[itime]
        equilibrium_in = imas.equilibrium()
        equilibrium_occ = 0
        core_profiles_in = None
        mhd_linear_in = imas.mhd_linear()
        mhd_linear_in.ids_properties.homogeneous_time = 1
        mhd_linear_occ = 0
        distributions_in_1 = imas.distributions()
        distributions_in_1.ids_properties.homogeneous_time = 1
        distributions_occ_1 = 0
        distributions_in_2 = imas.distributions()
        distributions_in_2.ids_properties.homogeneous_time = 1
        distributions_occ_2 = 1

        for ids_name, ids_occ in input_ids.items():
            if ids_name == "equilibrium":
                equilibrium_in = input.get_slice(
                    ids_name,
                    time[itime],
                    imas.imasdef.PREVIOUS_SAMPLE,
                    occurrence=ids_occ,
                )
                equilibrium_occ = ids_occ

            if ids_name == "mhd_linear":
                try:
                    mhd_linear_in = input.get_slice(
                        ids_name,
                        time[itime],
                        imas.imasdef.PREVIOUS_SAMPLE,
                        occurrence=ids_occ,
                    )
                    mhd_linear_in.ids_properties.homogeneous_time = 1
                    mhd_linear_occ = ids_occ
                except:
                    print(
                        f"No mhd_linear with occurrence {mhd_linear_occ} found, using empty mhd_linear"
                    )

            if ids_name == "distributions":
                if ids_occ == 0:
                    try:
                        distributions_in_1 = input.get_slice(
                            ids_name,
                            time[itime],
                            imas.imasdef.PREVIOUS_SAMPLE,
                            occurrence=ids_occ,
                        )
                    except:
                        print(
                            f"No distributions with occurrence {distributions_occ_1} found, using empty distributions"
                        )
                elif ids_occ == 1:
                    try:
                        distributions_in_2 = input.get_slice(
                            ids_name,
                            time[itime],
                            imas.imasdef.PREVIOUS_SAMPLE,
                            occurrence=ids_occ,
                        )
                    except:
                        print(
                            f"No distributions with occurrence {distributions_occ_2} found, using empty distributions"
                        )

            if ids_name == "core_profiles":
                core_profiles_in = input.get_slice(
                    ids_name,
                    time[itime],
                    imas.imasdef.PREVIOUS_SAMPLE,
                    occurrence=ids_occ,
                )
                core_profiles_occ = ids_occ

                curr_str, nspec, nback, nhot = profiles_get(
                    core_profiles_in, system_params, species_input, scenario_params
                )

                if actor_params["entrypoint_actor"]:
                    core_profiles_in = scenario_mod(
                        core_profiles_in, curr_str, scenario_params
                    )
                else:
                    save_xml_param_multiple_to_file_on_run(
                        config_file,
                        ["spec_str", "nspec", "nback", "nhot"],
                        [str(curr_str), str(nspec), str(nback), str(nhot)],
                    )

        (
            equilibrium_out,
            mhd_linear_out,
            core_profiles_out,
            distributions_out,
        ) = actor_params["wrapper"](
            equilibrium_in,
            core_profiles_in,
            mhd_linear_in,
            distributions_in_1,
            distributions_in_2,
            config_file,
            mpi_processes,
            actor_sandbox_options,
        )

        if equilibrium_out:
            if itime == 0:
                output.put(equilibrium_out, occurrence=output_ids["equilibrium"])
            else:
                output.put_slice(equilibrium_out, occurrence=output_ids["equilibrium"])
            print("*************************************")
            print("Output time = ", equilibrium_out.time[0])
            print(
                "Saved "
                + actor_name
                + " equilibrium under occurrence "
                + str(output_ids["equilibrium"])
            )
            print("*************************************")

        if mhd_linear_out:
            if (
                itime == 0
            ):  # Fix until mhd_linear is also independent of put/put_slice PR #600
                output.put(mhd_linear_out, occurrence=output_ids["mhd_linear"])
                print("*************************************")
                print("Initial Output")
                print(
                    "Saved "
                    + actor_name
                    + " mhd_linear under occurrence "
                    + str(output_ids["mhd_linear"])
                )
                print("*************************************")
            else:
                output.put_slice(mhd_linear_out, occurrence=output_ids["mhd_linear"])
                print("*************************************")
                print("Output time = ", mhd_linear_out.time[0])
                print(
                    "Saved "
                    + actor_name
                    + " mhd_linear under occurrence "
                    + str(output_ids["mhd_linear"])
                )
                print("*************************************")

        if core_profiles_out:
            output.put_slice(core_profiles_out, occurrence=output_ids["core_profiles"])
            print("*************************************")
            print("Output time = ", core_profiles_out.time[0])
            print(
                "Saved "
                + actor_name
                + " core_profiles under occurrence "
                + str(output_ids["core_profiles"])
            )
            print("*************************************")

        if distributions_out:
            if itime == 0:
                output.put(distributions_out, occurrence=output_ids["distributions"])
                print("*************************************")
                print("Initial Output")
                print(
                    "Saved "
                    + actor_name
                    + " mhd_linear under occurrence "
                    + str(output_ids["distributions"])
                )
                print("*************************************")
            else:
                output.put_slice(
                    distributions_out, occurrence=output_ids["distributions"]
                )
                print("*************************************")
                print("Output time = ", distributions_out.time[0])
                print(
                    "Saved "
                    + actor_name
                    + " distributions under occurrence "
                    + str(output_ids["distributions"])
                )
                print("*************************************")

    input.close()
    output.close()
