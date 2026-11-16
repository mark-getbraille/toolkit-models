@echo off
rem Picture Model Training Kit: put back what "Prepare This Computer.cmd" changed, after the training.
rem It asks Windows for administrator permission, then: restores your saved power plan (or the usual sleep
rem settings), turns hibernation back on, ends the Windows Update pause and the restart rule, and lets Windows
rem Defender scan the kit folder again. Long file names stay allowed (they do no harm).
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "KIT=%~dp0"
if "%KIT:~-1%"=="\" set "KIT=%KIT:~0,-1%"

net session >nul 2>&1
if errorlevel 1 (
  echo Asking Windows for administrator permission. Answer Yes in the User Account Control window.
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
  exit /b
)

echo.
echo Putting back the normal settings.
echo.

echo 1. The power plan.
set "RESTORED="
if exist "%KIT%\power-plan-before-training.pow" (
  for /f "tokens=2 delims=:" %%g in ('powercfg /import "%KIT%\power-plan-before-training.pow" 2^>nul ^| findstr /i "GUID"') do set "NEWPLAN=%%g"
  if defined NEWPLAN (
    set "NEWPLAN=!NEWPLAN: =!"
    powercfg /setactive !NEWPLAN! >nul 2>&1
    if not errorlevel 1 set "RESTORED=yes"
  )
)
if defined RESTORED (
  echo    Your saved power plan is active again.
) else (
  echo    No saved plan could be used; the usual settings are set instead: sleep after 30 minutes, lid close sleeps.
  powercfg /change standby-timeout-ac 30
  powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 1 >nul 2>&1
  powercfg /setactive SCHEME_CURRENT
)

echo 2. Turning hibernation back on.
powercfg /hibernate on

echo 3. Ending the Windows Update pause and the restart rule.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$k='HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'; foreach ($n in 'PauseUpdatesStartTime','PauseFeatureUpdatesStartTime','PauseQualityUpdatesStartTime','PauseUpdatesExpiryTime','PauseFeatureUpdatesEndTime','PauseQualityUpdatesEndTime') { Remove-ItemProperty -Path $k -Name $n -ErrorAction SilentlyContinue }; Remove-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU' -Name NoAutoRebootWithLoggedOnUsers -ErrorAction SilentlyContinue; Write-Host '   Windows Update works normally again.'"

echo 4. Letting Windows Defender scan the kit folder again.
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Remove-MpPreference -ExclusionPath '%KIT%' -ErrorAction Stop; Write-Host '   Done.' } catch { Write-Host '   Nothing to change.' }"

echo.
echo Finished. Your normal settings are back.
echo Press any key to close this window.
pause >nul
