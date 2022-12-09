import imas
import sys
import os
import numpy as np


def ids_read(backend_in, database_in, shot_no, run_in, user_in, ids_name, occurrence_in):
    """Method to retrieve data from the database """
    input = imas.DBEntry(backend_in,
                         database_in, shot_no, run_in, user_in)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)
    return input.get(ids_name, occurrence=occurrence_in)


def ids_fill(backend_in, backend_out, database_in, database_out,
             shot_no, run_in, run_out, user_in, ids_name, occurrence_in, occurrence_out, db_exists):

    # CREATE OUTPUT OBJECT REFERENCE, IN VIEW OF SAVING RESULTS TO LOCAL DB
    output = imas.DBEntry(backend_out,
                          database_out, shot_no, run_out, os.getenv('USER'))
    output_folder = os.getenv('HOME')+'/public/imasdb/' + \
        database_out+'/3/0'
    if os.path.isdir(output_folder) == False:
        print('-- Create local database for output file ' +
              output_folder)
        try:
            os.makedirs(output_folder)
        except FileExistsError:
            # Calling twice in parallel can give this error. Ignore
            pass
    if db_exists:
        print('=> Open output datafile')
        output.open()
    else:
        print('=> Create output datafile')
        output.create()

    ids_out = ids_read(backend_in, database_in, shot_no,
                       run_in, user_in, ids_name, occurrence_in)

    # Modify IDS HERE
    # e.g. depends on ids structure: dd_versio 3.35
    # https://sharepoint.iter.org/departments/POP/CM/IMDesign/Data%20Model/CI/imas-3.35.0/html_documentation.html
    # ids_out.time_slice[0].profiles_1d.q = np.array([0, 1, 2])

    output.put(ids_out, occurrence_out)
    print('Done with ', ids_name)

    output.close()


if __name__ == "__main__":
    # other option is HDF5_BACKEND
    backend_in = imas.imasdef.MDSPLUS_BACKEND
    backend_out = imas.imasdef.MDSPLUS_BACKEND
    database_in = 'iter'
    database_out = 'ids_modification_test'
    shot_no = 130012
    run_in = 2
    run_out = 0
    user_in = 'public'
    # other options are 'mhd_linear','core_profiles', etc.
    ids_name = 'equilibrium'
    occurrence_in = 0
    occurrence_out = 0
    # If following option is True, then it will not create a new DB, but it will append to existing one
    # otherwise, it will delete /create the former one
    db_exists = False

    ids_fill(backend_in, backend_out, database_in, database_out,
             shot_no, run_in, run_out, user_in, ids_name, occurrence_in, occurrence_out, db_exists)
