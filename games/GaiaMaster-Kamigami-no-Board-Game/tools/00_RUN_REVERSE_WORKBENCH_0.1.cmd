@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Gaia Master - Reverse Workbench 0.1

echo ============================================================
echo   GAIA MASTER - REVERSE WORKBENCH 0.1 (READ ONLY)
echo ============================================================
echo.
echo Tool nay KHONG patch BIN va KHONG thay doi production build.
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
  set "PY=py -3"
) else (
  set "PY=python"
)

echo [1/2] Quet graphic/TIM asset census...
%PY% "%~dp0gaia_graphic_asset_census_0.1.py" "%BIN%"
if errorlevel 1 (
  echo.
  echo [ERROR] Graphic asset census that bai. Dung tai day de giu log dau tien.
  echo Gui lai man hinh/log loi cho Ta.
  echo.
  pause
  exit /b 1
)

echo.
echo [2/2] Dinh vi chapter card runtime: 冒険のはじまり
%PY% "%~dp0gaia_runtime_target_locator_0.1.py" "%BIN%"
if errorlevel 1 (
  echo.
  echo [ERROR] Runtime target locator that bai.
  echo Gui lai man hinh/log loi cho Ta.
  echo.
  pause
  exit /b 1
)

echo.
echo ============================================================
echo   DONE - KHONG CO BYTE NAO TRONG BIN BI SUA

echo   Gui lai cac file sau:
echo   GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_REPORT.txt
echo   GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_OWNERS.csv
echo   GaiaMaster_GRAPHIC_ASSET_CENSUS_0.1_TIM.csv
echo   GaiaMaster_RUNTIME_TARGET_LOCATOR_0.1_REPORT.txt
echo ============================================================
echo.
pause
