#!/bin/bash
opendsscmd ../example/cim_test.dss
cp ../example/ieee13*CAT.XML .
cp ../example/ieee13*EP.XML .
cp ../example/ieee13*FUN.XML .
cp ../example/ieee13*GEO.XML .
cp ../example/ieee13*SSH.XML .
cp ../example/ieee13*TOPO.XML .
python3 test_combiner.py


