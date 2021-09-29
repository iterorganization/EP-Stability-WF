#!/bin/bash

module purge

if [[ $HOSTNAME == hpc* ]]; then
    # hpc-login
    echo "Loading hpc modules..."
    module load libcerf/1.5-intel-2018a
    module load IMAS/3.32.0-4.9.0
    # module load IMAS/3.33.0-4.9.2-2020b
    module load netCDF-Fortran/4.4.4-intel-2018a
    module load PSPLINE/20181008-intel-2018a
    module load MUMPS/5.1.2-intel-2018a-metis/
    module load NAG/26-intel-2018a
    module load SLATEC/4.1-iccifort-2018.1.163-GCC-6.4.0-2.28
    module load ppplib
    module load FC2K/4.13.5-Java-1.8
    # module load FC2K/4.14.0-Java-11
    module load XMLlib/3.3.1-intel-2018a
    module load lxml/4.2.0-intel-2018a-Python-3.6.4
    module load sh/1.12.14-intel-2018a-Python-3.6.4
    module load PLplot/5.13.0-intel-2018a-Java-1.8.0_162-Python-3.6.4
    module load SPRNG/2.0b-intel-2018a
fi
if [[ $HOSTNAME == sdcc* ]]; then
    # sdcc-login
    echo "Loading sdcc modules..."
    module load libcerf/1.14-iccifort-2020.4.304
    module load IMAS/3.33.0-4.9.2-2020b
    # module load IMAS/3.32.0-4.9.0-2020b
    module load FFTW/3.3.8-intel-2020b
    module load netCDF-Fortran/4.5.3-iimpi-2020b
    module load PSPLINE/2.0.0-iimpi-2020b
    module load MUMPS/5.3.5-intel-2020b-metis
    module load NAG/26-intel-2020b
    module load PPPLIB/16.5.26-iccifort-2020.4.304
    module load FC2K/4.14.0-Java-11
    # module load FC2K/4.13.5-Java-11
    module load XMLlib/3.3.1-intel-2020b
    module load lxml/4.6.2-GCCcore-10.2.0
    module load sh/1.14.1-GCCcore-10.2.0
    module load impi/2019.9.304-iccifort-2020.4.304
    module load PLplot/5.15.0-intel-2020b
    module load SPRNG/2.0b-iimpi-2020b
    module load SLATEC/4.1-iccifort-2020.4.304
    module load ParMETIS/4.0.3-iimpi-2020b
    module load libdierckx/1993-GCCcore-10.2.0
    export EZSPLINE_NO_SUFF=TRUE
fi
echo "Done loading modules."


# CREATE FOLDER FOR ACTOR POOL

export ACTOR_FOLDER=${HOME}/public/imas_actors_sdcc #edit this line to best suit your needs
export HAGIS2PATH_s=$ACTOR_FOLDER/hagis2_s/hagis2_s/native_wrapper/lib/def  # DO NOT CHANGE THIS LINE! (required by the finder)

mkdir -p ~/$ACTOR_FOLDER

# EXTEND PYTHON PATH AND AVOID DOUBLONS (where the actors are under the form: "/actor_name/version(if any)"
export PYTHONPATH=$ACTOR_FOLDER/hagis1:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/hagis2:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/hagis2_s:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/helena_imas:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/ligka:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/finder9:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/chease:$PYTHONPATH
export PYTHONPATH="$(perl -e 'print join(":", grep { not $seen{$_}++ } split(/:/, $ENV{PYTHONPATH}))')"
