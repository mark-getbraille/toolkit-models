@echo off
rem Writing Kit: install the OCR reader (RapidOCR, ONNX Runtime and pypdfium2) that reads scanned email releases.
rem It is installed once, from the Python package index; afterwards it runs on this computer with nothing online.
rem Guide: "READ ME FIRST.txt", section "Scanned email releases (OCR)".
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
echo Writing Kit: installing the OCR reader. This downloads about 100 MB once and takes a few minutes.
%PY% -m pip install -r kit\requirements-ocr.txt
if errorlevel 1 (
  echo STOPPED: the OCR reader could not be installed. Read the lines above for the reason.
  goto :end
)
echo Done: the OCR reader is installed.
:end
echo.
if not defined KIT_NO_PAUSE pause
