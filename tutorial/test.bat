rem call envars.bat
rem java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=both -a=1 -h=1 -l=1.0 -p=1.0 -e=carson both/ieee123ecp
rem python ../src_python/cimhub/DropProfiles.py cimhubjar.json CBE09B55-091B-4BB0-95DA-392237B12640
python ../src_python/cimhub/InsertProfiles.py cimhubjar.json oedi_profiles.dat

