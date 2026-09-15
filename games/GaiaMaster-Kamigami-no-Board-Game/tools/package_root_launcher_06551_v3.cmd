@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Gaia Master 0.6.55.1 - Persistent Log Launcher
cd /d "%~dp0"
set "LOG=%~dp0BUILD_LOG_0.6.55.1_BATCH45R2.txt"
set "DRIVER=%~dp0Core\tools\package_driver_06551.py"

>"%LOG%" echo GAIA MASTER 0.6.55.1 - ROOT LAUNCHER STARTED
>>"%LOG%" echo Time: %DATE% %TIME%
>>"%LOG%" echo Root: %~dp0

echo ============================================================
echo   GAIA MASTER 0.6.55.1 - ROOT LAUNCHER STARTED
echo ============================================================
echo A persistent log is being written to:
echo %LOG%
echo.

if not exist "%DRIVER%" goto MISSING_DRIVER

where py >nul 2>&1
if errorlevel 1 goto TRY_PYTHON
py -3 "%DRIVER%" "%~dp0" >>"%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
goto AFTER_RUN

:TRY_PYTHON
where python >nul 2>&1
if errorlevel 1 goto NO_PYTHON
python "%DRIVER%" "%~dp0" >>"%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
goto AFTER_RUN

:MISSING_DRIVER
>>"%LOG%" echo [ERROR] Missing driver: %DRIVER%
set "RC=5"
goto AFTER_RUN

:NO_PYTHON
>>"%LOG%" echo [ERROR] Python 3 not found. Neither py nor python is available in PATH.
set "RC=4"
goto AFTER_RUN

:AFTER_RUN
>>"%LOG%" echo ROOT LAUNCHER RETURN CODE: %RC%
echo.
echo ============================================================
echo   RETURN CODE: %RC%
echo ============================================================
echo.
type "%LOG%"
echo.
echo The log file will now open in Notepad.
echo Send BUILD_LOG_0.6.55.1_BATCH45R2.txt if RETURN CODE is not 0.
start "" notepad.exe "%LOG%"
echo.
pause
exit /b %RC%
