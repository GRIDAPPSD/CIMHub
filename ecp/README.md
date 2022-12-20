# CIMHub Test Cases for EnergyConnectionProfile

Copyright (c) 2021-2022, Battelle Memorial Institute

The _EnergyConnectionProfile_ CIM extension class supports the conversion of shapes,
curves, players, and schedules ("profiles") for time-series simulations in OpenDSS and
GridLAB-D. References from the network model components to the profiles convert through 
CIMHub. The user has to manage the profile data separately, in format suitable for
the simulator, i.e., CIM classes are not used for the profile data itself.

## Process

The test cases are executed as follows:

1. Start the Blazegraph engine
2. Invoke `python3 onestep.py` to perform the base model conversion
3. Invoke `python3 onestepa.py` to perform the time-series model conversion for OpenDSS

The test cases are configured by entries in the `cases.json` file. These cases are:

1. _ecp\_daily_ tests the OpenDSS _daily_ shape with solar, storage, load, and generator components
2. _ecp\_duty_ tests the OpenDSS _duty cycle_ shape with solar and storage components
3. _ecp\_growthcvr_ tests the OpenDSS _loadgrowth_ and _cvrcurve_ with Conservation Load Reduction (CVR) loads
4. _ecp\_harmonic_ tests the OpenDSS _spectrum_ with solar, storage, load, and generator components
5. _ecp\_temperature_ tests the OpenDSS _daily_ and _Tdaily_ shaps with solar components
6. _ecp\_yearly_ tests the OpenDSS _yearly_ shape with a load component

The `cases.json` file contains an array of case definitions, where each case has the following attributes:

- _mRID_ master resource identifier (mRID) of the Feeder to select from Blazegraph for this case. Most CIM objects have a mRID, which is a universally unique identifier (UUID) following the Web standard RFC 4122.
- _root_ common part of case file names, usually matches the incoming OpenDSS circuit name
- _inpath\_dss_ relative path to incoming OpenDSS models, including shapes. Will store base _time-series_ power flow results in this example. Must be specified. In this example, it's `./base/`
- _dssname_ file name of the incoming "master" OpenDSS file, often _root.dss_
- _path\_xml_ relative path to output CIM XML files, including archived UUID files to persist the mRIDs. Stores the base _snapshot_ power flow results. In this example, it's `./xml/`
- _outpath\_dss_ relative path to output OpenDSS files, `./dss/` in this example. WARNING: contents may be deleted and rewritten on subsequent exports. To forego OpenDSS export, omit this attribute, or specify as None or an empty string.
- _outpath\_glm_ relative path to output GridLAB-D files, `./glm/` in this example. WARNING: contents may be deleted and rewritten on subsequent exports. To forego GridLAB-D export, omit this attribute, or specify as None or an empty string.
- _outpath\_csv_ relative path to output comma-separated value (CSV) files, `./csv/` in this example. WARNING: contents may be deleted and rewritten on subsequent exports. To forego CSV export, omit this attribute, or specify as None or an empty string.
- _glmvsrc_ RMS line-to-neutral voltage for the GridLAB-D _substation_ source. Use nominal line-to-line voltage, divided by square root of three, then multiplied by per-unit voltage from the OpenDSS circuit definition.
- _bases_ array of nominal line-to-line voltage bases for power flow comparisons of per-unit voltages. Specify in ascending order, not including 208.0, which is always considered.
- _substation_ optional name of the CIM Substation. This may be used to help organize multiple feeders.
- _region_ optional name of the CIM GeographicalRegion. This may be used to help organize multiple feeders.
- _subregion_ optional name of the CIM SubGeographicalRegion. This may be used to help organize multiple feeders.
- _substationID_ optional mRID of the CIM Substation. This may be used to help organize multiple feeders.
- _regionID_ optional mRID of the CIM GeographicalRegion. This may be used to help organize multiple feeders.
- _subregionID_ optional mRID of the CIM SubGeographicalRegion. This may be used to help organize multiple feeders.
- _export\_options_ command-line options passed to the Java model exporter.  See [Command-line Reference](../README.md) for more details.
- _check\_branches_ optional array of individual branches to compare pre-conversion and post-conversion snapshot power flow solutions. Either the _dss_ or _gld_ pairs may be omitted.
    - _dss\_link_ name of an OpenDSS branch to compare the current and power flow.
    - _dss\_bus_ name of an OpenDSS bus at one end of the _dss\_link_ for comparing voltages, and calculating power from the current flow.
    - _gld\_link_ name of a GridLAB-D branch to compare the current and power flow.
    - _gld\_bus_ name of a GridLAB-D bus at one end of the _gld\_link_ for comparing voltages, and calculating power from the current flow.

