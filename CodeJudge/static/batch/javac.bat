@echo off
cd %2

set size=0
break > co.txt

javac %4 2> co.txt
call :filesize "co.txt" 
if not %size%==0 (
	echo #CompilationError#
	goto :eof
) else (
	echo #CompilationSuccess#
	goto :eof
)

exit

:filesize
	set size=%~z1
	goto :eof