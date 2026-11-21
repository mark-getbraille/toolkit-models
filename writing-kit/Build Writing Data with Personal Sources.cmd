@echo off
rem Writing Kit: build the training files from every source, including the personal-use-only ones (the Enron
rem emails and the W3C mailing lists). Use the result only on your own computer and do not share it.
rem The files go into the folder "output" here. Guide: "READ ME FIRST.txt".
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
echo Writing Kit: building the training files from every source, including the personal-use-only ones.
echo This takes about an hour the first time, because some sites are asked for one page every few seconds.
%PY% kit\build_dataset.py --out output --cache cache --personal %*
:end
echo.
if not defined KIT_NO_PAUSE pause
