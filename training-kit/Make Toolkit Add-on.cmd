@echo off
rem Make Toolkit Add-on: puts the toolkit version of your trained describer into each result zip that lacks it
rem (kit\make_toolkit_addon.py), for a zip made by an older kit. The kit does this by itself at its next start, so
rem this file is only needed when you do not want to start a training. The zip then has a folder "toolkit" with the
rem add-on in llama.cpp's format, which the Digital Accessibility Toolkit installs with "Install a trained
rem describer..." in its Describe pictures settings.
rem It needs the training's add-on, which stays in the kit's work folder (work\adapter-<training>\final): do not delete
rem the work folder first. It uses the kit's own Python (made by the first training); no NVIDIA card is needed. It
rem downloads llama.cpp's converter once (about 40 MB, from GitHub); nothing is sent anywhere.
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
set "HF_HOME=%CD%\work\hf-cache"
rem Only the kit's own plain sentences on the screen, not the libraries' technical warnings.
set "TRANSFORMERS_VERBOSITY=error"
set "PYTHONWARNINGS=ignore"
if not exist kit\make_toolkit_addon.py (
  echo STOPPED: kit\make_toolkit_addon.py is missing. Get the newest kit.
  goto :end
)
if not exist env\Scripts\python.exe (
  echo STOPPED: the training tools are not installed in this folder. Run this file in the kit folder where your
  echo training ran, the one with the "result" and "work" folders.
  goto :end
)
env\Scripts\python.exe -u kit\make_toolkit_addon.py %*
:end
echo.
echo Press any key to close this window.
pause >nul
