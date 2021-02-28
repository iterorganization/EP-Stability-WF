# EP-Stability-Workflow

Time-dependent Energetic Particles Stability workflow.

## Installation

You will need [EP Stability WF](https://git.iter.org/projects/WF/repos/ep-stability-wf/),  [LIGKA/finder](https://git.iter.org/projects/STAB/repos/ligka/), [HELENA](https://git.iter.org/projects/EQ/repos/helena/) and [HAGIS 1 and 2](https://git.iter.org/projects/STAB/repos/hagis/browse) repositories:

1. After cloning all 4 repositories checkout the following branches:

for EP Stability WF and LIGKA/finder
```bash
$ git checkout develop
```
for HELENA
```bash
$ git checkout EP_LIGKA
```
for HAGIS 1 and 2
```bash
$ git checkout feature/IMAS
```


2. In EP Stabiliy WF file **module_start_python.sh** contains all the necessary modules to run the workflow and build the actors LIGKA, HELENA and HAGIS . It also contains the location of the **ACTOR_FOLDER** where the actors will be stored after running FC2K (one can modify this to fit his own needs)

```bash
$ source module_start_python.sh
```

3. Compile and run FC2K for LIGKA:
```bash
$ gmake LIGKA_WF OPTS=IMAS,WF,MPI,MUMPS
```
4. Compile and run FC2K for HELENA:
```bash
$ gmake all
```
5. Compile and run FC2K for HAGIS 1:
```bash
$ cd src/hagis1
$ gmake hagis1_wf OPTS=IMAS,WF 
```
6. Compile and run FC2K for HAGIS 2 MPI:
```bash
$ cd src/hagis2
$ gmake hagis2_wf OPTS=MPI,IMAS,WF
```
6. Compile and run FC2K for HAGIS 2 serial:
```bash
$ cd src/hagis2
$ gmake hagis2_wf_s OPTS=IMAS,WF
```
7. Compile and run FC2K for finder_MPI:
```bash
$ cd ligka/finder/src
$ gmake finder9_wf OPTS=IMAS,MPI,WF
```
8. After the creation of the actors you should be able to go to **EP Stabiliy WF** and run:
```bash
$ python gui_HL.py
```

## Usage

**to be added**...

## Contributing
Pull requests are welcome. For major changes, please open an JIRA issue first to discuss what you would like to change.
