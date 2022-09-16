# SmartDS Feeder for OEDI

Copyright (c) 2017-2022, Battelle Memorial Institute

## Process

Changes to model as downloaded, to solve in OpenDSS 9.4.1.2 and OpenDSSCmd 1.7.5:

1. Comment out yearly loadshape attributes in Loads.dss
2. Comment out yearly loadshape attributes in PVSystems.dss
3. Change kvarlimit to kvarmax in PVSystems.dss
   a. Todo: set kvarmaxabs=kvarmax on each?
4. Comment out the Loadshapes in Master.dss
5. Disable inverter controls
   a. batchedit invcontrol..* enabled=no
   b. was necessary for convergence

