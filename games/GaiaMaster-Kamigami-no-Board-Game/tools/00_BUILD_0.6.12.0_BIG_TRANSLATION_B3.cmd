@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
  echo Drag CLEAN Gaia Master Japan BIN onto this CMD.
  pause
  exit /b 1
)

py -3 build_gaia_06120_big_translation_b3.py "%~1"
echo.
pause
