@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Drag CLEAN Gaia Master BIN onto this CMD.
  echo Or put the BIN in this folder with the original filename.
  pause
  exit /b 1
)
py -3 build_gaia_0654_native_base.py "%~1"
echo.
pause
