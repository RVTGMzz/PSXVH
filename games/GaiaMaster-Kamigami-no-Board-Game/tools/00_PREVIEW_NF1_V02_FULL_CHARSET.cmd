@echo off
setlocal DisableDelayedExpansion
set "OUT=%~dp0..\font_experiment\NF1_V02_FULL_CHARSET.svg"
if not exist "%~dp0..\font_experiment" mkdir "%~dp0..\font_experiment"
where py >nul 2>&1
if not errorlevel 1 goto :py
where python >nul 2>&1
if not errorlevel 1 goto :python
echo [ERROR] Python 3 was not found.
goto :fail
:py
py -3 "%~dp0gaia_nf1_full_font_art_v02.py" --selftest --svg "%OUT%"
goto :after
:python
python "%~dp0gaia_nf1_full_font_art_v02.py" --selftest --svg "%OUT%"
:after
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :done
echo [OK] Full NF1 V0.2 preview created: "%OUT%"
start "" "%OUT%"
goto :done
:fail
set "RC=4"
:done
echo.
if not "%RC%"=="0" echo [FAIL] Exit code %RC%.
pause
exit /b %RC%
