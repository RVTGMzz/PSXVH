@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
  echo Gaia Master B52R24 PCSX capture builder
  echo.
  echo Kéo-thả GaiaMaster_B52R23_GPU_MMIO_HITS.csv vào file CMD này.
  echo Tool chỉ tạo Lua trace script, không tạo ROM.
  pause
  exit /b 2
)
python "%~dp0gaia_b52r24_trace_generator.py" "%~1"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] Đã tạo GaiaMaster_B52R24_PCSX_DMA_SOURCE_CAPTURE.lua
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
