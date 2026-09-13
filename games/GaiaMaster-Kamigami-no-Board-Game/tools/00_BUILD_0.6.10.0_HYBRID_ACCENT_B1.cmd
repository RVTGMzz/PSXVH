@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
  echo Drag CLEAN Gaia Master BIN onto this CMD.
  pause
  exit /b 1
)

py -3 build_gaia_06100_hybrid_accent_b1.py "%~1"
echo.
pause