The `onestep.py` file reads `cases.json` into a Python dictionary, then processes it. Alternatively, you may create
this dictionary programmatically in the Python script.

- The last line of the script, calling _convert\_and\_check\_models_, performs all steps in sequence.
- The first argument is the _case_ dictionary, in which attribute values control how the conversions and comparisons are done.
- The second argument _bClearDB_, will empty the Blazegraph database right away. This is most convenenient for testing, but use caution if the database may contain other circuits.
- The third argument, _bClearOutput_, will remove any _outpath\_dss_, _outpath\_glm_, _outpath\_csv_ specified in _cases_. USE CAUTION if these directories may contain other files, or manual edits. The output directories are created or re-created as necessary.
- The fourth argument, _glmScheduleDir_, specifies where to find GridLAB-D's appliance and commercial schedules, which may be needed for the -h and -a export options.

## Snapshot Results

The results from _onestep.py_ follow, comparing the single snap shot load flow solutions before
and after model conversion through CIMHub. The OpenDSS MAEv and MAEi values match closely, except
for the _ecp\_growthcvr_ case. The reason is that the pre-conversion solution is at year 10, while the
post-conversion solution is at year 0, i.e., with no load growth. This is an automated comparison, which
does not allow year 10 to be specified post-conversion. These test cases include features not
supported in GridLAB-D, so the post-conversion GridLAB-D solution doesn't match MAEv and MAEi.

