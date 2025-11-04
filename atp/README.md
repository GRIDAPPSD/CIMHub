# ATP Support

Scripts that make Alternative Transients Program (ATP) netlist files from CIM. An [ATP License](https://atp-emtp.org/) is required to run the netlists.

Files:

- _atpbes.py_: Generates a bulk power system model for ATP. Inputs come from the [BES directory](https://github.com/GRIDAPPSD/CIMHub/tree/feature/SETO/BES) of this repository.
- _atpfdr.py_: Generates a distribution feeder model for ATP. Inputs for some of the example feeders come from the [Powergrid Models](https://github.com/GRIDAPPSD/Powergrid-Models/tree/feature/SETO/platform) repository, or from the [OEDI directory](https://github.com/GRIDAPPSD/CIMHub/tree/feature/SETO/OEDI) of this repository, or from the [CPYDAR directory](https://github.com/GRIDAPPSD/CIMHub/tree/feature/SETO/CPYDAR) of this repository. Other example feeder models, like _Nantucket_ and _CEF2_, were obtained by PNNL from partner utilities under various NDAs. These may not be available to others.


