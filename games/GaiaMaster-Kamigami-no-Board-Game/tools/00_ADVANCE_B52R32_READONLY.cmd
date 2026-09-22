@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
 echo Gaia Master B52R32 safe read-only advance
 echo.
 echo Kéo-thả exact B52R14R1 .bin vào đây.
 echo Tool chỉ tự chạy các bước static/read-only an toàn.
 echo Nó sẽ DỪNG ở thao tác PCSX runtime hoặc B52R31 build gate.
 pause
 exit /b 2
)
python "%~dp0gaia_b52r32_capture_session_manager.py" "%~1" --advance-readonly
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R32 advanced all currently-safe read-only steps.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
