@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Gaia Master 0.6.38.0 - Full Japanese Text Scan

echo ============================================================
echo   GAIA MASTER 0.6.38.0 - FULL JAPANESE TEXT SCAN
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
  py -3 "%~dp0scan_full_japanese_text_06380.py" "%BIN%"
) else (
  python "%~dp0scan_full_japanese_text_06380.py" "%BIN%"
)
echo.
echo Sau khi quet xong, gui lai 2 file:
echo GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv
echo GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
echo.
pause