```
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7354.60 -0.0052     87.13 -1.0418    326.299 + j   551.522     AB    12738.54  0.5184
    B   7354.60 -2.0996     87.13 -3.1362    326.299 + j   551.522     BC    12738.54 -1.5760
    C   7354.60  2.0892     87.13  1.0526    326.299 + j   551.522     CA    12738.54  2.6128
    Total S =   978.898 + j  1654.566
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7354.60 -0.0052     87.13 -1.0418    326.300 + j   551.523     AB    12738.54  0.5184
    B   7354.60 -2.0996     87.13 -3.1362    326.300 + j   551.523     BC    12738.54 -1.5760
    C   7354.60  2.0892     87.13  1.0526    326.300 + j   551.523     CA    12738.54  2.6128
    Total S =   978.899 + j  1654.568
  GridLAB-D branch flow in LINE_SEG1 from FDRHEAD
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7347.27 -0.0053     89.76 -1.0266    344.421 + j   562.390     AB    12725.85  0.5183
    B   7347.27  4.1835     89.76  3.1622    344.421 + j   562.390     BC    12725.84 -1.5761
    C   7347.27  2.0891     89.76  1.0678    344.421 + j   562.390     CA    12725.84  2.6127
    Total S =  1033.262 + j  1687.170
ecp_daily        Nbus=[    18,    18,    27] Nlink=[    36,    36,    15] MAEv=[ 0.0000, 0.0010] MAEi=[   0.0001,   2.2092]
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7742.12  0.0401    106.83 -3.0945   -827.055 + j     5.774     AB    13409.75  0.5637
    B   7742.12 -2.0543    106.83  1.0943   -827.055 + j     5.774     BC    13409.75 -1.5307
    C   7742.12  2.1345    106.83 -1.0001   -827.055 + j     5.774     CA    13409.75  2.6581
    Total S = -2481.165 + j    17.322
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7742.12  0.0401    106.83 -3.0945   -827.055 + j     5.774     AB    13409.75  0.5637
    B   7742.12 -2.0543    106.83  1.0943   -827.055 + j     5.774     BC    13409.75 -1.5307
    C   7742.12  2.1345    106.83 -1.0001   -827.055 + j     5.774     CA    13409.75  2.6581
    Total S = -2481.165 + j    17.322
  GridLAB-D branch flow in LINE_SEG1 from FDRHEAD
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7719.12  0.0321     86.01  3.1821   -663.918 + j     5.566     AB    13369.91  0.5557
    B   7719.12  4.2209     86.01  1.0877   -663.918 + j     5.566     BC    13369.91 -1.5387
    C   7719.12  2.1265     86.01 -1.0067   -663.918 + j     5.566     CA    13369.91  2.6501
    Total S = -1991.754 + j    16.698
ecp_duty         Nbus=[    18,    18,    24] Nlink=[    30,    30,    15] MAEv=[ 0.0000, 0.0026] MAEi=[   0.0000,   8.3789]
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7224.85 -0.0419    164.05 -0.5173   1053.771 + j   542.495     AB    12513.81  0.4817
    B   7224.85 -2.1363    164.05 -2.6117   1053.771 + j   542.495     BC    12513.81 -1.6127
    C   7224.85  2.0525    164.05  1.5771   1053.771 + j   542.495     CA    12513.81  2.5761
    Total S =  3161.313 + j  1627.485
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7302.58 -0.0314    128.81 -0.5424    820.494 + j   460.063     AB    12648.44  0.4922
    B   7302.58 -2.1258    128.81 -2.6368    820.494 + j   460.063     BC    12648.44 -1.6022
    C   7302.58  2.0630    128.81  1.5519    820.494 + j   460.063     CA    12648.44  2.5866
    Total S =  2461.482 + j  1380.190
  GridLAB-D branch flow in LINE_SEG1 from FDRHEAD
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7318.07 -0.0315    124.52 -0.5221    803.801 + j   429.317     AB    12675.28  0.4921
    B   7318.07  4.1573    124.52  3.6667    803.801 + j   429.317     BC    12675.27 -1.6023
    C   7318.07  2.0629    124.52  1.5723    803.801 + j   429.317     CA    12675.27  2.5865
    Total S =  2411.403 + j  1287.952
ecp_growthcvr    Nbus=[    18,    18,    21] Nlink=[    33,    33,    15] MAEv=[ 0.0107, 0.0129] MAEi=[  19.2234,  31.6192]
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7796.71  0.0105     71.77 -1.5432      9.570 + j   559.470     AB    13504.30  0.5341
    B   7796.71 -2.0839     71.77  2.6456      9.570 + j   559.470     BC    13504.30 -1.5603
    C   7796.71  2.1049     71.77  0.5512      9.570 + j   559.470     CA    13504.30  2.6285
    Total S =    28.711 + j  1678.410
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7796.71  0.0105     71.77 -1.5432      9.570 + j   559.472     AB    13504.30  0.5341
    B   7796.71 -2.0839     71.77  2.6456      9.570 + j   559.472     BC    13504.30 -1.5603
    C   7796.71  2.1049     71.77  0.5512      9.570 + j   559.472     CA    13504.30  2.6285
    Total S =    28.711 + j  1678.415
  GridLAB-D branch flow in LINE_SEG1 from FDRHEAD
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7743.38 -0.0048     84.83 -1.0257    343.262 + j   560.017     AB    13411.93  0.5188
    B   7743.38  4.1840     84.83  3.1631    343.262 + j   560.017     BC    13411.93 -1.5756
    C   7743.38  2.0896     84.83  1.0687    343.262 + j   560.017     CA    13411.93  2.6132
    Total S =  1029.787 + j  1680.050
ecp_harmonic     Nbus=[    18,    18,    30] Nlink=[    42,    42,    15] MAEv=[ 0.0000, 0.0061] MAEi=[   0.0001,   5.6529]
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7639.47  0.0052     15.39 -3.1343   -117.558 + j     0.246     AB    13231.95  0.5288
    B   7639.47 -2.0892     15.39  1.0545   -117.558 + j     0.246     BC    13231.95 -1.5656
    C   7639.47  2.0996     15.39 -1.0399   -117.558 + j     0.246     CA    13231.95  2.6232
    Total S =  -352.675 + j     0.739
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7639.47  0.0052     15.39 -3.1343   -117.598 + j     0.246     AB    13231.95  0.5288
    B   7639.47 -2.0892     15.39  1.0545   -117.598 + j     0.246     BC    13231.95 -1.5656
    C   7639.47  2.0996     15.39 -1.0399   -117.598 + j     0.246     CA    13231.95  2.6232
    Total S =  -352.794 + j     0.739
  GridLAB-D branch flow in LINE_SEG1 from FDRHEAD
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7640.53  0.0061     16.30  3.1493   -124.563 + j     0.200     AB    13233.79  0.5297
    B   7640.53  4.1949     16.30  1.0549   -124.563 + j     0.200     BC    13233.79 -1.5647
    C   7640.53  2.1005     16.30 -1.0395   -124.563 + j     0.200     CA    13233.79  2.6241
    Total S =  -373.690 + j     0.600
ecp_temperature  Nbus=[    18,    18,    21] Nlink=[    24,    24,    15] MAEv=[ 0.0000, 0.0001] MAEi=[   0.0033,   0.5488]
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Base case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7126.10 -0.0489    197.66 -0.5679   1222.994 + j   698.716     AB    12342.77  0.4747
    B   7126.10 -2.1433    197.66 -2.6623   1222.994 + j   698.716     BC    12342.77 -1.6197
    C   7126.10  2.0455    197.66  1.5265   1222.994 + j   698.716     CA    12342.77  2.5691
    Total S =  3668.983 + j  2096.147
  OpenDSS branch flow in LINE.SEG1 from FDRHEAD, Converted case
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7126.10 -0.0489    197.66 -0.5679   1222.994 + j   698.716     AB    12342.77  0.4747
    B   7126.10 -2.1433    197.66 -2.6623   1222.994 + j   698.716     BC    12342.77 -1.6197
    C   7126.10  2.0455    197.66  1.5265   1222.994 + j   698.716     CA    12342.77  2.5691
    Total S =  3668.983 + j  2096.147
  GridLAB-D branch flow in LINE_SEG1 from FDRHEAD
  Phs     Volts     rad      Amps     rad         kW          kVAR   PhsPhs     Volts     rad
    A   7058.86 -0.0543    223.57 -0.5776   1366.994 + j   788.604     AB    12226.30  0.4693
    B   7058.86  4.1345    223.57  3.6112   1366.993 + j   788.606     BC    12226.31 -1.6251
    C   7058.86  2.0401    223.57  1.5168   1366.994 + j   788.604     CA    12226.30  2.5637
    Total S =  4100.981 + j  2365.814
ecp_yearly       Nbus=[    18,    18,    21] Nlink=[    24,    24,    15] MAEv=[ 0.0000, 0.0093] MAEi=[   0.0000,  20.7317]

```
## Time Series Results (OpenDSS)

