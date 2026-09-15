@echo off
setlocal
cd /d "%~dp0.."

set "CLEAN=%~1"
set "SCAN=%~2"

if not defined CLEAN set "CLEAN=GaiaMaster - Kamigami no Board Game (Japan).bin"
if not defined SCAN set "SCAN=."

echo ================================================================
echo GAIA MASTER B51R1 - READ-ONLY RUNTIME BASE FINDER
echo ================================================================
echo CLEAN    : "%CLEAN%"
echo SCAN DIR : "%SCAN%"
echo.

python tools\find_gaia_b51r1_runtime_base.py "%CLEAN%" --dir "%SCAN%"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo [OK] At least one valid runtime base was found.
) else (
  echo [NOTE] No valid runtime base was confirmed. Exit code %RC%.
)
echo [SAFE] This finder is read-only and does not modify BIN files.

pause
exit /b %RC%
