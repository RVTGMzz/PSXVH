@echo off
setlocal
chcp 65001 >nul

if "%~1"=="" (
  echo Gaia Master B52R22 live-source probe
  echo.
  echo Keo-tha file B52R14R1 .bin vao file CMD nay, hoac chay:
  echo   %~nx0 "D:\duong-dan\GaiaMaster_B52R14R1.bin"
  echo.
  echo Tool chi doc BIN va tao TXT/CSV nhe. Khong tao BIN moi.
  pause
  exit /b 2
)

python "%~dp0gaia_b52r22_live_source_probe.py" "%~1"
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" echo [FAIL] B52R22 probe exit code %ERR%
if "%ERR%"=="0" echo [OK] B52R22 probe complete. Gui lai file GaiaMaster_B52R22_LIVE_SOURCE_PROBE_REPORT.txt de tiep tuc.
pause
exit /b %ERR%
