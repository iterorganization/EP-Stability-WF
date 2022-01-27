import imas
import sys
import os
from imas import imasdef


def converter(backend_from, backend_to, database_from, database_to, shot_no, run_from, run_to, user_from, ids_dict):

    input = imas.DBEntry(backend_from, database_from,
                         shot_no, run_from, user_from)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)

    # OPEN OUTPUT OBJECT, IN VIEW OF SAVING RESULTS TO LOCAL DB
    print('=> Create output datafile')
    output = imas.DBEntry(backend_to,
                          database_to, shot_no, run_to, os.getenv('USER'))
    output.create()

    for ids_name in ids_dict:
        ids_out = input.get(ids_name, ids_dict[ids_name][0])

        output.put(ids_out, ids_dict[ids_name][1])
        print('Done with ', ids_name)

    print('Done converting.')

    input.close()
    output.close()


if __name__ == "__main__":
    backend_from = imasdef.HDF5_BACKEND
    backend_to = imasdef.MDSPLUS_BACKEND
    database_from = ''
    database_to = ''
    shot_no = 0
    run_from = 0
    run_to = 0
    user_from = ''

    # FORM OF THE DICT IS: IDS NAME as key, first entry IDS_OCCURRENCE IN and second entry IDS_OCCURRENCE OUT.
    ids_dict = {'equilibrium': (0, 1), 'mhd_linear': (0, 1)}

    converter(backend_from, backend_to, database_from, database_to,
              shot_no, run_from, run_to, user_from, ids_dict)
