@echo off
setlocal
chcp 65001 >nul
if "%~2"=="" (
 echo Gaia Master B52R27 disc payload fingerprint
 echo.
 echo Chạy với 2 file:
 echo   GaiaMaster_B52R24_DMA_SOURCE.bin
 echo   exact B52R14R1 .bin
 pause
 exit /b 2
)
python "%~dp0gaia_b52r27_disc_payload_fingerprint.py" "%~1" "%~2"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R27 fingerprint complete.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
