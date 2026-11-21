@echo off
rem Writing Kit: build the training files from the open and share-alike sources only (OpenAssistant OASST2 and
rem Dolly). The files go into the folder "out" here. Guide: "READ ME FIRST.txt".
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
echo Writing Kit: building the training files from the open and share-alike sources.
%PY% kit\build_dataset.py --out out --cache cache %*
:end
echo.
if not defined KIT_NO_PAUSE pause
