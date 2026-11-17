@echo off
rem Picture Model Training Kit: get a describing workspace ready for review (kit\prepare_data.py): set aside dark,
rem blurry and repeated pictures, remove date stamps and logos, blur faces, and have two to four picture models write
rem draft descriptions, combined into one starting description per picture. Like run_video.cmd: downloads the helper
rem uv once, uses the kit's own Python 3.12 with kit\requirements.txt and kit\requirements-video.txt (installed once),
rem then runs kit\prepare_data.py with the arguments given:
rem   call kit\run_prepare.cmd "D:\Describing" all --overlays crop --engines qwen,internvl,florence
rem The Dataset Preparation program starts this file without a window and sets KIT_NO_PAUSE so it does not wait for
rem a key. The drafts need the NVIDIA graphics card; the clean-up does not.
setlocal
cd /d "%~dp0.."
set "UV_URL=https://github.com/astral-sh/uv/releases/download/0.9.5/uv-x86_64-pc-windows-msvc.zip"
set "UV_CACHE_DIR=%CD%\work\uv-cache"
set "UV_PYTHON_INSTALL_DIR=%CD%\tools\python"
set "HF_HOME=%CD%\work\hf-cache"
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
rem Only the kit's own plain sentences on the screen, not the libraries' technical warnings.
set "TRANSFORMERS_VERBOSITY=error"
set "PYTHONWARNINGS=ignore"
if not exist work mkdir work
if not exist tools mkdir tools
if not exist kit\prepare_data.py (
  echo STOPPED: this kit cannot prepare pictures yet: kit\prepare_data.py is missing. Get the newest kit.
  goto :end
)
if not exist tools\uv.exe (
  echo Getting ready: downloading the installer helper, about 20 MB.
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '%UV_URL%' -OutFile 'tools\uv.zip'; Expand-Archive -Force 'tools\uv.zip' 'tools'"
  if not exist tools\uv.exe (
    echo STOPPED: the installer helper could not be downloaded. Check the internet connection and start again.
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
rem The video and speech tools, once (installed-video-cmd.txt is this file's own mark).
if exist kit\requirements-video.txt if not exist env\installed-video-cmd.txt (
  echo Getting ready: installing the video and speech tools in this folder. This can take 5 to 15 minutes.
  tools\uv.exe pip install --python env\Scripts\python.exe -r kit\requirements-video.txt --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match --quiet
  if errorlevel 1 goto :failed
  echo installed> env\installed-video-cmd.txt
)
env\Scripts\python.exe -u kit\prepare_data.py %*
goto :end
:failed
echo STOPPED: the tools could not be installed. Check the internet connection and start again.
:end
if defined KIT_NO_PAUSE exit /b 0
echo.
echo Press any key to close this window.
pause >nul
