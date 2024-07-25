#!/bin/bash
declare -r DB_URL="http://localhost:8889/bigdata/namespace/kb/sparql"
declare -r CIMHUB_PATH="target/libs/*:../cimhub/target/cimhub-1.0.0-SNAPSHOT.jar"
declare -r CIMHUB_PROG="gov.pnnl.gridappsd.cimhub.CIMImporter"

#declare -r CIMHUB_FID="_3CC2D836-CE11-4D4F-B93D-B2851B1E79B5" #local_avr_b
#declare -r CIMHUB_FID="_6A7D5722-8D9D-4C54-861D-56E1CDA52231" #local_chcurve_b
#declare -r CIMHUB_FID="_1D4B98E2-62AB-411A-813E-F125F29ABD48" #local_combo_a
#declare -r CIMHUB_FID="_7C1EEB79-9E9C-43E5-BAE9-0F0F99B41384" #local_combo_b
#declare -r CIMHUB_FID="_A0BABA6C-3323-412C-A87A-E8F15456031C" #local_fixq_a
#declare -r CIMHUB_FID="_3D9154FE-8514-40BA-8AE1-7DB8B134617D" #local_optpf_a
#declare -r CIMHUB_FID="_43728B05-D922-4477-99DA-F980D27811ED" #local_optpf_b
#declare -r CIMHUB_FID="_B3600BC3-18B5-4720-9CC6-5997E35E8158" #local_unity_a
#declare -r CIMHUB_FID="_D1D5E183-EE39-44E6-9D5C-A1519F0D8709" #local_vvar_a
#declare -r CIMHUB_FID="_3D840B6D-4A97-4BDA-A488-4EEF2F4F5FBD" #local_vvar_b
#declare -r CIMHUB_FID="_0A81F3A8-0985-423B-A5F5-2A7A0319A9B6" #local_vwatt_b
#declare -r CIMHUB_FID="_746C6392-9F8B-4537-98C4-E978AB9547D4" #local_wvar_b
#declare -r CIMHUB_FID="_520E4BC8-D3C2-4745-B784-AE23361E94BB" #remote_1phase_b
#declare -r CIMHUB_FID="_408201DC-BBAB-4CDE-85DF-7F8D1E2CF258" #remote_avr_b
#declare -r CIMHUB_FID="_58EAA940-6023-4F38-B09B-3D445BAB4429" #remote_combo_b
#declare -r CIMHUB_FID="_DA89ACD5-8AB1-46E4-959E-5BDE188DC12F" #remote_vvar_a
#declare -r CIMHUB_FID="_5824790B-58F9-4428-BB11-6D56CE013C73" #remote_vvar_b
#declare -r CIMHUB_FID="_4C7345DE-E5D1-4A00-ACC4-0F85B9016F03" #remote_vwatt_b
#declare -r CIMHUB_FID="_57AA3D7E-E023-4C09-A9A7-81C44C2EE87E" #default_avr_b

declare -r CIMHUB_FID="_49AD8E07-3BF9-A4E2-CB8F-C3722F837B62" # ieee13
#declare -r CIMHUB_FID="_5B816B93-7A5F-B64C-8460-47C17D6E4B0F" # ieee13assets
#declare -r CIMHUB_FID="_AAE94E4A-2465-6F5E-37B1-3E72183A4E44" # ieee9500

#java -cp $CIMHUB_PATH $CIMHUB_PROG -u=$DB_URL -o=idx test

java -cp $CIMHUB_PATH $CIMHUB_PROG \
  -s=$CIMHUB_FID -u=$DB_URL -o=glm -l=1.0 -i=1 -h=0 -x=0 -t=1 test
#gridlabd test_run.glm
#cat test_base.glm

#java -cp $CIMHUB_PATH $CIMHUB_PROG \
#  -s=$CIMHUB_FID -u=$DB_URL -o=dss -l=1.0 -i=1 -h=0 -x=0 -t=1 test
#cat *base.dss
#opendsscmd test.dss

#java -cp $CIMHUB_PATH $CIMHUB_PROG \
#  -s=$CIMHUB_FID -u=$DB_URL -o=csv -l=1.0 -i=1 -h=0 -x=0 -t=1 test
#cat test_Solar.csv
#cat test_Storage.csv
