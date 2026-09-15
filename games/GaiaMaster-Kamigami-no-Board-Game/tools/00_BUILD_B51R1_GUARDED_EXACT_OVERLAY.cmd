@echo off
setlocal
cd /d "%~dp0.."

set "CLEAN=%~1"
set "BASE=%~2"

if not defined CLEAN set "CLEAN=GaiaMaster - Kamigami no Board Game (Japan).bin"
if not defined BASE (
  echo ================================================================
  echo GAIA MASTER B51R1 - GUARDED BUILD
  echo ================================================================
  echo CLEAN: "%CLEAN%"
  echo.
  echo Enter the KNOWN-GOOD runtime base BIN path.
  echo It must already pass frozen-60 plus 560/102/19 historical gates.
  echo Do NOT enter the CLEAN BIN here.
  echo.
  set /p "BASE=Runtime base BIN: "
)

if not defined BASE (
  echo [ERROR] Runtime base BIN is required.
  pause
  exit /b 2
)

echo.
echo CLEAN: "%CLEAN%"
echo BASE : "%BASE%"
echo.
python tools\build_gaia_b51r1_guarded_exact_overlay.py "%CLEAN%" --build-from "%BASE%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo [OK] B51R1 guarded build + static byte verification completed.
  echo [NOTE] Runtime PASS is still NO until gameplay screenshots are reviewed.
) else (
  echo [ERROR] B51R1 guarded build failed with exit code %RC%.
  echo [STOP] Keep the previous known-good runtime build.
)

pause
exit /b %RC%
