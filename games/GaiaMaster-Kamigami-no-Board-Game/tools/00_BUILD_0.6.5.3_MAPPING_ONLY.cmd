@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Keo file CLEAN GaiaMaster .bin vao file CMD nay.
  echo Hoac dat CLEAN BIN cung thu muc voi ten:
  echo GaiaMaster - Kamigami no Board Game ^(Japan^).bin
  echo.
  py -3 build_gaia_0653_mapping_only.py
) else (
  py -3 build_gaia_0653_mapping_only.py "%~1"
)
echo.
pause
