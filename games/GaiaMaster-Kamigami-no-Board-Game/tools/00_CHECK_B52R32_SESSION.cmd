@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
 echo Gaia Master B52R32 session status
 echo.
 echo Kéo-thả exact B52R14R1 .bin vào đây.
 echo Chỉ kiểm trạng thái, không chạy probe và không build ROM.
 pause
 exit /b 2
)
python "%~dp0gaia_b52r32_capture_session_manager.py" "%~1"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R32 status report written next to BIN.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
