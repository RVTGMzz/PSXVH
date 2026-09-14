@echo off
setlocal
cd /d "%~dp0"
python gaia_batch19_report_compiler_06280.py
if errorlevel 1 (
  echo.
  echo [FAIL] Batch 19 report compiler returned an error.
  pause
  exit /b 1
)
echo.
echo [OK] Reports written to checkpoints\0.6.28.0\reports
pause