The results from executing _onestepa.py_ follow. The CIM XML files must already have been created
from _onestep.py_. The time series script in _onstepa.py_ is more complicated, as it customizes the steps that
were embedded in _convert\_and\_check\_models_ for snapshot power flow.

- The outputs and export options are customized in lines 155-161.
- The CIM XML upload and export steps are broken out in lines 163-167.
- Lines 169-179 set up the time-series power flow tests under `./dssa/`, by copying custom OpenDSS files defined as templates in lines 21-133.
    - Include files named _*edits.dss_ were referenced by the -m _export\_option_. They define necessary OpenDSS shapes for these cases to run.
    - Files named _*run.dss_ call and execute the exported models in _*base.dss_. In general, these custom files define and export monitors for the time-series data. They also call for solution modes other than snapshot, e.g., daily, yearly, duty, harmonic.
    - In three cases, _*run.dss_ perform manual edits before the time-series / harmonic solution, as required for a few attributes not translated through CIM. Details are explained below.
- Lines 180-181 execute six time-series / harmonic solutions on the exported models.

The built-in function to compare snapshot power flow solutions doesn't compare time-series or harmonic solutions. Therefore, six custom Python
post-processing programs are provided to compare pre-conversion and post-conversion solutions.

### ecp_daily

Executing `python ecp\_daily.py` produces the tabular and plotted output shown below, in which both solutions match.

```
Results from base
Total Energy PV1=-7828.02 PV2=-6963.21 kwh
Total Energy Gen1=-11999.88 Gen2=-9909.84 kwh
Total Energy Load1=46696.12 Load2=38556.70 kwh
Results from dssa
Total Energy PV1=-7828.02 PV2=-6963.21 kwh
Total Energy Gen1=-11999.88 Gen2=-9909.84 kwh
Total Energy Load1=46696.12 Load2=38556.70 kwh
```

![ECP Daily](../docs/media/ecp_daily.png)

### ecp_duty

Executing `python ecp\_duty.py` produces the tabular and plotted output shown below, in which both solutions match.
The _dispmode=follow_ parameter was manually specified at line 49 of _onestepa.py_ to achieve this match.
This solver-specific parameter is not included in CIM, nor presently planned as a CIMHub extension.

