@echo off
py -m pip install -r requirements.txt
cls
echo py account_creator.py >> run.bat
echo pause >> run.bat
start run.bat
start /b "" cmd /c del "%~f0"&exit /b
