call envars.bat
java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=dss  -l=1.0 -i=1.0 -e=carson dss/testing

rem rd /s /q bentley\dss
rem md bentley\dss
rem rd /s /q bentley\glm
rem md bentley\glm
rem java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=dss  -l=1.0 -i=1.0 -e=carson bentley/dss/testing
rem java -cp %CIMHUB_PATH% %CIMHUB_PROG% -u=%DB_URL% -o=glm  -l=1.0 -i=1.0 -e=carson bentley/glm/testing
