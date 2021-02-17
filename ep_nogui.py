#!/usr/bin/env python

import sys, os

sys.path.append(os.getcwd())
sys.path.append('workflow')

import argparse

# Management of input arguments
parser = argparse.ArgumentParser(description='---- Run the EP workflow without the interface')
parser.add_argument("-c","--config_folder",help="input configuration folder", required=True)

args = vars(parser.parse_args())
config_folder  = args["config_folder"]

from workflow.run_workflow import workflow_EP
workflow_EP(config_folder)