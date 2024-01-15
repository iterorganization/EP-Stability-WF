import imas
import sys
import os
from ep_stability_wf.workflow.functions_wf import time_construction


def data_retrieve(ids_merge_param):
    """Method to retrieve data sets from the database

    Returns:
        [ids]: [for now only core_profiles]
    """
    if int(ids_merge_param["Inputs"]["HDF5_1"][0]):
        backend = imas.imasdef.HDF5_BACKEND
    else:
        backend = imas.imasdef.MDSPLUS_BACKEND

    input_1 = imas.DBEntry(
        backend,
        ids_merge_param["Inputs"]["machine_in_1"][0],
        int(ids_merge_param["Inputs"]["shot_in_1"][0]),
        int(ids_merge_param["Inputs"]["run_in_1"][0]),
        ids_merge_param["Inputs"]["user_in_1"][0],
    )
    status, _ = input_1.open()
    if status != 0:
        print("Can't open the first selected dataset!", file=sys.stderr)
        sys.exit(1)

    time = input_1.partial_get("core_profiles", "time")

    if int(ids_merge_param["Inputs"]["HDF5_2"][0]):
        backend = imas.imasdef.HDF5_BACKEND
    else:
        backend = imas.imasdef.MDSPLUS_BACKEND

    input_2 = imas.DBEntry(
        backend,
        ids_merge_param["Inputs"]["machine_in_2"][0],
        int(ids_merge_param["Inputs"]["shot_in_2"][0]),
        int(ids_merge_param["Inputs"]["run_in_2"][0]),
        ids_merge_param["Inputs"]["user_in_2"][0],
    )
    status, _ = input_2.open()
    if status != 0:
        print("Can't open the second selected dataset!", file=sys.stderr)
        sys.exit(1)

    return input_1, input_2, time


def data_writeout_create(ids_merge_param):
    if int(ids_merge_param["Output"]["HDF5_out"][0]):
        backend = imas.imasdef.HDF5_BACKEND
    else:
        backend = imas.imasdef.MDSPLUS_BACKEND
        machine_out = ids_merge_param["Output"]["machine_out"][0]
        version = os.getenv("IMAS_VERSION")[0]
        output_folder = os.path.join(
            os.getenv("HOME"), "public/imasdb/{}/{}/0".format(machine_out, version)
        )
        if not os.path.isdir(output_folder):
            print(
                "-- Create local database folder for output file " + output_folder,
                file=sys.stdout,
            )
            os.makedirs(output_folder)

    # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
    print("=> Create output datafile")
    output = imas.DBEntry(
        backend,
        ids_merge_param["Output"]["machine_out"][0],
        int(ids_merge_param["Output"]["shot_out"][0]),
        int(ids_merge_param["Output"]["run_out"][0]),
        os.getenv("USER"),
    )

    status, _ = output.create()
    if status != 0:
        print("Something's wrong, data-entry creation failed")

    return output


def data_step_writeout(output, core_profiles_out):
    output.put_slice(core_profiles_out, occurrence=0)

    print("*************************************")
    print(f"Output time = {core_profiles_out.time[0]}")
    print("*************************************")


def profiles_get_species(core_profiles_in_1, core_profiles_in_2, ids_merge_param):
    ion_profs_1 = core_profiles_in_1.profiles_1d[0].ion
    ion_profs_2 = core_profiles_in_2.profiles_1d[0].ion
    species = [spec.label for spec in ion_profs_1]
    print("Species present in core_profiles_in_1 are:", species)

    ion_implement_list = ["H", "D", "T", "Be", "C", "Ne"]
    # ion_labels = {f'{ion}+':str(ion) for ion in ion_implement_list}

    for prof_spec_1, prof_spec_2 in zip(ion_profs_1, ion_profs_2):
        species_label = prof_spec_1.label
        # species_label_tmp = ion_labels.get(species_label, species_label)
        species_label_tmp = species_label.split("+")[0]

        # Skip if ions not one of H,D,T,Be,C,Ne
        if species_label_tmp not in ion_implement_list:
            continue

        if int(ids_merge_param["Settings"][f"ni_{species_label_tmp}"][0]):
            prof_spec_1.density_thermal = prof_spec_2.density_thermal
            print(f"Replaced density for {species_label}")
        if int(ids_merge_param["Settings"][f"Ti_{species_label_tmp}"][0]):
            prof_spec_1.temperature = prof_spec_2.temperature
            print(f"Replaced Temperature for {species_label}")

    return core_profiles_in_1


def ids_compare(ids_merge_param):
    time_index_list, _ = time_construction(ids_merge_param["Settings"]["itime"][0])
    ntime = len(time_index_list)
    input_1, input_2, time = data_retrieve(ids_merge_param)
    output = data_writeout_create(ids_merge_param)
    for i, itime in enumerate(time_index_list):
        print(f"Time = {time[itime]} s, itime = {i}/{ntime-1}")

        core_profiles_in_1 = input_1.get_slice(
            "core_profiles", time[itime], imas.imasdef.PREVIOUS_SAMPLE, occurrence=0
        )

        core_profiles_in_2 = input_2.get_slice(
            "core_profiles", time[itime], imas.imasdef.PREVIOUS_SAMPLE, occurrence=0
        )

        core_profiles_out = profiles_get_species(
            core_profiles_in_1, core_profiles_in_2, ids_merge_param
        )

        data_step_writeout(output, core_profiles_out)

        if int(ids_merge_param["Settings"]["Equilibrium_copy"][0]):
            print("Exporting Equilibrium also in the new DB!")
            equilibrium_out = input_1.get_slice(
                "equilibrium", time[itime], imas.imasdef.PREVIOUS_SAMPLE, occurrence=0
            )
            data_step_writeout(output, equilibrium_out)

    print("IDS merge Completed!")
    input_1.close()
    input_2.close()
    output.close()
