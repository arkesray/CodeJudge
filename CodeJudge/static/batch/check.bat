@echo off
cd %2

fc "output.txt" "%1\data\problems\%3\outputs\output.txt" > "cm.txt"
if %errorlevel% == 0 (
	echo #CorrectAnswer#
) else (
	echo #WrongAnswer#
)

exit