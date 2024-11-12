FOR /f "tokens=*" %%i IN ('docker ps -q') DO docker stop %%i
