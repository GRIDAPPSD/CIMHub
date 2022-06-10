The Open Distribution System Simulator, OpenDSS

Copyright (c) 2008-2022, Electric Power Research Institute, Inc.
Copyright (c) 2017-2022, Battelle Memorial Institute
All rights reserved.

opendsscmd version 1.7.1
========================

This is a 64-bit command-line version of the simulator for Windows, Linux and Mac OSX operating systems. It is model-compatible with version 9 of the Windows-only version. The major differences between opendsscmd and Windows-only OpenDSS are:

1 - There is no support for Windows COM automation, and no separate DLL version. (Use FNCS or HELICS instead)

2 - There is no graphical user interface (GUI) or plotting. (Use MATLAB or Python instead)

3 - Automation is provided through the Framework for Network Cosimulation (FNCS) library developed by Pacific Northwest National Laboratory (PNNL), and the HELICS framework developed by several US Department of Energy labs under the Grid Modernization Laboratory Consortium (GMLC) project 1.4.15.

4 - It is built with Free Pascal instead of Delphi.

Installation
============

On Linux and Mac OSX, the files will be installed as follows (no user choice at this time):

  Executables:     /usr/local/bin
  Libraries:       /usr/local/lib
  Docs:            /usr/local/share/opendsscmd/doc
  Tech Notes:      /usr/local/share/opendsscmd/doc/notes
  Test Files:      /usr/local/share/opendsscmd/test
  EPRI Test Cases: /usr/local/share/opendsscmd/examples/epri
  IEEE Test Cases: /usr/local/share/opendsscmd/examples/ieee

On Windows, the files will be installed as follows, and c:\opendsscmd is appended to the system path 
(the user can change c:\opendsscmd):

  Executables:     c:\opendsscmd
  Libraries:       c:\opendsscmd
  Docs:            c:\opendsscmd\doc
  Tech Notes:      c:\opendsscmd\doc\notes
  Test Files:      c:\opendsscmd\test
  EPRI Test Cases: c:\opendsscmd\examples\epri
  IEEE Test Cases: c:\opendsscmd\examples\ieee

On all platforms, an uninstaller is provided one level above the Docs directory.

FNCS and HELICS
===============

On all platforms, FNCS and HELICS will be installed or updated (no user choice at this time).

On Windows, the communication libraries ZeroMQ and CZMQ are also installed to support FNCS
and HELICS. These local copies won't interfere with other software on the computer.

On Linux or Mac OS X, you may have to install ZeroMQ and CZMQ yourself, following examples
provided below. Without those libraries, you may see "FNCS not available" and/or
"HELICS not available" from the opendsscmd prompt, but in all other respects the program is 
fully functional.

To install the support libraries on Ubuntu 20.04 LTS:

  sudo apt-get update
  sudo apt-get -y install libzmq5-dev
  sudo apt-get -y install libczmq-dev

To install the support libraries on Centos 8:

  sudo dnf update -y
  sudo dnf install zeromq-devel -y
  sudo dnf install czmq-devel -y

To install the support libraries on Mac OS X:

  xcode-select --install
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
  brew install zmq
  brew install czmq

Quick Start
===========

If you're unfamiliar with OpenDSS, the Doc files OpenDSSPrimer.pdf and OpenDSSManual.pdf to learn about its modeling and analysis features.  However, none of the COM automation or plotting features are supported in opendsscmd. To run any of the non-graphical commands:

1. Enter "opendsscmd" from a command prompt
    a. The program's >> prompt will appear. Enter any OpenDSS command(s) from this prompt
    b. Up and down arrows navigate through the command history
    c. Enter "help" from the >> prompt for the built-in help
    d. Enter "exit", "q" or an empty line from >> to exit
2. You can enter "opendsscmd filename.dss" from a command prompt. This runs the OpenDSS commands in filename.dss, and then exits immediately.
3. You can enter "opendsscmd –f" from a command prompt; this enters a FNCS time step loop.
4. You can enter "opendsscmd –f filename.dss" from a command prompt. This runs the OpenDSS commands in filename.dss, and then enters a FNCS time step loop.
5. Enter "opendsscmd -h" from a command prompt to show the command line options, which include three logging levels for FNCS messages

To verify proper installation:

1. Navigate to the test directory
   a. On Windows, "cd c:\opendsscmd\test"
   b. On Linux or Mac OS X:
      i.   "mkdir work"
      ii.  "cp -r /usr/local/share/opendsscmd/* work"
      iii. "cd work/test"
1. From the test directory, invoke "opendsscmd", and then "redirect IEEE13Nodeckt.dss". A list of solved node voltages should appear in your system's default test editor. Enter "quit" to leave opendsscmd
2. From the test directory, invoke "opendsscmd export_test.dss". This should create a Common Information Model (CIM) export of the IEEE 13-bus feeder.
3. If you have FNCS installed, from install_dir/test invoke "test_fncs.bat" (on Windows) or "./test_fncs.sh" (on Linux or Mac OSX). This will play some basic commands to opendsscmd over FNCS on port 5570, and then exit. If something goes wrong here:
   a. To list processes using port 5570, use "list5570.bat" on Windows or "lsof -i tcp:5570" on Linux/Mac
   b. To kill all processes using port 5570, use "kill5570.bat" on Windows or "kill5570.sh" on Linux/Mac

