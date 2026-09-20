@echo off
setlocal
chcp 65001 >nul
if "%~2"=="" (
  echo Gaia Master B52R25 writer-PC resolver
  echo.
  echo Chọn/kéo-thả CẢ HAI file:
  echo   GaiaMaster_B52R25_WRITER_TRACE.tsv
  echo   B52R14R1 .bin
  echo vào CMD này cùng lúc, hoặc chạy CMD với 2 đường dẫn.
  pause
  exit /b 2
)
python "%~dp0gaia_b52r25_writer_pc_resolver.py" "%~1" "%~2"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] Đã tạo GaiaMaster_B52R25_WRITER_RESOLVE.txt
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
