@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Gaia Master 0.6.55.1 - Batch45R2 Font Micro Polish

echo ============================================================
echo   GAIA MASTER 0.6.55.1 - BATCH45R2 FONT MICRO POLISH
echo ============================================================
echo.
set "BIN=%~1"
if not defined BIN (
  for %%F in ("%~dp0*.bin") do if not defined BIN set "BIN=%%~fF"
)
if not defined BIN (
  echo [!] Khong tim thay CLEAN Japan BIN.
  echo Keo CLEAN BIN tha vao file CMD nay, hoac dat BIN cung thu muc tools.
  echo.
  pause
  exit /b 2
)

where py >nul 2>&1
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  set "PY=python"
)

echo [1/2] Static selftest...
%PY% "%~dp0build_gaia_06551_batch45r2_font_micro_polish.py" --selftest
if errorlevel 1 (
  echo.
  echo [ERROR] STATIC SELFTEST FAILED. Khong build game.
  echo Gui lai man hinh/log loi cho Ta.
  echo.
  pause
  exit /b 9
)

echo.
echo [2/2] Build tu CLEAN BIN + font geometry gates...
%PY% "%~dp0build_gaia_06551_batch45r2_font_micro_polish.py" "%BIN%"
if errorlevel 1 (
  echo.
  echo [ERROR] BUILD FAILED. Dung tai loi dau tien, khong goi Runtime PASS.
  echo Gui BUILD_LOG/man hinh loi cho Ta.
  echo.
  pause
  exit /b 9
)

echo.
echo ============================================================
echo   BUILD DONE - VAN CAN GAMEPLAY SCREENSHOT

echo   Gui lai:
echo   GaiaMaster_0.6.55.1_BATCH45R2_FINAL_REPORT.txt
echo   + screenshot co chu đ / Đ / â-ê-ô / dau kep neu co
echo ============================================================
echo.
pause
