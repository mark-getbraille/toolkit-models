@echo off
rem Writing Kit: download and build the historical US newspaper corpus (American Stories, 1770 to 1964, CC BY 4.0).
rem The whole download is 340 GB; it can be stopped (close the window) and resumed (start this again).
rem The year files go into the folder "newspapers", the examples into "out\newspapers".
rem You can also give options after the file name, for example: "Build Newspaper Data.cmd" --list
rem Guide: "READ ME FIRST.txt", section "Historical newspapers".
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo STOPPED: Python is not installed. Install Python 3 from python.org, tick "Add Python to PATH", and start again.
  goto :end
)
if not "%~1"=="" (
  %PY% kit\build_newspapers.py %*
  goto :end
)
echo Writing Kit: historical US newspapers, 1770 to 1964. All the years together are 340 GB.
set "YEARS="
set /p "YEARS=Type the years you want, for example 1850-1869,1900s, or just press Enter for every year: "
set "MAXGB="
set /p "MAXGB=Type the most gigabytes to download, for example 50, or just press Enter for no limit: "
set "ARGS="
if defined YEARS set ARGS=--years "%YEARS%"
if defined MAXGB set ARGS=%ARGS% --max-gb %MAXGB%
%PY% kit\build_newspapers.py %ARGS%
:end
echo.
if not defined KIT_NO_PAUSE pause
