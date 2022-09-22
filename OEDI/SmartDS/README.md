# SmartDS Feeder for OEDI

Copyright (c) 2017-2022, Battelle Memorial Institute

## Process

Changes to model as downloaded, to solve in OpenDSS 9.4.1.2 and OpenDSSCmd 1.7.5:

- Comment out yearly loadshape attributes in Loads.dss
- Comment out yearly loadshape attributes in PVSystems.dss
- Change kvarlimit to kvarmax in PVSystems.dss
    * Todo: set kvarmaxabs=kvarmax on each?
- Comment out the Loadshapes in Master.dss
- Disable inverter controls
    * batchedit invcontrol..* enabled=no
    * This was necessary for convergence
- Specify phases=2 on 926 PVSystems that had phases=1, phasing .1.2, kV=0.240
    * The default conn=wye was incorrect on phases=1, phasing .1.2
    * Tried to specify conn=d on these 926 PVSystems, keeping phases=1, but solution did not converge. Maybe one of these PVSystems doesn't have a parallel load to provide ground reference?

```
  OpenDSS branch flow in LINE.L(R:P9UDT12866-P9UHS16_1247) from P9UDT12866-P9UHS16_1247X, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7415.54  0.0000    242.74 -0.5582   1526.854 + j   953.343     AB    12844.09  0.5236
    B   7415.54 -2.0944    181.35 -2.8058   1018.649 + j   878.034     BC    12844.09 -1.5708
    C   7415.54  2.0944    206.04  1.4355   1208.069 + j   935.387     CA    12844.09  2.6180
    Total S =  3753.572 + j  2766.764
  OpenDSS branch flow in LINE.L(R:P9UDT12866-P9UHS16_1247) from P9UDT12866-P9UHS16_1247X, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7415.54  0.0000    227.99 -0.5498   1441.545 + j   883.380     AB    12844.09  0.5236
    B   7415.54 -2.0944    168.15 -2.7751    969.018 + j   784.695     BC    12844.09 -1.5708
    C   7415.54  2.0944    186.72  1.4317   1091.538 + j   851.883     CA    12844.09  2.6180
    Total S =  3502.101 + j  2519.958
SmartDS          Nbus=[  8515,  8515,     0] Nlink=[ 14224, 14224,     0] MAEv=[ 0.0041,-1.0000] MAEi=[   0.7853,  -1.0000]
```

