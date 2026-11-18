@echo off
rem Build a review pack: the pictures the training packs set aside because their description was missing or poor
rem (the release "needs-description"), with the text of each picture's web page (kept on this computer only) and two
rem drafts per picture written from the picture alone. The same as Dataset Preparation's "Build a review pack" window,
rem in a plain text window. It carries on where it stopped when started again with the same folder.
rem Guide: "HOW TO DESCRIBE PICTURES THAT NEED A DESCRIPTION.txt".
setlocal
echo Build a Review Pack: pictures from the training packs that need a description.
echo Reading the list of collections. The first time, the kit's tools are installed first, which takes a while.
set "KIT_NO_PAUSE=1"
call "%~dp0kit\run_prepare.cmd" --list-needs
set "KIT_NO_PAUSE="
echo.
set "KEYS="
set /p "KEYS=Type the collections to put in the pack, separated by commas, or all, then press Enter: "
if "%KEYS%"=="" set "KEYS=all"
set "FOLDER="
set /p "FOLDER=Type the folder for the review pack, or press Enter for the folder Review pack in the kit: "
if "%FOLDER%"=="" set "FOLDER=%~dp0Review pack"
echo Building the review pack in %FOLDER%. Close this window to stop; start it again to carry on.
call "%~dp0kit\run_prepare.cmd" "%FOLDER%" review-pack --keys "%KEYS%"
