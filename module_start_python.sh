module purge
module load libcerf/1.5-intel-2018a
module load IMAS/3.30.0-4.8.5
# module load IMAS/3.29.0-4.8.3
module load netCDF-Fortran/4.4.4-intel-2018a
module load PSPLINE/20181008-intel-2018a
module load MUMPS/5.1.2-intel-2018a-metis/
module load NAG/26-intel-2018a
module load SLATEC/4.1-iccifort-2018.1.163-GCC-6.4.0-2.28
module load ppplib
module load FC2K/4.13.2-Java-1.8
module load XMLlib/3.3.1-intel-2018a
module load lxml/4.2.0-intel-2018a-Python-3.6.4
module load sh/1.12.14-intel-2018a-Python-3.6.4
module load PLplot/5.13.0-intel-2018a-Java-1.8.0_162-Python-3.6.4
module load SPRNG/2.0b-intel-2018a

# CREATE FOLDER FOR ACTOR POOL
export ACTOR_FOLDER_WF=~/public/imas_actors #edit this line to best suit your needs
export ACTOR_FOLDER=public/imas_actors #edit this line to best suit your needs
export HAGIS2PATH=$ACTOR_FOLDER/hagis2/hagis2/native_wrapper/lib/def  # DO NOT CHANGE THIS LINE! (required by the finder)
# export HAGIS2PATH=develop/testingActors
mkdir -p ~/$ACTOR_FOLDER

# EXTEND PYTHON PATH AND AVOID DOUBLONS (where the actors are under the form: "/actor_name/version(if any)"
export PYTHONPATH=$ACTOR_FOLDER_WF/hagis1:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER_WF/hagis2:$PYTHONPATH
#export PYTHONPATH=$ACTOR_FOLDER_WF/hagis2_s:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER_WF/helena_imas:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER_WF/ligka:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER_WF/finder9:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER_WF/finder9_s:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER_WF/chease:$PYTHONPATH
export PYTHONPATH="$(perl -e 'print join(":", grep { not $seen{$_}++ } split(/:/, $ENV{PYTHONPATH}))')"