Change Log
==========

1.0.1 - CIM export of Relay, Fuse, Breaker based on controls attached to Lines having switch=yes

1.1.0 - CIM100 support, time-stepping under control of FNCS

1.2.0 - FNCS output publications
      - operational limits included in CIM100 export
      - ExpControl and VCCS enhancements from IEEE PVSC 46 papers

1.2.1 - removed FNCS debug output
      - added test.json sample FNCS messaging config file

1.2.2 - changed CIM100 mRID from GUID to UUID v4; see RFC 4122

1.2.3 - added "-v" flag and "about" command for version number

1.2.4 - fixed FNCS time synchronization for power rationing example
      - implemented FNCS log levels (opendsscmd --help for details)

1.2.5 - include Buses in "export UUIDS" and "UUID" commands

1.2.6 - persist all CIM mRID values in the "uuid" and "export uuid" commands

1.2.7 - bugfix for persistent mRID values on CIM-created XfmrCodes

1.2.8 - performance tuning in the FNCS interface

1.2.9 - added the option to export CIM100 in six separate sub-profiles

1.2.10 - trap UUID for a missing bus

1.2.11 - fix TransformerCoreAdmittance, TransformerEnd and some indentation
       - fix undervoltage relay property values

1.2.12 - more performance tuning in FNCS interface
       - supporting both JSON and Text formatted FNCS publication
       - example of linking a GridLAB-D house and weather to OpenDSS
       - works with FNCS feature/opendss and GridLAB-D feature/1173 branches

1.2.13 - publish battery stored energy over FNCS

1.2.14 - fixed FNCS publication of complex values with very small imaginary parts

1.2.15 - retain the user-input line length units for subsequent CIM export
       - installs FNCS and HELICS

1.2.16 - CIM export uses load.class=2 to prevent s1, s2 phases on 3-phase LV loads

1.2.17 - links with HELICS, includes three HELICS examples
       - Distance (21) and incremental distance (TD21) types added to Relay
       - fix voltage base for 3-phase VCCS in RMS mode
       - VCCS will cease to inject current when a terminal opens, e.g., by a Relay
       - VCCS injects positive sequence current only when in RMS mode
       - Distance (21) and TD21 relays have a reverse-looking flag
       - Include the Microsoft Visual C++ 2019 redistributable installer

1.3.0  - Version archived for GridAPPS-D co-simulation

1.4.0  - Using the minP and maxP attributes of PowerElectronicsConnection for CIM export

1.5.0  - builds from the Version 8 source tree, with support for most Version 8 features
       - fixes to autotransformer losses and 3-winding short-circuit currents
       - new CIM export of autotransformers, capacitor states, reactors
       - fixed CIM export of secondary switches, center-tapped delta transformers
       - fixed the line geometry "make like" to reset the number of phases
       - increased precision of length conversion to 1609.344 m/mile
       - fixed the change directory command on Linux
       - properly initialize list of CIM operational limits in a circuit with no Lines
       - fixes to CIM phase transpositions on lines and transformers
       - first implementation of the IEC 61970-302 CIM Dynamics profile for DER

1.6.0  - exporting InvControl and ExpControl to the CIM Dynamics profile
       - correction to CIM export of transformer magnetizing and exciting current

1.7.0  - updated to version 9.4.1 model features from the Windows-only version
       - updates for GMDM interoperability tests: orderedPhases, TapChanger, minQ, maxQ attributes
       - updates for round-trip testing of CIM Dynamics and transformer connections
       - improvements to ExpControl performance and static solutions

1.7.1  - export CIM leakage impedance as Z (was X)
       - distribute CIM load losses among short-circuit tests (was all on the first one)
       - rename BatteryState to BatteryStateKind for CIM export

Open Issues
===========

1. The regular expressions for the batchedit command, which are implemented in ExecHelper.pas, have become case-sensitive.  They need to be made case-insensitive.
2. On Windows, the command history editor is "sluggish". You have to type slowly.

Source Code
===========

OpenDSS source code is available from the following SVN repository: 

http://svn.code.sf.net/p/electricdss/code/trunk/

The opendsscmd version requires Lazarus/Free Pascal to build. Some of the supporting modules may require a C++ compiler to build from source. See the Doc file OpenDSS_FPC_Build.pdf for directions.

Third-party Components
======================

KLUSolve.DLL is open source software, available from www.sourceforge.net/projects/klusolve

The command history editor is forked from open source software, available from https://github.com/pnnl/linenoise-ng.git 

License
=======

Use of this software is subject to a license. The terms are in:

1 - A file called "license.txt" distributed with the software, and
2 - The user manual

