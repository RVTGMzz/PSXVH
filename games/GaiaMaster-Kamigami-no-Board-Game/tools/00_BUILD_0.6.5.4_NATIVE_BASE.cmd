@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "BIN=%~1"

if not defined BIN if exist "GaiaMaster - Kamigami no Board Game (Japan).bin" set "BIN=%CD%\GaiaMaster - Kamigami no Board Game (Japan).bin"

if not defined BIN (
  for %%F in (*.bin) do (
    if not defined BIN set "BIN=%%~fF"
  )
)

if not defined BIN (
  for /f "usebackq delims=" %%F in (`powershell -NoProfile -STA -Command "Add-Type -AssemblyName System.Windows.Forms; $d=New-Object System.Windows.Forms.OpenFileDialog; $d.Filter='Gaia Master BIN (*.bin)|*.bin|All files (*.*)|*.*'; $d.Title='Chon CLEAN Gaia Master BIN'; if($d.ShowDialog() -eq 'OK'){ $d.FileName }"`) do set "BIN=%%F"
)

if not defined BIN (
  echo [CANCEL] No BIN selected.
  pause
  exit /b 1
)

echo Using BIN:
echo %BIN%
echo.
py -3 build_gaia_0654_native_base.py "%BIN%"
echo.
pause
