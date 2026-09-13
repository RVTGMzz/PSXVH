@echo off
setlocal
cd /d "%~dp0"
set "BIN=%~1"
if not "%BIN%"=="" goto run
if exist "GaiaMaster - Kamigami no Board Game (Japan).bin" (
  set "BIN=%CD%\GaiaMaster - Kamigami no Board Game (Japan).bin"
  goto run
)
for %%F in (*.bin) do (
  set "BIN=%%~fF"
  goto run
)
echo No BIN found in this folder.
echo Choose the CLEAN Gaia Master BIN.
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $d=New-Object System.Windows.Forms.OpenFileDialog; $d.Filter='BIN files (*.bin)|*.bin|All files (*.*)|*.*'; if($d.ShowDialog() -eq 'OK'){[Console]::Write($d.FileName)}"`) do set "BIN=%%I"
if "%BIN%"=="" (
  echo No file selected.
  pause
  exit /b 1
)
:run
py -3 build_gaia_0662_native_narrow_8px.py "%BIN%"
echo.
pause
