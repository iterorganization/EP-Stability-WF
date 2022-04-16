#!/usr/bin/env python
import imas
import os
import yaml
from cerberus import Validator
from imas import imasdef
import argparse


def read_data(input, ids_field, occurrence):
    """Method to retrieve data from the database

    Returns:
        [ids_var]: [field of ids object]
    """

    ids_var = input.partial_get(
        'mhd_linear', ids_field, occurrence=occurrence)

    return (ids_var)


def test_ids(backend, database, user, shot_no, run, occurrence, validation_schema):
    input = imas.DBEntry(backend, database, shot_no, run, user)
    status, _ = input.open()
    with open(validation_schema, 'r') as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    v = Validator()
    data_dict = {}
    for ids_field in parsed_yaml:
        ids_var = read_data(input, ids_field, occurrence)
        data_dict[ids_field] = ids_var
    input.close()
    if v.validate(data_dict, parsed_yaml):
        print(f'Data is valid for occurrence {occurrence}!')
    else:
        print(f'Invalid data: {v.errors}')


if __name__ == "__main__":
    # Management of input arguments
    parser = argparse.ArgumentParser(
        description='---- Configuration for testing different mhd_linear occurences and cases')
    parser.add_argument("-o", "--occurrence_list", nargs="+", type=int,
                        help="input occurrence list", required=True)
    parser.add_argument("-v", "--validation_schema",
                        help="input validation schema", default="./ci-plans/files/03-output/validation-01-hl5.yaml")
    parser.add_argument("-d", "--database",
                        help="input Database", default="ci_test_DB")
    parser.add_argument("-s", "--shot", type=int,
                        help="input Database", default="130012")
    parser.add_argument("-r", "--run", type=int,
                        help="input Database", default="10")
    args = parser.parse_args()

    backend = imasdef.MDSPLUS_BACKEND
    database = args.database
    user = os.getenv('USER')
    shot_no = args.shot
    run = args.run
    occurrence_list = args.occurrence_list
    validation_schema = args.validation_schema

    for occurrence in occurrence_list:
        test_ids(backend, database, user, shot_no,
                 run, occurrence, validation_schema)