```
Results from base
Total Energy PV1=-805.28 PV2=-522.46 kwh
Total Energy BESS1=-402.64 BESS2=3.86 kwh
Results from dssa
Total Energy PV1=-805.28 PV2=-522.46 kwh
Total Energy BESS1=-402.64 BESS2=3.86 kwh
```

![ECP Duty](../docs/media/ecp_duty.png)

### ecp_growthcvr

Executing `python ecp\_growthcvr.py` produces the tabular and plotted output shown below, in which both solutions match.
Recall that the snapshot power flow solutions did not match, but the time series solutions match because both specify year=10.
Some _vminpu_, _cvrwatts_, and _cvrvars_ parameters were manually specified at lines 77-79 of _onestepa.py_ to achieve this match.
These solver-specific parameters are not included in CIM, nor presently planned as CIMHub extensions.

```
Results from base
Total Energy LOAD1 = 11928.77 kwh
Total Energy LOAD2 = 11127.69 kwh
Total Energy LOAD3 = 11283.36 kwh
Total Energy LOAD4 = 12859.48 kwh
Total Energy LOAD5 = 12682.07 kwh
Results from dssa
Total Energy LOAD1 = 11928.77 kwh
Total Energy LOAD2 = 11127.69 kwh
Total Energy LOAD3 = 11283.36 kwh
Total Energy LOAD4 = 12859.48 kwh
Total Energy LOAD5 = 12682.08 kwh
```

![ECP Growth CVR](../docs/media/ecp_growthcvr.png)

### ecp_harmonic

Executing `python ecp\_harmonic.py` produces the tabular and plotted output shown below, in which both solutions match.

```
Results from base
THDi PV1    =  33.43 %
THDi PV2    = 137.56 %
THDi LOAD1  =   7.29 %
THDi LOAD2  = 107.40 %
THDi GEN1   =  10.86 %
THDi GEN2   =   8.39 %
THDi BESS1  =   4.52 %
THDi BESS2  =  60.54 %
Results from dssa
THDi PV1    =  33.43 %
THDi PV2    = 137.56 %
THDi LOAD1  =   7.29 %
THDi LOAD2  = 107.40 %
THDi GEN1   =  10.86 %
THDi GEN2   =   8.39 %
THDi BESS1  =   4.52 %
THDi BESS2  =  60.54 %
```

![ECP Harmonic](../docs/media/ecp_harmonic.png)

### ecp_temperature

Executing `python ecp\_duty.py` produces the tabular and plotted output shown below, in which both solutions match.
The _effcurve_, _irradiance_, and _P-TCurve_ parameters were manually specified at lines 100-101 of _onestepa.py_ to achieve this match.
These parameters are not included in CIM, nor are they planned as CIM extensions. In many cases, _irradiance_ converts as expected,
but not when the inverter efficiency has been defined by the user, as done here.

```
Results from base
Total Energy PV1=-751.10 PV2=-779.94 kWh
Results from dssa
Total Energy PV1=-751.10 PV2=-779.94 kWh
```

![ECP Temperature](../docs/media/ecp_temperature.png)

### ecp_yearly

Executing `python ecp\_yearly.py` produces the tabular and plotted output shown below, in which both solutions match.

```
Results from base
Total Energy Load1=16859.94 Load2=7004.20 MWh
Results from dssa
Total Energy Load1=16859.94 Load2=7004.20 MWh
```

![ECP Yearly](../docs/media/ecp_yearly.png)

### gld_daily

![GLD Daily OpenDSS](../docs/media/gld_daily_dss.png)

![GLD Daily GridLAB-D](../docs/media/gld_daily_gld.png)

## Manual Adjustments to the Exported Model

In half of the six cases, manual adjustments were needed to obtain matching solutions.
This will occur any time the solution depends on parameters not included in CIM. To make
these adjustments, two options are available:

1. Add extra definitions and options to a file like _ecp\_duty\_edits.dss_, which is included just after the circuit definition, i.e., before other components have been defined.
2. Add monitors, energymeters, edits, batchedits, solution options, and solution modes to a file like _ecp\_duty\_run.dss_, just after it includes _ecp\_duty\_base.dss_. The _base_ file will have defined all the network components and calculated the voltage bases.

## Time Series Results (GridLAB-D)

To be written. Will use the InsertProfiles function for daily, duty, yearly.

