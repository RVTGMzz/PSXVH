@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
 echo Gaia Master B52R26 CD DMA locator
 echo.
 echo Kéo-thả exact B52R14R1 .bin vào đây.
 pause
 exit /b 2
)
python "%~dp0gaia_b52r26_cd_dma_locator.py" "%~1"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R26 locator complete.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
