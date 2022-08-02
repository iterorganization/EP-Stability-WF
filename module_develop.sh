module purge
module load IMAS/3.36.0-4.10.2-2020b
module load FC2K/4.14.0-Java-11
module load XMLlib/3.3.1-intel-2020b

#HELENA
module load PPPLIB/16.5.26-iccifort-2020.4.304
module load libdierckx/1993-GCCcore-10.2.0

#LIGKA
module load libcerf/1.14-iccifort-2020.4.304
module load FFTW/3.3.8-intel-2020b
module load netCDF-Fortran/4.5.3-iimpi-2020b
module load PSPLINE/2.0.0-iimpi-2020b
module load MUMPS/5.3.5-intel-2020b-metis
module load NAG/26-intel-2020b
module load lxml/4.6.2-GCCcore-10.2.0
module load sh/1.14.1-GCCcore-10.2.0
module load impi/2019.9.304-iccifort-2020.4.304
module load PLplot/5.15.0-intel-2020b
module load SPRNG/2.0b-iimpi-2020b
module load SLATEC/4.1-iccifort-2020.4.304
module load ParMETIS/4.0.3-iimpi-2020b
export EZSPLINE_NO_SUFF=TRUE

# #CHEASE
# module load INTERPOS/9.1.0-intel-2020b
module load CHEASE/1.0.9-intel-2020b-DD-3.36.0



export ACTOR_FOLDER=~/public/imas_actors_sdcc
# export PYTHONPATH=$ACTOR_FOLDER/chease:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/helena:$PYTHONPATH
export PYTHONPATH=$ACTOR_FOLDER/ligka:$PYTHONPATH
export PYTHONPATH="$(perl -e 'print join(":", grep { not $seen{$_}++ } split(/:/, $ENV{PYTHONPATH}))')"