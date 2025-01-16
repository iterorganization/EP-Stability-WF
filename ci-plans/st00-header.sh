#!/bin/bash
# Bamboo Load modules script
# Stage 0: Load necessary modules
# Set up environment for compilation

. /etc/profile.d/modules.sh
module use /work/imas/etc/modules/all

module purge

set -e

module load \
lxml/4.9.3-GCCcore-13.2.0 \
Tkinter/3.11.5-GCCcore-13.2.0 \
PyYAML/6.0.1-GCCcore-13.2.0 \
HELENA/2.1.0-intel-2023b-DD-3.42.0 \
LIGKA/2.1.0-intel-2023b-DD-3.42.0 \
CHEASE/14.5-intel-2023b-DD-3.42.0

module list


export IMAS_AL_DISABLE_VALIDATE=1
