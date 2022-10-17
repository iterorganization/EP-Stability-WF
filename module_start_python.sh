#!/bin/bash

module purge
export PYTHONPATH=''
if [[ $(hostname) == *"iter.org"* ]] || [[ $(dnsdomainname) == *"iter.org"* ]]; then
    OSDESC=`lsb_release -d`
    if [[ $OSDESC == *"CentOS Linux release 7"* ]]; then
        # hpc-login
        echo "Loading hpc modules..."
        module load libcerf/1.5-intel-2018a
        module load IMAS/3.32.0-4.9.0
        module load netCDF-Fortran/4.4.4-intel-2018a
        module load PSPLINE/20181008-intel-2018a
        module load MUMPS/5.1.2-intel-2018a-metis/
        module load NAG/26-intel-2018a
        module load SLATEC/4.1-iccifort-2018.1.163-GCC-6.4.0-2.28
        module load ppplib
        module load FC2K/4.13.5-Java-1.8
        module load XMLlib/3.3.1-intel-2018a
        module load lxml/4.2.0-intel-2018a-Python-3.6.4
        module load sh/1.12.14-intel-2018a-Python-3.6.4
        module load PLplot/5.13.0-intel-2018a-Java-1.8.0_162-Python-3.6.4
        module load SPRNG/2.0b-intel-2018a
    elif [[ $OSDESC == *"CentOS Linux release 8"* ]]; then
        # sdcc-login
        echo "Loading sdcc modules..."
        module load LIGKA/1.0.0-intel-2020b-DD-3.35.0
        module load HELENA/2.0.0-intel-2020b-DD-3.35.0
        module load lxml/4.6.2-GCCcore-10.2.0
    else
        echo "WHERE AM I??? Could not load modules!"
    fi
else
    #gateway
    echo "Loading gateway modules..."
    module load cineca-dev
    module load imasenv/3.35.0/intel/17.0/rc
    module unload itm-qt/5.8.0

    module load imas-pyal/1.3.5
    module load nag/mark26--binary
    module load fftw/3.3.4--intelmpi--2017--binary
    module load zlib/1.2.8--gnu--6.1.0
    module load szip/2.1--gnu--6.1.0
    module load hdf5/1.8.17--intel--pe-xe-2017--binary
    module load netcdf/4.4.1--intel--pe-xe-2017--binary
    module load netcdff/4.4.4--intel--pe-xe-2017--binary
    module load pspline/20161207
    module load parmetis/4.0.3--intelmpi--2017--binary
    module load metis/5.1.0--intel--pe-xe-2017--binary
    module load mumps/5.0.1--intelmpi--2017--binary
    module load xmllib/3.3.1/intel/17.0
    module load mkl/2017--binary
    module load pspline/20190408

    export IPP_USER=pwl
    export PPPLIB_HOME=/afs/eufus.eu/user/g/g2plaube/public/lib/
    export DIERCKX_HOME=/afs/eufus.eu/user/g/g2plaube/public/lib/
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH\:/afs/eufus.eu/user/g/g2plaube/public/lib/
    export MUMPS_5=TRUE
    export HELENA_XML=helena_imas_gateway.xml

    # CREATE FOLDER FOR ACTOR POOL (for gateway mandatory, no modules yet)
    export ACTOR_FOLDER=${HOME}/public/imas_actors #edit this line to best suit your needs
    export HAGIS2PATH_s=$ACTOR_FOLDER/hagis2_s/hagis2_s/native_wrapper/lib/def  # DO NOT CHANGE THIS LINE! (required by the finder)

    mkdir -p $ACTOR_FOLDER

    # EXTEND PYTHON PATH AND AVOID DOUBLONS (where the actors are under the form: "/actor_name/version(if any)"

    export PYTHONPATH=$ACTOR_FOLDER/hagis1:$PYTHONPATH
    export PYTHONPATH=$ACTOR_FOLDER/hagis2:$PYTHONPATH
    export PYTHONPATH=$ACTOR_FOLDER/hagis2_s:$PYTHONPATH
    export PYTHONPATH=$ACTOR_FOLDER/helena:$PYTHONPATH
    export PYTHONPATH=$ACTOR_FOLDER/ligka:$PYTHONPATH
    export PYTHONPATH=$ACTOR_FOLDER/finder9:$PYTHONPATH
    export PYTHONPATH=$ACTOR_FOLDER/chease:$PYTHONPATH
    export PYTHONPATH="$(perl -e 'print join(":", grep { not $seen{$_}++ } split(/:/, $ENV{PYTHONPATH}))')"
fi
