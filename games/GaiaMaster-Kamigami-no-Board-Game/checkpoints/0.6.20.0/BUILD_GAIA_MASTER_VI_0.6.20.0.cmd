@echo off
setlocal
cd /d "%~dp0"
title Gaia Master VI 0.6.20.0 - Batch 11

echo.
echo ============================================================
echo  GAIA MASTER VI 0.6.20.0 - STORY DIALOG CARD BATCH 11
echo ============================================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Khong tim thay Python Launcher "py".
    pause
    exit /b 10
)

py -3 "%~dp0build_gaia_06200_ONE_FOLDER.py"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo [DONE] Build hoan tat. Mo CUE 0.6.20.0 de test.
) else (
    echo [FAILED] Exit code: %RC%
)
echo.
pause
exit /b %RC%
