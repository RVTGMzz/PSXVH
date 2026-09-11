@echo off
setlocal
cd /d "%~dp0"
set "BIN=%~1"
if "%BIN%"=="" set "BIN=%~dp0..\GaiaMaster - Kamigami no Board Game (Japan).bin"
if not exist "%BIN%" (
  echo ERROR: Original BIN not found.
  echo Drag the original BIN onto this BAT, or place it one folder above tools.
  pause
  exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0diagnostic_isolate_0.1.5.py" jp_slps "%BIN%"
) else (
  python "%~dp0diagnostic_isolate_0.1.5.py" jp_slps "%BIN%"
)
echo.
pause
