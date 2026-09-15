@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Gaia Master 0.6.55.1 - Direct Font-Only Patch

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
cd /d "%ROOT%"
set "PATCHER=%ROOT%\Core\tools\patch_gaia_06551_from_06550_direct.py"

echo ============================================================
echo   GAIA MASTER 0.6.55.1 - DIRECT FONT-ONLY PATCH
echo ============================================================
echo Input required beside this CMD:
echo   1. CLEAN Japan BIN
echo   2. The proven 0.6.55.0 HYBRID GAMEPLAY BIN
echo.

if not exist "%PATCHER%" goto MISSING

where py >nul 2>&1
if errorlevel 1 goto TRY_PYTHON
py -3 "%PATCHER%" "%ROOT%"
set "RC=%ERRORLEVEL%"
goto DONE

:TRY_PYTHON
where python >nul 2>&1
if errorlevel 1 goto NOPY
python "%PATCHER%" "%ROOT%"
set "RC=%ERRORLEVEL%"
goto DONE

:MISSING
echo [ERROR] Missing direct patcher:
echo %PATCHER%
set "RC=5"
goto DONE

:NOPY
echo [ERROR] Python 3 not found in PATH.
set "RC=4"

:DONE
echo.
echo ============================================================
echo   RETURN CODE: %RC%
echo ============================================================
echo.
if exist "%ROOT%\PATCH_LOG_0.6.55.1_R2.txt" type "%ROOT%\PATCH_LOG_0.6.55.1_R2.txt"
echo.
if /I "%GAIA_CI%"=="1" exit /b %RC%
echo If RETURN CODE is not 0, send PATCH_LOG_0.6.55.1_R2.txt
pause
exit /b %RC%
