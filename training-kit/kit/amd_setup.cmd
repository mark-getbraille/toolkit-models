@echo off
rem Picture Model Training Kit: the AMD graphics way (new, being tested). Called by run.cmd and run_pictures.cmd ONLY
rem when no NVIDIA driver was found; computers with an NVIDIA card never come here and work exactly as before.
rem   1. looks for an AMD graphics adapter in Windows' list (PCI vendor number 1002); when there is none, it says the
rem      kit's usual message (the kit needs an NVIDIA card) and stops;
rem   2. downloads the helper uv once (the same file and checksum as run.cmd) and makes the kit's own Python 3.12;
rem   3. runs kit\gpu_backend.py --check, which says in plain words whether AMD's PyTorch for Windows (ROCm 7.2.1)
rem      supports this AMD card, and stops when it does not (an unknown card can be tried with KIT_AMD_TRY=1);
rem   4. installs kit\requirements-amd.txt once (AMD's own PyTorch from repo.radeon.com, each file checked against
rem      its SHA-256; instead of kit\requirements.txt, which stays the NVIDIA list), and with the argument "pictures"
rem      also kit\requirements-pictures.txt. It writes env\installed-amd.txt, and env\installed.txt so the other
rem      start files do not put NVIDIA's PyTorch back.
rem Ends with errorlevel 0 when the training can start, 1 when it said STOPPED. Uses the caller's UV_URL, UV_SHA256,
rem UV_CACHE_DIR and UV_PYTHON_INSTALL_DIR, and runs in the kit folder.
powershell -NoProfile -Command "if (Get-CimInstance Win32_VideoController | Where-Object { $_.PNPDeviceID -match 'VEN_1002' }) { exit 0 } else { exit 1 }"
if errorlevel 1 (
  echo STOPPED: no NVIDIA graphics card driver was found. The kit needs an NVIDIA card with at least 12 GB of memory
  echo and its driver from nvidia.com. If this computer has an AMD or Intel graphics card instead, tell Claude its name.
  exit /b 1
)
echo No NVIDIA driver was found, but there is AMD graphics. Checking whether the kit can train on it: this is new
echo and being tested.
if not exist tools\uv.exe (
  echo Getting ready: downloading the installer helper, about 20 MB.
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '%UV_URL%' -OutFile 'tools\uv.zip'; if ((Get-FileHash -Algorithm SHA256 'tools\uv.zip').Hash -eq '%UV_SHA256%') { Expand-Archive -Force 'tools\uv.zip' 'tools' } else { Remove-Item -Force 'tools\uv.zip'; Write-Host 'The downloaded helper did not match its published checksum, so it was deleted.' }"
  if not exist tools\uv.exe (
    echo STOPPED: the installer helper could not be downloaded. Check the internet connection and start the kit again.
    exit /b 1
  )
)
if not exist env\Scripts\python.exe (
  tools\uv.exe venv env --python 3.12 --quiet
  if errorlevel 1 goto :failed
)
env\Scripts\python.exe kit\gpu_backend.py --check
if errorlevel 1 exit /b 1
if not exist env\installed-amd.txt (
  echo Getting ready: installing the training tools for AMD graphics in this folder, about 4 GB. This takes 10 to 30
  echo minutes.
  tools\uv.exe pip install --python env\Scripts\python.exe -r kit\requirements-amd.txt --quiet
  if errorlevel 1 goto :failed
  echo installed> env\installed-amd.txt
  echo installed> env\installed.txt
)
if /i not "%~1"=="pictures" exit /b 0
if exist kit\requirements-pictures.txt if not exist env\installed-pictures-amd-cmd.txt (
  echo Getting ready: installing the picture-making tools in this folder. This can take 10 to 30 minutes.
  tools\uv.exe pip install --python env\Scripts\python.exe -r kit\requirements-amd.txt -r kit\requirements-pictures.txt --quiet
  if errorlevel 1 goto :failed
  echo installed> env\installed-pictures-amd-cmd.txt
  echo installed> env\installed-pictures-cmd.txt
)
exit /b 0
:failed
echo STOPPED: the training tools for AMD graphics could not be installed. Check the internet connection and start
echo the kit again. If it says the same again, tell Claude.
exit /b 1
