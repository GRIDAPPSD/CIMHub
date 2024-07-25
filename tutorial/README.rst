# CIMHub Tutorial

Copyright (c) 2017-2022, Battelle Memorial Institute

## End User Instructions

See [ReadTheDocs Tutorial](https://cimhub.readthedocs.io/en/latest/Tutorial.html) 
for installation and tutorial steps.

## CSV Column File Map

The columns in _aug11slow.csv_, _aug11slow.hdf5_,  _15min/aug11avg.csv_ and _15min/aug11avg.hdf5_ are:

- *timestamp*: local date and time
- *distribution\_load*: substation real and reactive power in rectangular format, [VA]. Use *sub\_p* and *sub\_q* for convenience.
- *positive\_sequence\_voltage*: substation line-to-neutral positive sequence voltage in rectangular format, [V]
- *power\_in*: feeder-head input power in line L115, equal to *distribution\_load* except for some losses
- *current\_in\_A*: feeder-head phase A input current in line L115 in rectangular format, [A]. Use *fdrA* for convenience.
- *current\_in\_B*: feeder-head phase B input current in line L115 in rectangular format, [A]. Use *fdrB* for convenience.
- *current\_in\_C*: feeder-head phase C input current in line L115 in rectangular format, [A]. Use *fdrC* for convenience.
- *ld\_s35a:measured\_power*: power into a load _ld\_s35a_ that is connected to the feeder primary, in rectangular format, [VA]. The next 4 columns are like this, for different primary-connected loads.
- *7\_pvmtr:measured\_power*: power out of PV inverter at *7\_pvmtr* in rectangular format, [VA]. This follows load sign convention, so the real power is negative. The inverters operate at unity power factor, so the reactive power is zero. The next 13 columns are like this, for different PV inverters.
- *temperature*: outside air temperature, [degF]
- *humidity*: relative air humidity, [pu]
- *solar\_flux*: total solar irradiation, rescaled from GridLAB-D's default mph units to [W/m2]
- *pressure*: outside air pressure, [mbar]
- *wind\_speed*: average wind speed, [mph]
- *xf\_xfs49a:power\_in*: power into a single-phase, center-tap transformer _xf\_xfs49a_ that serves a triplex load _ld\_49a_, in rectangular format, [VA]. Transformer losses are included with load power. The next 81 columns are like this, for different secondary-connected loads.
- *sub\_p*: real part of *distribution\_load* in [W]
- *sub\_q*: imaginary part of *distribution\_load* in [var] 
- *fdrIa*: magnitude of *current\_in\_A* in [A]
- *fdrIb*: magnitude of *current\_in\_B* in [A]
- *fdrIc*: magnitude of *current\_in\_C* in [A]
- *pvS*: summation of PV apparent power from _\*pvmtr_ columns, in [VA].
- *primaryS*: summation of primary-connected load apparent power from _\*ld\*_ colmuns, in [VA].
- *secondaryS*:  summation of single-phase, center-tap transformer apparent power from _xf\*_ colmuns, in [VA].
- *pvP*: real part of *pvS*, in [W]
- *primaryP*: real part of *primaryS*, in [W]
- *secondaryP*: real part of *secondaryS*, in [W]

Load Flow Comparisons
---------------------

The test cases in *cases.json* are configured as decribed in 
`Test Case Configuration <../README.rst#Test-Case-Configuration>`_. The
`Command-Line Reference <../README.rst#Command-Line-Reference>`_ describes available
**export\_options** for each case.

The command *python3 onestep.py* runs the test cases.

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on 
interpreting the `Results <onestep.inc>`_.

..
    literalinclude:: onestep.inc
   :language: none
   However, GitHub README will not support include files


