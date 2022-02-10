import imas
from imas import imasdef
import sys


def time_construction(ids_merge_param):
    time_index = ids_merge_param['Settings']['itime'][0]
    time_list_initial = time_index.split(",")
    time_list = []
    time_list_ligka_auto = []
    ligka_auto_index = 0
    for itime in time_list_initial:
        if "-" in itime:
            itime = itime.split("-")
            itime_list = list(range(int(itime[0]), int(itime[1])+1))
            ligka_auto_index = ligka_auto_index + \
                int(itime[1]) - int(itime[0]) + 1
            for i in itime_list:
                time_list.append(i)
        else:
            time_list.append(int(itime))
            ligka_auto_index = ligka_auto_index + 1
    for i in range(0, ligka_auto_index):
        time_list_ligka_auto.append(i)

    return time_list


def data_retrieve(ids_merge_param):
    """Method to retrieve data sets from the database

    Returns:
        [ids]: [for now only core_profiles]
    """
    if ids_merge_param['Inputs']['HDF5_1'][0] == 1:
        backend = imasdef.HDF5_BACKEND
    else:
        backend = imasdef.MDSPLUS_BACKEND

    input_1 = imas.DBEntry(backend, ids_merge_param['Inputs']['machine_in_1'][0], int(ids_merge_param['Inputs']
                                                                                      ['shot_in_1'][0]), int(ids_merge_param['Inputs']['run_in_1'][0]), ids_merge_param['Inputs']['user_in_1'][0])
    status, _ = input_1.open()
    if status != 0:
        print("Can't open the first selected dataset!", file=sys.stderr)
        sys.exit(1)

    time = input_1.partial_get('core_profiles', 'time')

    if ids_merge_param['Inputs']['HDF5_2'][0] == 1:
        backend = imasdef.HDF5_BACKEND
    else:
        backend = imasdef.MDSPLUS_BACKEND

    input_2 = imas.DBEntry(backend,
                           ids_merge_param['Inputs']['machine_in_2'][0], int(ids_merge_param['Inputs']['shot_in_2'][0]), int(ids_merge_param['Inputs']['run_in_2'][0]), ids_merge_param['Inputs']['user_in_2'][0])
    status, _ = input_2.open()
    if status != 0:
        print("Can't open the second selected dataset!", file=sys.stderr)
        sys.exit(1)

    return input_1, input_2, time


def data_writeout_create(ids_merge_param):

    if ids_merge_param['Output']['HDF5_out'][0] == 1:
        backend = imasdef.HDF5_BACKEND
    else:
        backend = imasdef.MDSPLUS_BACKEND

    # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
    print('=> Create output datafile')
    output = imas.DBEntry(backend,
                          ids_merge_param['Output']['machine_out'][0], int(ids_merge_param['Output']['shot_out'][0]), int(ids_merge_param['Output']['run_out'][0]), ids_merge_param['Output']['user_out'][0])
    output.create()

    return output


def data_step_writeout(output, core_profiles_out):

    output.put_slice(core_profiles_out, occurrence=0)

    print('*************************************')
    print('Output time = ', core_profiles_out.time[0])
    print('*************************************')


def profiles_get(core_profiles_in_1, core_profiles_in_2, ids_merge_param):
    nspecies = len(core_profiles_in_1.profiles_1d[0].ion)
    species = []
    for ispecies in range(nspecies):
        species.append(
            core_profiles_in_1.profiles_1d[0].ion[ispecies].label)
    print('Species present in core_profiles_in_1 are:', species)

    for ispecies in range(nspecies):
        if species[ispecies] == 'H' or species[ispecies] == 'H+':
            if ids_merge_param['Settings']['ni_H'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[ispecies].density_thermal = core_profiles_in_2.profiles_1d[0].ion[ispecies].density_thermal
                print('Replaced density for ', species[ispecies])
            if ids_merge_param['Settings']['Ti_H'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[
                    ispecies].temperature = core_profiles_in_2.profiles_1d[0].ion[ispecies].temperature
                print('Replaced temperature for ', species[ispecies])
        if species[ispecies] == 'T' or species[ispecies] == 'T+':
            if ids_merge_param['Settings']['ni_T'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[ispecies].density_thermal = core_profiles_in_2.profiles_1d[0].ion[ispecies].density_thermal
                print('Replaced density for ', species[ispecies])
            if ids_merge_param['Settings']['Ti_T'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[
                    ispecies].temperature = core_profiles_in_2.profiles_1d[0].ion[ispecies].temperature
                print('Replaced temperature for ', species[ispecies])
        if species[ispecies] == 'D' or species[ispecies] == 'D+':
            if ids_merge_param['Settings']['ni_D'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[ispecies].density_thermal = core_profiles_in_2.profiles_1d[0].ion[ispecies].density_thermal
                print('Replaced density for ', species[ispecies])
            if ids_merge_param['Settings']['Ti_D'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[
                    ispecies].temperature = core_profiles_in_2.profiles_1d[0].ion[ispecies].temperature
                print('Replaced temperature for ', species[ispecies])
        if species[ispecies] == 'Be' or species[ispecies] == 'Be+':
            if ids_merge_param['Settings']['ni_Be'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[ispecies].density_thermal = core_profiles_in_2.profiles_1d[0].ion[ispecies].density_thermal
                print('Replaced density for ', species[ispecies])
            if ids_merge_param['Settings']['Ti_Be'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[
                    ispecies].temperature = core_profiles_in_2.profiles_1d[0].ion[ispecies].temperature
                print('Replaced temperature for ', species[ispecies])
        if species[ispecies] == 'C' or species[ispecies] == 'C+':
            if ids_merge_param['Settings']['ni_C'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[ispecies].density_thermal = core_profiles_in_2.profiles_1d[0].ion[ispecies].density_thermal
                print('Replaced density for ', species[ispecies])
            if ids_merge_param['Settings']['Ti_C'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[
                    ispecies].temperature = core_profiles_in_2.profiles_1d[0].ion[ispecies].temperature
                print('Replaced temperature for ', species[ispecies])
        if species[ispecies] == 'Ne' or species[ispecies] == 'Ne+':
            if ids_merge_param['Settings']['ni_Ne'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[ispecies].density_thermal = core_profiles_in_2.profiles_1d[0].ion[ispecies].density_thermal
                print('Replaced density for ', species[ispecies])
            if ids_merge_param['Settings']['Ti_Ne'][0] == 1:
                core_profiles_in_1.profiles_1d[0].ion[
                    ispecies].temperature = core_profiles_in_2.profiles_1d[0].ion[ispecies].temperature
                print('Replaced temperature for ', species[ispecies])

    return core_profiles_in_1


def ids_compare(ids_merge_param):
    time_index_list = time_construction(ids_merge_param)
    ntime = len(time_index_list)
    input_1, input_2, time = data_retrieve(ids_merge_param)
    output = data_writeout_create(ids_merge_param)
    for itime in time_index_list:
        print('Time = ', time[itime], ' s, itime = ', itime, '/', ntime-1)

        core_profiles_in_1 = input_1.get_slice(
            'core_profiles', time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=0)

        core_profiles_in_2 = input_2.get_slice(
            'core_profiles', time[itime], imasdef.PREVIOUS_SAMPLE, occurrence=0)

        core_profiles_out = profiles_get(
            core_profiles_in_1, core_profiles_in_2, ids_merge_param)

        data_step_writeout(output, core_profiles_out)

    input_1.close()
    input_2.close()
    output.close()
