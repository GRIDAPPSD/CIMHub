#!/bin/bash
cd cimhub
mvn clean install
cd ..

# opendsscmd build product from fpc
rm -rf distrib
mkdir distrib
cp ../OpenDSS/Source/CMD/test/opendsscmd distrib
cp ../linenoise-ng/build/liblinenoise.so distrib
cp ../KLUSolve/Lib/libklusolve.so distrib

./stop.sh
docker rmi gridappsd/cimhub:0.0.2
docker rmi gridappsd/cimhub:0.0.3
docker rmi gridappsd/cimhub:0.0.4
docker build -t="gridappsd/cimhub:0.0.4" .
