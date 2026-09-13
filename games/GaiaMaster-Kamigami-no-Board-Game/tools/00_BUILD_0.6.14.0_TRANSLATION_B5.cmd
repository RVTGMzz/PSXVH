@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Drag CLEAN Gaia Master Japan BIN onto this CMD.
  pause
  exit /b 2
)
py -3 "%~dp0build_gaia_06140_translation_b5.py" "%~1"
pause
