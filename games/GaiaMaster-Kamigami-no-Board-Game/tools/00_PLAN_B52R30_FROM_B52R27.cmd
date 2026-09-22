@echo off
setlocal
chcp 65001 >nul
if "%~3"=="" (
  echo Gaia Master B52R30 ownership + patch planner
  echo.
  echo Usage:
  echo   %~nx0 "B52R14R1.bin" "GaiaMaster_B52R27_DISC_FINGERPRINT_CANDIDATES.csv" "GaiaMaster_B52R24_DMA_SOURCE.bin" [row] [replacement.bin]
  echo.
  echo Tool is READ ONLY. It never patches the BIN.
  pause
  exit /b 2
)
set ROW=%~4
if "%ROW%"=="" set ROW=1
if "%~5"=="" (
  python "%~dp0gaia_b52r30_ownership_patch_planner.py" "%~1" --candidate-csv "%~2" --row %ROW% --payload "%~3"
) else (
  python "%~dp0gaia_b52r30_ownership_patch_planner.py" "%~1" --candidate-csv "%~2" --row %ROW% --payload "%~3" --replacement "%~5"
)
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R30 ownership/patch plan complete.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
