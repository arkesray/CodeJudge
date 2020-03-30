@echo off
echo.
echo.
:choice
set /P c=Start Python server(y/n)?
if /I "%c%" EQU "y" goto :start
if /I "%c%" EQU "Y" goto :start
if /I "%c%" EQU "N" goto :end
if /I "%c%" EQU "n" goto :end
goto :choice


:start
python run.py


:end
echo To start server use "python run.py".
pause
exit