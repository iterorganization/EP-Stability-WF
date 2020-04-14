module purge
module load libcerf
module load IMAS/3.27.0-4.7.1
module load netCDF-Fortran/4.4.4-intel-2018a
module load PSPLINE/20181008-intel-2018a
module load MUMPS/5.1.2-intel-2018a-metis/
module load NAG
module load SLATEC/4.1-iccifort-2018.1.163-GCC-6.4.0-2.28
module load ppplib
module load FC2K/4.9.0
module load XMLlib/3.2.0-intel-2018a
module load PyAL/1.3.1-intel-2018a-Python-3.6.4
module load lxml/4.2.0-intel-2018a-Python-3.6.4
#module load TensorFlow/1.8.0-intel-2018a-Python-3.6.4

# CREATE FOLDER FOR ACTOR POOL
export ACTOR_FOLDER=~/develop/imas_actors #edit this line to best suit your needs
mkdir -p $ACTOR_FOLDER

# EXTEND PYTHON PATH AND AVOID DOUBLONS (where the actors are under the form: "/actor_name/version(if any)"
export PYTHONPATH=$ACTOR_FOLDER/helena_imas/0.1/:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/ligka:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/chease:$PYTHONPATH
export PYTHONPATH="$(perl -e 'print join(":", grep { not $seen{$_}++ } split(/:/, $ENV{PYTHONPATH}))')"
