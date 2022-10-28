#!/bin/bash
# Bamboo Load modules script
# Stage 0: Load necessary modules
# Set up environment for compilation

. /usr/share/Modules/init/sh
module use /work/imas/etc/modules/all

module purge

module load LIGKA/1.0.1-intel-2020b-DD-3.35.0
module load HELENA/2.0.1-intel-2020b-DD-3.35.0
module load lxml/4.6.2-GCCcore-10.2.0
