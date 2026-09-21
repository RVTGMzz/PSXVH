@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
  echo Gaia Master B52R28 CD-DMA provenance analyzer
  echo.
  echo Cách 1: kéo TRACE.tsv vào đây để phân tích overlap RAM.
  echo Cách 2: chạy với TRACE.tsv và exact B52R14R1 .bin để map LBA sang ISO file.
  pause
  exit /b 2
)
if "%~2"=="" (
  python "%~dp0gaia_b52r26_cd_dma_provenance_analyzer.py" "%~1"
) else (
  python "%~dp0gaia_b52r26_cd_dma_provenance_analyzer.py" "%~1" "%~2"
)
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R28 provenance analysis complete.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
