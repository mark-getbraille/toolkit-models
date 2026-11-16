@echo off
rem Computer Check for the Picture Model Training Kit.
rem Writes "Computer Check.txt" on your desktop: the graphics cards (with the NVIDIA tool's report when there is
rem one), the processor, the memory, the free disk space and the Windows version. Nothing is changed and nothing is
rem sent anywhere; upload the text file to Claude yourself.
setlocal
for /f "usebackq delims=" %%d in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%d"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
set "OUT=%DESKTOP%\Computer Check.txt"

echo Checking this computer. This takes about half a minute.

echo COMPUTER CHECK FOR THE PICTURE MODEL TRAINING KIT> "%OUT%"
echo Made on %date% at %time%>> "%OUT%"
echo.>> "%OUT%"

echo GRAPHICS CARDS>> "%OUT%"
powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | ForEach-Object { 'Name: ' + $_.Name; 'Driver version: ' + $_.DriverVersion; 'Driver date: ' + $_.DriverDate; 'Memory reported by Windows (often wrong above 4 GB): ' + [math]::Round($_.AdapterRAM / 1GB, 1) + ' GB'; '' }" >> "%OUT%"

echo NVIDIA TOOL (nvidia-smi)>> "%OUT%"
set "NVSMI="
where nvidia-smi >nul 2>&1
if not errorlevel 1 set "NVSMI=nvidia-smi"
if not defined NVSMI if exist "%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe" set "NVSMI=%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
if not defined NVSMI if exist "%SystemRoot%\System32\nvidia-smi.exe" set "NVSMI=%SystemRoot%\System32\nvidia-smi.exe"
if defined NVSMI (
  echo Found: %NVSMI%>> "%OUT%"
  "%NVSMI%" >> "%OUT%" 2>&1
) else (
  echo Not found in the search path, in Program Files\NVIDIA Corporation\NVSMI or in System32.>> "%OUT%"
)
echo.>> "%OUT%"

echo PROCESSOR AND MEMORY>> "%OUT%"
powershell -NoProfile -Command "Get-CimInstance Win32_Processor | ForEach-Object { 'Processor: ' + $_.Name.Trim() + ', ' + $_.NumberOfCores + ' cores, ' + $_.NumberOfLogicalProcessors + ' threads' }; 'Memory: ' + [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB) + ' GB'; $cs = Get-CimInstance Win32_ComputerSystem; 'Computer: ' + $cs.Manufacturer + ' ' + $cs.Model" >> "%OUT%"
echo.>> "%OUT%"

echo DRIVES AND FREE SPACE>> "%OUT%"
powershell -NoProfile -Command "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object { $_.DeviceID + ' ' + [math]::Round($_.FreeSpace / 1GB) + ' GB free of ' + [math]::Round($_.Size / 1GB) + ' GB' }" >> "%OUT%"
echo.>> "%OUT%"

echo WINDOWS>> "%OUT%"
powershell -NoProfile -Command "$os = Get-CimInstance Win32_OperatingSystem; $os.Caption + ', version ' + $os.Version + ', ' + $os.OSArchitecture" >> "%OUT%"
echo.>> "%OUT%"

echo POWER>> "%OUT%"
powershell -NoProfile -Command "$b = Get-CimInstance Win32_Battery; if ($b) { 'Laptop with a battery: keep it plugged in while training.' } else { 'No battery: a desktop computer.' }" >> "%OUT%"
powercfg /getactivescheme >> "%OUT%" 2>&1

echo.
echo Finished. The file "Computer Check.txt" is on your desktop:
echo %OUT%
echo Upload it to Claude.
echo.
echo Press any key to close this window.
pause >nul
