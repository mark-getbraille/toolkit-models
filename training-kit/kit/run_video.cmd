@echo off
rem Picture Model Training Kit: take still pictures out of videos (kit\video_frames.py), for describing.
rem Like run.cmd: downloads the helper uv once and makes the kit's own Python 3.12 with kit\requirements.txt (the
rem same environment the training uses, in this folder only); then also installs kit\requirements-video.txt (the
rem video and speech tools, when that file is there) once, and runs kit\video_frames.py with the arguments given:
rem   call kit\run_video.cmd "D:\Videos\Shop.mp4" --out "D:\Describing" --every 2 --blur-faces --overlays crop
rem (--overlays crop or fill removes burned-in date stamps and station logos; the Describe pictures window adds it
rem when "Date stamps and logos" is not "Leave them".)
rem The program's "Describe pictures" window starts this file without a window, writes every line it says into
rem the "Picture Model Training logs" folder on the desktop, and sets KIT_NO_PAUSE so it does not wait for a key.
rem No NVIDIA card is needed: the speech is turned into text on the graphics card when there is one, otherwise on
rem the processor (slower).
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
if not exist kit\video_frames.py (
  echo STOPPED: this kit cannot take stills from videos yet: kit\video_frames.py is missing. Get the newest kit.
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
env\Scripts\python.exe -u kit\video_frames.py %*
goto :end
:failed
echo STOPPED: the tools could not be installed. Check the internet connection and start again.
:end
if defined KIT_NO_PAUSE exit /b 0
echo.
echo Press any key to close this window.
pause >nul
