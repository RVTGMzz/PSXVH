@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Gaia Master 0.6.35.0 - Batch26 Final Exact Production Build
echo ============================================================
echo.

if "%~1"=="" (
    echo Drag the CLEAN Japan BIN onto this CMD file,
    echo or run it with the CLEAN BIN path as the first argument.
    echo.
    pause
    exit /b 2
)

python "%~dp0build_gaia_06350_batch26_final.py" "%~1"
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" (
    echo [FAILED] Builder exit code: %ERR%
) else (
    echo [OK] Build finished. Runtime screenshots/logs are still required.
)
echo.
pause
exit /b %ERR%
