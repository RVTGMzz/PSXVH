@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Gaia Master 0.6.40.0 - Batch30 Accent Sweep

echo ============================================================
echo   GAIA MASTER 0.6.40.0 - BATCH30 ACCENT SWEEP BUILD
echo ============================================================
echo.
set "BIN=%~1"
if not defined BIN (
  for %%F in ("%~dp0*.bin") do if not defined BIN set "BIN=%%~fF"
)
if not defined BIN (
  echo [!] Khong tim thay CLEAN Japan BIN.
  echo Keo file BIN tha vao CMD nay, hoac dat BIN cung thu muc tools.
  echo.
  pause
  exit /b 2
)
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 "%~dp0build_gaia_06400_batch30_accent_sweep.py" "%BIN%"
) else (
  python "%~dp0build_gaia_06400_batch30_accent_sweep.py" "%BIN%"
)
echo.
pause
