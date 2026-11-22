@echo off
rem Writing Kit: download and build the US patent text corpus, year by year (abstracts, claims, descriptions).
rem HUPD (applications 2004 to 2018, CC BY-SA 4.0) is 62 GB; the USPTO's granted patents need your own key.
rem It can be stopped (close the window) and resumed (start this again).
rem The files go into the folder "patents", the examples into "out\patents".
rem You can also give options after the file name, for example: "Build Patent Data.cmd" --list
rem Guide: "READ ME FIRST.txt", section "Patents".
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
  %PY% kit\build_patents.py %*
  goto :end
)
echo Writing Kit: US patents. Type 1 for HUPD (applications 2004 to 2018, 62 GB, no key needed),
echo or 2 for the USPTO's granted patents (1976 to now; needs your USPTO_ODP_API_KEY setting).
set "WHICH="
set /p "WHICH=Type 1 or 2, or just press Enter for 1: "
set "SOURCE=hupd"
if "%WHICH%"=="2" set "SOURCE=uspto"
set "YEARS="
set /p "YEARS=Type the years you want, for example 2010-2014 or 1980s, or just press Enter for every year: "
set "MAXGB="
set /p "MAXGB=Type the most gigabytes to download, for example 20, or just press Enter for no limit: "
set ARGS=--source %SOURCE%
if defined YEARS set ARGS=%ARGS% --years "%YEARS%"
if defined MAXGB set ARGS=%ARGS% --max-gb %MAXGB%
%PY% kit\build_patents.py %ARGS%
:end
echo.
if not defined KIT_NO_PAUSE pause
