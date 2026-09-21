@echo off
setlocal
chcp 65001 >nul
if "%~3"=="" (
  echo Gaia Master B52R29 overlay fingerprint resolver
  echo.
  echo Cần 3 file:
  echo   1. GaiaMaster_B52R25_WRITER_TRACE.tsv
  echo   2. GaiaMaster_B52R25_WRITER_RAM.bin
  echo   3. exact B52R14R1 .bin
  echo.
  echo Chạy: %~nx0 "TRACE.tsv" "WRITER_RAM.bin" "B52R14R1.bin"
  pause
  exit /b 2
)
python "%~dp0gaia_b52r27_overlay_fingerprint_resolver.py" "%~1" "%~2" "%~3"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R29 overlay fingerprint analysis complete.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
