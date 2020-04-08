# EP-Stability-Workflow

Time-dependent HELENA+LIGKA workflow.

## Installation

You will need [EP Stability WF](https://git.iter.org/projects/WF/repos/ep-stability-wf/),  [LIGKA](https://git.iter.org/projects/STAB/repos/ligka/) and [HELENA](https://git.iter.org/projects/EQ/repos/helena/) repositories:

1. After cloning all 3 repositories checkout the following branches:

for EP Stability WF and LIGKA
```bash
$ git checkout develop
```
for HELENA
```bash
$ git checkout EP_LIGKA
```

2. In EP Stabiliy WF file **module_start_python.sh** contains all the necessary modules to run the workflow and compile LIGKA and HELENA. It also contains the location of the **ACTOR_FOLDER** where the actors will be stored after running FC2K.

```bash
$ source module_start_python.sh
```
3. Both **LIGKA/ligka_kepler.xml** and **HELENA/helena_imas_0.1.xml** you must modify the paths according to your specific case.

4. Compile and run FC2K for LIGKA:
```bash
$ gmake LIGKA_KEP OPTS=IMAS,KEP,MPI,MUMS
```
5. Compile and run FC2K for HELENA:
```bash
$ gmake all
```
6. After the creation of the actors you should be able to go to **EP Stabiliy WF** and run:
```bash
$ python gui_HL.py
```

## Usage

**to be added**...

## Contributing
Pull requests are welcome. For major changes, please open an JIRA issue first to discuss what you would like to change.