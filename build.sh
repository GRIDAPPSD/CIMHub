#!/bin/bash
#cd cimhub
#mvn clean install
#cd ..

# opendsscmd build product from fpc
#rm -rf distrib
#mkdir distrib
#cp ../OpenDSS/Source/CMD/test/opendsscmd distrib
#cp ../linenoise-ng/build/liblinenoise.so distrib
#cp ../KLUSolve/Lib/libklusolve.so distrib

python3 batch_tests.py clean

./stop.sh
docker rmi gridappsd/cimhub:1.1.0
docker build -t="gridappsd/cimhub:1.1.0" .
