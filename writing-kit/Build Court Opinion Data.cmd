@echo off
rem Writing Kit: download and build the US court opinions corpus (CourtListener bulk data, public domain).
rem The five bulk files are 63 GB; it can be stopped (close the window) and resumed (start this again).
rem The files go into the folder "court_opinions", the examples into "out\court_opinions".
rem You can also give options after the file name, for example: "Build Court Opinion Data.cmd" --list
rem Guide: "READ ME FIRST.txt", section "Court opinions".
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
  %PY% kit\build_court_opinions.py %*
  goto :end
)
echo Writing Kit: US court opinions from CourtListener. The download is 63 GB; building takes about a day.
set "COURTS="
set /p "COURTS=Type the courts you want, for example scotus,ca9,cal, or just press Enter for every court: "
set "YEARS="
set /p "YEARS=Type the years you want, for example 1950-1999,2010s, or just press Enter for every year: "
set "ARGS="
if defined COURTS set ARGS=--courts "%COURTS%"
if defined YEARS set ARGS=%ARGS% --years "%YEARS%"
%PY% kit\build_court_opinions.py %ARGS%
:end
echo.
if not defined KIT_NO_PAUSE pause
