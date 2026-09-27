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
py -3 "%~dp0build_gaia_nf1_new_font.py" "%~f1"
goto :after
:python
python "%~dp0build_gaia_nf1_new_font.py" "%~f1"
:after
set "RC=%ERRORLEVEL%"
goto :done
:usage
echo Gaia Master NF1 - NEW VIETNAMESE FONT BUILD
echo.
echo Drag and drop the exact B52R14R1 BIN onto this CMD file.
echo Input is never overwritten. A new BIN/CUE is created next to it.
set "RC=2"
goto :done
:missing
echo [ERROR] Dropped BIN does not exist:
echo %~f1
set "RC=3"
goto :done
:fail
set "RC=4"
:done
echo.
if "%RC%"=="0" echo [OK] NF1 static build/readback completed. Runtime screenshot is still required.
if not "%RC%"=="0" echo [FAIL] Exit code %RC%.
pause
exit /b %RC%
