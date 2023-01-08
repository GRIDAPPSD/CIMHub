#!/bin/bash
# (now using archived JAR for consistency with non-Docker CIMHub)
#cd cimhub
#mvn clean install
#./deploy.sh
#cd ..

# local opendsscmd build product from fpc 
# (now using the archived version for consistency with non-Docker CIMHub)
#rm -rf distrib
#mkdir distrib
#cp ../OpenDSS/Source/CMD/test/opendsscmd distrib
#cp ../linenoise-ng/build/liblinenoise.so distrib
#cp ../KLUSolve/Lib/libklusolve.so distrib

rm blazegraph/*.jnl
rm blazegraph/*.log
python3 batch_tests.py clean

# use the local build of GridLAB-D, because it's not part of non-Docker CIMHub
rm -rf gridlabd
mkdir gridlabd
mkdir gridlabd/bin
mkdir gridlabd/lib
mkdir gridlabd/lib/static
mkdir gridlabd/share
export GLD_INSTALL=/opt/tesp
cp $GLD_INSTALL/bin/gridlabd gridlabd/bin/gridlabd
cp $GLD_INSTALL/bin/gridlabd.sh gridlabd/bin/gridlabd.sh
cp $GLD_INSTALL/lib/assert.so gridlabd/lib/assert.so
cp $GLD_INSTALL/lib/climate.so gridlabd/lib/climate.so
cp $GLD_INSTALL/lib/commercial.so gridlabd/lib/commercial.so
cp $GLD_INSTALL/lib/connection.so gridlabd/lib/connection.so
cp $GLD_INSTALL/lib/generators.so gridlabd/lib/generators.so
cp $GLD_INSTALL/lib/glsolvers.so gridlabd/lib/glsolvers.so
cp $GLD_INSTALL/lib/glxengine.so gridlabd/lib/glxengine.so
cp $GLD_INSTALL/lib/market.so gridlabd/lib/market.so
cp $GLD_INSTALL/lib/mysql.so gridlabd/lib/mysql.so
cp $GLD_INSTALL/lib/optimize.so gridlabd/lib/optimize.so
cp $GLD_INSTALL/lib/powerflow.so gridlabd/lib/powerflow.so
cp $GLD_INSTALL/lib/reliability.so gridlabd/lib/reliability.so
cp $GLD_INSTALL/lib/residential.so gridlabd/lib/residential.so
cp $GLD_INSTALL/lib/tape.so gridlabd/lib/tape.so
cp $GLD_INSTALL/lib/tape_file.so gridlabd/lib/tape_file.so
cp $GLD_INSTALL/lib/tape_plot.so gridlabd/lib/tape_plot.so
cp $GLD_INSTALL/lib/static/libjsoncpp.a gridlabd/lib/static/libjsoncpp.a
cp $GLD_INSTALL/lib/static/superlu_lib.a gridlabd/lib/static/superlu_lib.a
cp $GLD_INSTALL/share/tzinfo.txt gridlabd/share/tzinfo.txt
cp $GLD_INSTALL/share/unitfile.txt gridlabd/share/unitfile.txt

./stop.sh
docker rmi gridappsd/cimhub:1.1.0
docker build -t="gridappsd/cimhub:1.1.0" .
