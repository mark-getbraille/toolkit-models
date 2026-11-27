@echo off
rem Picture Model Training Kit: prepare this computer for a long training run.
rem Run it once, before "Quick Try.cmd". It asks Windows for administrator permission, then:
rem   1. saves your current power plan (to put it back later with "Restore Normal Settings.cmd");
rem   2. on mains power: never sleep, never hibernate, never turn off the disks, and do nothing when a laptop lid
rem      is closed (the screen may still turn off);
rem   3. turns hibernation off (this also frees the disk space of the hibernation file);
rem   4. pauses Windows Update for 7 days and stops it restarting the computer while you are signed in;
rem   5. allows long file names (some training files have long paths);
rem   6. tells Windows Defender not to scan the kit folder (it holds hundreds of thousands of small pictures and
rem      5 GB of tools; scanning each one slows the kit down a lot);
rem   7. checks the NVIDIA card and the free disk space.
rem Everything it changes is listed in "settings-before-training.txt" in this folder.
setlocal
cd /d "%~dp0"
set "KIT=%~dp0"
if "%KIT:~-1%"=="\" set "KIT=%KIT:~0,-1%"

net session >nul 2>&1
if errorlevel 1 (
  echo Asking Windows for administrator permission. Answer Yes in the User Account Control window.
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

set "NOTE=%KIT%\settings-before-training.txt"
echo Prepare This Computer, %date% %time%> "%NOTE%"
echo.
echo Preparing this computer for the picture model training.
echo.

echo 1. Saving your current power plan.
powercfg /export "%KIT%\power-plan-before-training.pow" SCHEME_CURRENT >nul 2>&1
if errorlevel 1 (
  echo    The power plan could not be saved; it is changed anyway.
  echo Power plan: not saved>> "%NOTE%"
) else (
  echo    Saved as power-plan-before-training.pow.
  echo Power plan saved: power-plan-before-training.pow>> "%NOTE%"
)

echo 2. On mains power: never sleep, never hibernate, disks always on, nothing happens when the lid is closed.
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change disk-timeout-ac 0
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0 >nul 2>&1
powercfg /setactive SCHEME_CURRENT
echo Sleep, hibernate and disk timeouts on mains power: never. Lid close on mains power: do nothing.>> "%NOTE%"

echo 3. Turning hibernation off.
powercfg /hibernate off
echo Hibernation: turned off.>> "%NOTE%"

echo 4. Pausing Windows Update for 7 days, with no restarts while you are signed in.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$f='yyyy-MM-ddTHH:mm:ssZ'; $now=(Get-Date).ToUniversalTime(); $end=$now.AddDays(7); $k='HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'; New-Item -Path $k -Force | Out-Null; foreach ($n in 'PauseUpdatesStartTime','PauseFeatureUpdatesStartTime','PauseQualityUpdatesStartTime') { Set-ItemProperty -Path $k -Name $n -Value $now.ToString($f) }; foreach ($n in 'PauseUpdatesExpiryTime','PauseFeatureUpdatesEndTime','PauseQualityUpdatesEndTime') { Set-ItemProperty -Path $k -Name $n -Value $end.ToString($f) }; $p='HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'; New-Item -Path $p -Force | Out-Null; Set-ItemProperty -Path $p -Name NoAutoRebootWithLoggedOnUsers -Value 1 -Type DWord; Write-Host ('   Paused until ' + $end.ToLocalTime().ToString('dddd d MMMM, HH:mm') + '.')"
echo Windows Update: paused for 7 days; no automatic restart while signed in.>> "%NOTE%"

echo 5. Allowing long file names.
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f >nul
echo Long file names: allowed.>> "%NOTE%"

echo 6. Asking Windows Defender not to scan the kit folder.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Add-MpPreference -ExclusionPath '%KIT%' -ErrorAction Stop; Write-Host '   Done.' } catch { Write-Host '   Not possible here (another antivirus program, or Defender is managed). The kit still works, a little slower.' }"
echo Windows Defender: the kit folder %KIT% is not scanned.>> "%NOTE%"

echo 7. Checking the graphics card and the disk.
set "NVSMI="
where nvidia-smi >nul 2>&1
if not errorlevel 1 set "NVSMI=nvidia-smi"
if not defined NVSMI if exist "%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe" set "NVSMI=%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
if not defined NVSMI (
  echo    No NVIDIA driver was found. The graphics cards in this computer are:
  powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | ForEach-Object { Write-Host ('      ' + $_.Name) }"
  echo    The kit needs an NVIDIA card. Tell Claude the names above.
  echo    AMD Radeon graphics are a second choice, new and being tested: Quick Try.cmd checks whether yours
  echo    can be used. See "Training on an AMD graphics card" in READ ME FIRST.txt.
) else (
  for /f "tokens=1,2 delims=," %%a in ('call "%NVSMI%" --query-gpu^=name^,memory.total --format^=csv^,noheader') do echo    Graphics card: %%a, memory%%b
)
powershell -NoProfile -Command "$d=(Get-Item '%KIT%').PSDrive; $gb=[math]::Floor($d.Free/1GB); if ($gb -ge 90) { Write-Host ('   Free disk space on drive ' + $d.Name + ': ' + $gb + ' GB. Enough.') } else { Write-Host ('   Free disk space on drive ' + $d.Name + ': only ' + $gb + ' GB. The training needs about 90 GB: move the kit folder to a bigger drive.') }"

echo.
echo Finished. This computer is ready. Now press Enter on "Quick Try.cmd".
echo When the training is over, run "Restore Normal Settings.cmd" to put everything back.
echo.
rem Started by the wizard with /nopause: no key to press.
if /i "%~1"=="/nopause" exit /b 0
echo Press any key to close this window.
pause >nul
