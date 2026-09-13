@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Drag CLEAN Gaia Master BIN onto this CMD.
  pause
  exit /b 2
)
py -3 "%~dp0build_gaia_06130_translation_b4.py" "%~1"
echo.
pause
