#!/usr/bin/env python

import sys, os

sys.path.append(os.getcwd())
sys.path.append('workflow')
sys.path.append('workflow/input')

from workflow.run_physics_code_final_no_kep import run_HL_noKEP
run_HL_noKEP()