@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" goto :usage
if not exist "%~f1" goto :missing
where py >nul 2>&1
if not errorlevel 1 goto :py
where python >nul 2>&1
if not errorlevel 1 goto :python
echo [ERROR] Python 3 was not found.
goto :fail
:py
py -3 "%~dp0gaia_nf2_cache_advance_probe.py" "%~f1"
goto :after
:python
python "%~dp0gaia_nf2_cache_advance_probe.py" "%~f1"
:after
set "RC=%ERRORLEVEL%"
goto :done
:usage
echo Gaia Master NF2 - CACHE ADVANCE PROBE
echo.
echo Drag and drop exact B52R14R1 or CLEAN BIN onto this CMD file.
echo READ ONLY. It does not patch the game.
set "RC=2"
goto :done
:missing
echo [ERROR] BIN does not exist:
echo %~f1
set "RC=3"
goto :done
:fail
set "RC=4"
:done
echo.
if "%RC%"=="0" echo [OK] NF2 report, CSV and PCSX Lua were created next to the BIN.
if not "%RC%"=="0" echo [FAIL] Exit code %RC%.
pause
exit /b %RC%
