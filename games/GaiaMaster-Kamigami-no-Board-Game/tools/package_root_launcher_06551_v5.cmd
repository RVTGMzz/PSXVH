@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Gaia Master 0.6.55.1 - Rename-Safe Log Launcher

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
cd /d "%ROOT%"
set "LOG=%ROOT%\BUILD_LOG_0.6.55.1_R2.txt"
set "DRIVER=%ROOT%\Core\tools\package_driver_06551_logsafe.py"

>"%LOG%" echo GAIA MASTER 0.6.55.1 - ROOT LAUNCHER STARTED
>>"%LOG%" echo Time: %DATE% %TIME%
>>"%LOG%" echo Root: %ROOT%

echo ============================================================
echo   GAIA MASTER 0.6.55.1 - ROOT LAUNCHER STARTED
echo ============================================================
echo Persistent log:
echo %LOG%
echo.

if not exist "%DRIVER%" goto MISSING_DRIVER

where py >nul 2>&1
if errorlevel 1 goto TRY_PYTHON
py -3 "%DRIVER%" "%ROOT%"
set "RC=%ERRORLEVEL%"
goto AFTER_RUN

:TRY_PYTHON
where python >nul 2>&1
if errorlevel 1 goto NO_PYTHON
python "%DRIVER%" "%ROOT%"
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

if /I "%GAIA_CI%"=="1" exit /b %RC%

echo The log file will now open in Notepad.
echo Send BUILD_LOG_0.6.55.1_R2.txt if RETURN CODE is not 0.
start "" notepad.exe "%LOG%"
echo.
pause
exit /b %RC%
