@echo off
rem Writing Kit: read a folder of scanned PDF email releases you downloaded yourself, with OCR, and build training
rem files from them. Personal use only, except US federal government works. The files go into the folder "out".
rem You can also give the folder after the file name, for example: "Build Writing Data from Scanned Folder.cmd" "B:\Original sources"
rem Guide: "READ ME FIRST.txt", section "Your own folder of scanned PDFs".
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
set "FOLDER=%~1"
if not defined FOLDER set /p "FOLDER=Type the folder of scanned PDFs, for example B:\Original sources, then press Enter: "
if not defined FOLDER (
  echo STOPPED: no folder was typed.
  goto :end
)
if not exist "%FOLDER%\" (
  echo STOPPED: the folder %FOLDER% was not found.
  goto :end
)
echo Writing Kit: reading the scanned PDFs in %FOLDER% with OCR. This takes two to five seconds a page.
%PY% kit\build_dataset.py --out out --scanned-folder "%FOLDER%"
:end
echo.
if not defined KIT_NO_PAUSE pause
