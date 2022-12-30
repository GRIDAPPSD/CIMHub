CIMHub Test Cases for Transformers
==================================

Copyright (c) 2017-2022, Battelle Memorial Institute

Process
-------

The test cases in *cases.json* are configured as decribed in 
`Test Case Configuration <../README.rst#Test-Case-Configuration>`_. The
`Command-Line Reference <../README.rst#Command-Line-Reference>`_ describes available
**export\_options** for each case.

The test cases are executed with ``python3 onestep.py``. They cover:

1. Step-down, balanced and unbalanced load IEEE 4-bus test cases for YY, DD, 
   grounded YD, ungrounded YD, and DY three-phase transformers
2. Single-phase, centertapped secondary transformer with balanced or unbalanced load
3. Single-phase, wye connected transformer
4. Open Wye/Open Delta stepdown transformer
5. 3-winding substation transformer, with tank modeling and neutral reactance options
6. YD, Open Wye/Open Delta lagging, and Open Wye/Open Delta leading service to 
   induction motor and plug/lighting loads
7. 3-winding autotransformers

Items 1, 2, 4, and 6 are based on IEEE test cases. Items 4-7 are not supported in GridLAB-D.

Load Flow Comparisons
---------------------

See `Round-trip Validation <../README.rst#Round-trip-Validation>`_ for notes on 
interpreting the `Results <onestep.inc>`_. 

The OYOD and IMYD test cases do not establish a solid ground reference on the
load side of the transformer. The branch flow and line-to-line voltage
comparisons match well in OpenDSS, but the line-to-ground voltages do not, and
this is reflected in their *MAEv* values.

There are 4 test cases with YD connections that solve in GridLAB-D, but 
the primary and secondary windings must be swapped, i.e., GridLAB-D solves 
these as DY transformers.  The branch comparisons match well, because they 
are performed on a line adjacent to the tranformer under test.  However, 
the *MAEi* values are high artificially due to the swapped winding 
references.  

..
    literalinclude:: onestep.inc
   :language: none
   However, GitHub README will not support include files

AutoTransformers
----------------

The three-winding autotransformer test cases were derived from a 
whitepaper on CIM transformer modeling, which included an actual test 
report from a 345/161/13.8 kV, 330/330/72 MVA, YNad1 autotransformer.  The 
test data is archived in the OpenDSS repository, with scripts that verify 
losses, short-circuit currents and voltage regulation for the modeling 
options available in OpenDSS.  GridLAB-D does not support 3-winding 
transformers, nor autotransformers, so GridLAB-D validation is skipped.  
The CIM support for autotransformers is incomplete, so only two of the 
four variants work properly for round-trip validation in OpenDSS.  

- **AutoHLT.dss** represents the autotransformer as a non-auto Yyd1. 
  It replicates test data, except for the split of load losses between 
  HT and LT tests. It also fails to show the MVA size reduction inherent 
  in the autotransformer.
- **Auto1bus.dss** represents the autotransformer as a bank of three 
  single-phase, reduced-MVA tanks, connected YNad1. This is accurate, 
  but does not translate through CIM because it uses a "9-phase bus" to 
  represent the common node, which causes errors in connections and 
  voltage ratings. This is "option 1" from the OpenDSS Tech Note on 
  modeling autotransformers.
- **Auto3bus.dss** represents the autotransformer as a bank of three 
  single-phase, reduced-MVA tanks, connected YNad1. This is accurate, 
  but does not translate through CIM because it uses a "6-phase bus" with 
  jumper to represent the common node, which causes errors in connections 
  and voltage ratings. This is "option 2" from the OpenDSS Tech Note on 
  modeling autotransformers.
- **AutoAuto.dss** uses the built-in "autotrans" component in OpenDSS. 
  It uses test results directly as input, making the series-common 
  winding connection internally. CIM can support this by recognizing the 
  vector group YNa or YNad1.  OpenDSS uses the PowerTransformer.vectorGroup 
  to determine whether it's an autotransformer.  The choices of 
  WindingConnectionKind include Y, Yn, and A for windings 1 and 2.  A 
  applies to winding 2 and Y can work for winding 1.  A new enumeration 
  should be considered for winding 1, i.e., S for series.  



