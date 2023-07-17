#!/bin/bash

python3 -mvenv --system-site-packages wf_pip
source wf_pip/bin/activate
python3 -mpip install cerberus flake8
