@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Gaia Master 0.6.55.1 - Safe Package Launcher

echo ============================================================
echo   GAIA MASTER 0.6.55.1 - SAFE PACKAGE LAUNCHER
echo ============================================================
echo.

set "ROOT=%~dp0..\.."
for %%I in ("%ROOT%") do set "ROOT=%%~fI"
set "BUILDER=%~dp0build_gaia_06551_batch45r2_font_micro_polish.py"
set "FINDER=%~dp0find_clean_bin_06551.py"
set "PATHFILE=%TEMP%\gaia_clean_06551_%RANDOM%_%RANDOM%.txt"

if not exist "%BUILDER%" (
  echo [ERROR] Missing builder:
  echo %BUILDER%
  exit /b 5
)
if not exist "%FINDER%" (
  echo [ERROR] Missing CLEAN BIN finder:
  echo %FINDER%
  exit /b 5
)

where py >nul 2>&1
if not errorlevel 1 (
  set "PYEXE=py"
  set "PYOPT=-3"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python was not found in PATH.
    echo Install Python 3 or enable the Python launcher, then run again.
    exit /b 4
  )
  set "PYEXE=python"
  set "PYOPT="
)

echo [OK] Python command: %PYEXE% %PYOPT%

set "BIN=%~1"
if defined BIN (
  if not exist "%BIN%" (
    echo [ERROR] Supplied BIN does not exist:
    echo %BIN%
    exit /b 2
  )
  for %%I in ("%BIN%") do set "BIN=%%~fI"
) else (
  if exist "%PATHFILE%" del /q "%PATHFILE%" >nul 2>&1
  echo [1/3] Finding exact CLEAN Japan BIN by SHA1...
  "%PYEXE%" %PYOPT% "%FINDER%" "%ROOT%" "%PATHFILE%"
  if errorlevel 1 exit /b 3
  if not exist "%PATHFILE%" (
    echo [ERROR] CLEAN BIN finder returned no path file.
    exit /b 3
  )
  set /p "BIN="<"%PATHFILE%"
  del /q "%PATHFILE%" >nul 2>&1
)

if not defined BIN (
  echo [ERROR] CLEAN BIN path is empty.
  exit /b 3
)

echo [OK] CLEAN BIN:
echo %BIN%
echo.

echo [2/3] Running static selftest...
"%PYEXE%" %PYOPT% "%BUILDER%" --selftest
if errorlevel 1 (
  echo [ERROR] Static selftest failed.
  exit /b 9
)

echo.
echo [3/3] Building from CLEAN BIN...
"%PYEXE%" %PYOPT% "%BUILDER%" "%BIN%"
if errorlevel 1 (
  echo [ERROR] CLEAN build failed.
  exit /b 9
)

echo.
echo ============================================================
echo   BUILD 0.6.55.1 COMPLETED
echo ============================================================
echo Open the generated 0.6.55.1 CUE for runtime testing.
echo Send GaiaMaster_0.6.55.1_BATCH45R2_FINAL_REPORT.txt back.
echo Runtime screenshot is still required before Runtime PASS.
exit /b 0
