@echo off
setlocal
cd /d "%~dp0.."

set "CLEAN=%~1"
if not defined CLEAN set "CLEAN=GaiaMaster - Kamigami no Board Game (Japan).bin"

echo ================================================================
echo GAIA MASTER B51R1 - GUARDED DRY-RUN
echo ================================================================
echo CLEAN: "%CLEAN%"
echo.

python tools\build_gaia_b51r1_guarded_exact_overlay.py "%CLEAN%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo [OK] B51R1 guarded dry-run completed.
  echo [NOTE] This is NOT Runtime PASS. Build and gameplay screenshots are still required.
) else (
  echo [ERROR] B51R1 guarded dry-run failed with exit code %RC%.
  echo [STOP] Do not build until this dry-run is clean.
)

pause
exit /b %RC%
