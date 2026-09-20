@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
  echo Gaia Master B52R24 runtime capture analyzer
  echo.
  echo Kéo-thả GaiaMaster_B52R24_TRACE.tsv vào file CMD này.
  echo File GaiaMaster_B52R24_RAM.bin phải nằm cùng thư mục và cùng prefix.
  pause
  exit /b 2
)
python "%~dp0gaia_b52r24_trace_analyzer.py" "%~1"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R24 analysis complete.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
