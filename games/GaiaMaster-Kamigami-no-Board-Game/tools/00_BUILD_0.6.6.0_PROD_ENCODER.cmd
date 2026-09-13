@echo off
setlocal
cd /d "%~dp0"
set "BIN=%~1"
if not "%BIN%"=="" goto run
for %%F in (*.bin) do (
  set "BIN=%%~fF"
  goto run
)
echo No BIN found in this folder.
echo Choose the CLEAN Gaia Master BIN in the file picker.
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $d=New-Object System.Windows.Forms.OpenFileDialog; $d.Filter='BIN files (*.bin)|*.bin|All files (*.*)|*.*'; if($d.ShowDialog() -eq 'OK'){[Console]::Write($d.FileName)}"`) do set "BIN=%%I"
if "%BIN%"=="" (
  echo No file selected.
  pause
  exit /b 1
)
:run
py -3 build_gaia_0660_production_encoder.py "%BIN%"
echo.
pause
