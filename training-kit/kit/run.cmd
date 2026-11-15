@echo off
rem Picture Model Training Kit: shared start-up for "Start Training.cmd" and "Start Training 8B.cmd".
rem Downloads the helper uv (MIT/Apache-2.0, astral.sh) once, makes the kit's own Python 3.12 with the pinned
rem packages in kit\requirements.txt (in this folder only), then runs kit\train.py with the arguments given.
setlocal
cd /d "%~dp0.."
set "UV_URL=https://github.com/astral-sh/uv/releases/download/0.9.5/uv-x86_64-pc-windows-msvc.zip"
set "UV_CACHE_DIR=%CD%\work\uv-cache"
set "UV_PYTHON_INSTALL_DIR=%CD%\tools\python"
set "HF_HOME=%CD%\work\hf-cache"
set "PYTHONUTF8=1"
rem Only the kit's own plain sentences on the screen, not the libraries' technical warnings.
set "TRANSFORMERS_VERBOSITY=error"
set "PYTHONWARNINGS=ignore"
if not exist work mkdir work
if not exist tools mkdir tools
where nvidia-smi >nul 2>&1
if errorlevel 1 (
  echo STOPPED: no NVIDIA graphics card driver was found. The kit needs an NVIDIA card with at least 12 GB of memory.
  goto :end
)
if not exist tools\uv.exe (
  echo Getting ready: downloading the installer helper, about 20 MB.
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '%UV_URL%' -OutFile 'tools\uv.zip'; Expand-Archive -Force 'tools\uv.zip' 'tools'"
  if not exist tools\uv.exe (
    echo STOPPED: the installer helper could not be downloaded. Check the internet connection and start the kit again.
    goto :end
  )
)
if not exist env\installed.txt (
  echo Getting ready: installing the training tools in this folder, about 5 GB. This takes 10 to 30 minutes.
  tools\uv.exe venv env --python 3.12 --quiet
  if errorlevel 1 goto :failed
  tools\uv.exe pip install --python env\Scripts\python.exe -r kit\requirements.txt --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match --quiet
  if errorlevel 1 goto :failed
  echo installed> env\installed.txt
)
env\Scripts\python.exe kit\train.py %*
goto :end
:failed
echo STOPPED: the training tools could not be installed. Check the internet connection and start the kit again.
:end
echo.
echo Press any key to close this window.
pause >nul
