@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" goto :usage
if not exist "%~f1" goto :missing
where py >nul 2>&1
if not errorlevel 1 goto :run_py
where python >nul 2>&1
if not errorlevel 1 goto :run_python
echo [ERROR] Python 3 was not found. Install Python 3 and enable PATH.
goto :failed
:run_py
py -3 "%~dp0gaia_b52r32_capture_session_manager.py" "%~f1" --advance-readonly
set "RC=%errorlevel%"
goto :done
:run_python
python "%~dp0gaia_b52r32_capture_session_manager.py" "%~f1" --advance-readonly
set "RC=%errorlevel%"
goto :done
:usage
echo Gaia Master B52R32 - SAFE READ-ONLY ADVANCE
echo.
echo Drag and drop the exact B52R14R1 BIN file onto this CMD file.
echo This tool runs static checks only and stops before PCSX runtime or ROM build.
set "RC=2"
goto :done
:missing
echo [ERROR] The dropped BIN file does not exist:
echo %~f1
set "RC=3"
goto :done
:failed
set "RC=4"
:done
echo.
if "%RC%"=="0" echo [OK] Check GaiaMaster_B52R32_SESSION_STATUS.txt next to your BIN.
if not "%RC%"=="0" echo [FAIL] Exit code %RC%.
pause
exit /b %RC%
