@echo off
SETLOCAL

cls||clear
set /P User_Os=Is your OS windows *w* or other *o*: 

if /i %User_Os% == w call :Windows 
if /i %User_Os% == o call :others

echo %User_Os% Is not a valid Operating System
pause
exit

:Windows
cls||clear
title Installing Packages
py -3 -m pip install -r requirements.txt
cls||clear
title Installed Packages
@echo Installed All Packages
pause

:others
cls||clear
title Installing Packages
python3 -m pip install -r requirements.txt
cls||clear
title Installed Packages
@echo Installed All Packages
pause

cls
echo py account_creator.py >> run.bat
echo pause >> run.bat
start run.bat
start /b "" cmd /c del "%~f0"&exit /b
