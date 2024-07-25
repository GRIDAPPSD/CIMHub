#!/bin/bash
source envars.sh
curl -D- -X POST $DB_URL --data-urlencode "update=drop all"
curl -D- -H "Content-Type: application/xml" --upload-file base/local_unity_a.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_optpf_a.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_optpf_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_fixq_a.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_combo_a.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_combo_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_vvar_a.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_vvar_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_avr_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_vwatt_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/remote_vvar_a.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/remote_vvar_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/remote_avr_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/remote_vwatt_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/remote_combo_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_chcurve_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/local_wvar_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/remote_1phase_b.xml -X POST $DB_URL
curl -D- -H "Content-Type: application/xml" --upload-file base/default_avr_b.xml -X POST $DB_URL

