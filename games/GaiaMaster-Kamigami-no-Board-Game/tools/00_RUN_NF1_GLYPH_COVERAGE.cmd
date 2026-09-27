@echo off
setlocal
python "%~dp0gaia_nf1_glyph_coverage.py"
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" echo [OK] NF1 glyph coverage report created.
if not "%RC%"=="0" echo [FAIL] exit code %RC%.
pause
exit /b %RC%
