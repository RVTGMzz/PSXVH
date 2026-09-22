@echo off
setlocal
chcp 65001 >nul
if "%~3"=="" (
 echo Gaia Master B52R31 GUARDED DRY-RUN
 echo.
 echo Usage:
 echo   %~nx0 "B52R14R1.bin" "GaiaMaster_B52R30_PATCH_PLAN.json" "replacement.bin"
 echo.
 echo This launcher NEVER writes a BIN.
 pause
 exit /b 2
)
python "%~dp0gaia_b52r31_guarded_candidate_builder.py" "%~1" "%~2" "%~3"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R31 guarded dry-run PASS.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
