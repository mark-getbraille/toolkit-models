@echo off
rem Picture Model Training Kit: shared start-up for training a picture-making model (words to pictures).
rem Like run.cmd: downloads the helper uv once and makes the kit's own Python 3.12 with kit\requirements.txt; then
rem also installs kit\requirements-pictures.txt (the picture-making tools, when that file is there) once, and runs
rem kit\train_pictures.py with the arguments given, for example:
rem   call kit\run_pictures.cmd --base sdxl --size normal --with-nudity --own "D:\My pictures"
rem Every line it says also goes into training-log.txt in the kit folder, as with the picture describer.
setlocal
cd /d "%~dp0.."
set "UV_URL=https://github.com/astral-sh/uv/releases/download/0.9.5/uv-x86_64-pc-windows-msvc.zip"
rem The helper's SHA-256 published with uv 0.9.5 (uv-x86_64-pc-windows-msvc.zip.sha256): a download that does
rem not match it (damaged, or changed on the way) is deleted, never unpacked or run.
set "UV_SHA256=515dc53d7553f1357d0abc1f70acd921fbb9e30230b1d9a08737236daa6ee920"
set "UV_CACHE_DIR=%CD%\work\uv-cache"
set "UV_PYTHON_INSTALL_DIR=%CD%\tools\python"
set "HF_HOME=%CD%\work\hf-cache"
set "PYTHONUTF8=1"
rem Only the kit's own plain sentences on the screen, not the libraries' technical warnings.
set "TRANSFORMERS_VERBOSITY=error"
set "PYTHONWARNINGS=ignore"
if not exist work mkdir work
if not exist tools mkdir tools
if not exist kit\train_pictures.py (
  echo STOPPED: this kit cannot train a picture-making model yet: kit\train_pictures.py is missing. Get the newest kit.
  goto :end
)
rem The NVIDIA driver's tool: in the search path (newer drivers), or in its own folder (older drivers).
set "NVSMI="
where nvidia-smi >nul 2>&1
if not errorlevel 1 set "NVSMI=nvidia-smi"
if not defined NVSMI if exist "%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe" set "NVSMI=%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
if not defined NVSMI if exist "%SystemRoot%\System32\nvidia-smi.exe" set "NVSMI=%SystemRoot%\System32\nvidia-smi.exe"
if not defined NVSMI (
  echo STOPPED: no NVIDIA graphics card driver was found. The kit needs an NVIDIA card with at least 12 GB of memory
  echo and its driver from nvidia.com. If this computer has an AMD or Intel graphics card instead, tell Claude its name.
  goto :end
)
if not exist tools\uv.exe (
  echo Getting ready: downloading the installer helper, about 20 MB.
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '%UV_URL%' -OutFile 'tools\uv.zip'; if ((Get-FileHash -Algorithm SHA256 'tools\uv.zip').Hash -eq '%UV_SHA256%') { Expand-Archive -Force 'tools\uv.zip' 'tools' } else { Remove-Item -Force 'tools\uv.zip'; Write-Host 'The downloaded helper did not match its published checksum, so it was deleted.' }"
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
rem The picture-making tools, once (installed-pictures-cmd.txt is this file's own mark; the program keeps its own).
if exist kit\requirements-pictures.txt if not exist env\installed-pictures-cmd.txt (
  echo Getting ready: installing the picture-making tools in this folder. This can take 10 to 30 minutes.
  tools\uv.exe pip install --python env\Scripts\python.exe -r kit\requirements.txt -r kit\requirements-pictures.txt --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match --quiet
  if errorlevel 1 goto :failed
  echo installed> env\installed-pictures-cmd.txt
)
env\Scripts\python.exe kit\train_pictures.py %*
goto :end
:failed
echo STOPPED: the training tools could not be installed. Check the internet connection and start the kit again.
:end
echo.
echo Press any key to close this window.
pause >nul
