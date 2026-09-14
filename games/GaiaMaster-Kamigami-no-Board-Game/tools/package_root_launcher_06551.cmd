@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Gaia Master 0.6.55.1 - Safe Root Launcher

echo ============================================================
echo   GAIA MASTER 0.6.55.1 - LAUNCHER STARTED
echo ============================================================
echo.

set "INNER=%~dp0Core\tools\package_launcher_06551.cmd"
if not exist "%INNER%" (
  echo [ERROR] Package is incomplete or was not fully extracted.
  echo Missing:
  echo %INNER%
  echo.
  echo Extract the whole ZIP to a normal folder, then run this file again.
  echo.
  pause
  exit /b 5
)

call "%INNER%" "%~1"
set "RC=%ERRORLEVEL%"

echo.
echo ============================================================
if "%RC%"=="0" (
  echo   LAUNCHER FINISHED SUCCESSFULLY
) else (
  echo   LAUNCHER STOPPED WITH ERROR CODE %RC%
  echo   Send this window or the first error line back for diagnosis.
)
echo ============================================================
echo.
pause
exit /b %RC%
