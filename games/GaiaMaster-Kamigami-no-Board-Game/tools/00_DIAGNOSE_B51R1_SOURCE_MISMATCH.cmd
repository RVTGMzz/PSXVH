@echo off
setlocal
cd /d "%~dp0.."
set "CLEAN=GaiaMaster - Kamigami no Board Game (Japan).bin"
python tools\diagnose_b51r1_source_mismatch.py "%CLEAN%"
echo.
pause
