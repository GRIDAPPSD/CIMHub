opendsscmd ..\example\cim_test.dss
copy ..\example\ieee13*CAT.XML .
copy ..\example\ieee13*EP.XML .
copy ..\example\ieee13*FUN.XML .
copy ..\example\ieee13*GEO.XML .
copy ..\example\ieee13*SSH.XML .
copy ..\example\ieee13*TOPO.XML .
python test_combiner.py


