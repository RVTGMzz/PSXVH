@echo off
setlocal
chcp 65001 >nul

if "%~1"=="" (
  echo Gaia Master B52R23 GPU upload locator
  echo.
  echo Kéo-thả file B52R14R1 .bin vào file CMD này, hoặc chạy:
  echo   %~nx0 "D:\duong-dan\GaiaMaster_B52R14R1.bin"
  echo.
  echo Tool chỉ đọc BIN và tạo TXT/CSV. Không tạo BIN/CUE/ISO mới.
  pause
  exit /b 2
)

python "%~dp0gaia_b52r23_gpu_upload_locator.py" "%~1"
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" echo [FAIL] B52R23 locator exit code %ERR%
if "%ERR%"=="0" echo [OK] B52R23 locator complete. Xem GaiaMaster_B52R23_GPU_UPLOAD_LOCATOR_REPORT.txt và GPU_BREAKPOINTS.txt.
pause
exit /b %ERR%
