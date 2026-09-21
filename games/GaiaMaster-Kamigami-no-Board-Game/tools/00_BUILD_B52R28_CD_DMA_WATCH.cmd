@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
  echo Gaia Master B52R28 CD-DMA provenance watch builder
  echo.
  echo Kéo-thả GaiaMaster_B52R24_TRACE.tsv vào đây.
  echo B52R24 target phải là linear DMA SyncMode 0/1.
  pause
  exit /b 2
)
python "%~dp0gaia_b52r26_cd_dma_provenance_generator.py" "%~1"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] Đã tạo GaiaMaster_B52R28_PCSX_CD_DMA_PROVENANCE.lua
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
