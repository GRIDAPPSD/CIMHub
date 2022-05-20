call envars.bat
curl -D- -X POST %DB_URL% --data-urlencode "update=drop all"
curl -D- -H "Content-Type: application/xml" --upload-file base/ieee9500unbal.xml -X POST %DB_URL%
java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=dss  -p=1.0 -l=1.0 -e=carson -t=1 dss/ieee9500unbal
java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=csv  -p=1.0 -l=1.0 -e=carson -t=1 csv/ieee9500unbal
java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=glm  -p=1.0 -l=1.0 -e=carson -t=1 glm/ieee9500unbal
