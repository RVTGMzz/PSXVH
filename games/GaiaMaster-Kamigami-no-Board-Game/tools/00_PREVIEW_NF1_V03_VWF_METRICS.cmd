@echo off
setlocal DisableDelayedExpansion
set "OUT=%~dp0..\font_experiment\NF1_V03_VWF_PREVIEW.svg"
set "CSV=%~dp0..\font_experiment\NF1_V03_WIDTH_METRICS.csv"
if not exist "%~dp0..\font_experiment" mkdir "%~dp0..\font_experiment"
where py >nul 2>&1
if not errorlevel 1 goto :py
where python >nul 2>&1
if not errorlevel 1 goto :python
echo [ERROR] Python 3 was not found.
goto :fail
:py
py -3 "%~dp0gaia_nf1_v03_width_metrics.py" --selftest --svg "%OUT%" --csv "%CSV%"
goto :after
:python
python "%~dp0gaia_nf1_v03_width_metrics.py" --selftest --svg "%OUT%" --csv "%CSV%"
:after
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" goto :done
echo [OK] V0.3 proportional preview created: "%OUT%"
start "" "%OUT%"
goto :done
:fail
set "RC=4"
:done
echo.
if not "%RC%"=="0" echo [FAIL] Exit code %RC%.
pause
exit /b %RC%
