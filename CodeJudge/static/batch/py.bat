@echo off
cd %2

set size=0
break echo interpreter> co.txt
break > rte.txt

python %4<"%1\data\problems\%3\inputs\input.txt">"output.txt" 2>"rte.txt"
call :filesize "rte.txt"
if not %size%==0 (
	echo #RunTimeError#
	goto :eof
)

fc "output.txt" "%1\data\problems\%3\outputs\output.txt" > "cm.txt"
if %errorlevel% == 0 (
	echo #CorrectAnswer#
) else (
	echo #WrongAnswer#
)

exit

:filesize
	set size=%~z1
	goto :eof