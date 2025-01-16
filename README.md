# EP-Stability-Workflow

Time-dependent Energetic Particles Stability workflow.

## Installation

The [EP Stability WF](https://git.iter.org/projects/WF/repos/ep-stability-wf/) depends on actors from various codes. These are: [LIGKA](https://git.iter.org/projects/STAB/repos/ligka/) and [HELENA](https://git.iter.org/projects/EQ/repos/helena/); [CHEASE](https://git.iter.org/projects/EQ/repos/chease), [HAGIS 1 and 2](https://git.iter.org/projects/STAB/repos/hagis) and finder (part of the LIGKA repository) are optional components.

If these actors are already provided as modules on your system, this is the easiest way to get them. These modules will also set the `$PYTHONPATH` variable appropriately such that the actors can be easily imported in python once loaded.

If you are building the actors yourself, see the instructions of each of the components. You will need to make sure that `$PYTHONPATH` is appropriately set to be able to import the actors in python.

The workflow itself (with appropriate dependencies on the actors) is installed as a module on the ITER SDCC cluster. For anyone using and not modifying the code, this is the easiest way to access the workflow.
See `module avail EP-Stability-WF` to see which releases are available.

## Usage

Once successfully installed and loaded, the workflow can be launched with `ep_gui` (if loaded from a module), or `$PATH_TO_REPOSITORY/ep_gui` otherwise.

For further details on how to use the workflow, please see the training materials, or the [ITER Confluence page](https://confluence.iter.org/display/IMP/EP-WF+-+Energetic+Particle+Stability+Workflow). Improved documentation is a work in progress.

## Contributing

Pull requests are welcome. For major changes, please open an JIRA issue first to discuss what you would like to change.
