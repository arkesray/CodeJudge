@echo off
cd %2

set size=0
break > rte.txt

java %5<"%1\data\problems\%3\inputs\input.txt">"output.txt" 2>"rte.txt"
call :filesize "rte.txt"
if not %size%==0 (
	echo #RunTimeError#
	goto :eof
) else (
	echo #NoErrors#
	goto :eof
)

exit

:filesize
	set size=%~z1
	goto :eof