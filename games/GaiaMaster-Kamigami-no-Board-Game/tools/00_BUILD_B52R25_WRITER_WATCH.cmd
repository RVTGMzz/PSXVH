@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
  echo Gaia Master B52R25 source-writer watch builder
  echo.
  echo Kéo-thả GaiaMaster_B52R24_TRACE.tsv vào file CMD này.
  echo Chỉ hỗ trợ linear DMA SyncMode 0/1. SyncMode 2 phải dùng GPU-origin/transaction khác.
  pause
  exit /b 2
)
python "%~dp0gaia_b52r25_writer_watch_generator.py" "%~1"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] Đã tạo GaiaMaster_B52R25_PCSX_SOURCE_WRITER_WATCH.lua
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
