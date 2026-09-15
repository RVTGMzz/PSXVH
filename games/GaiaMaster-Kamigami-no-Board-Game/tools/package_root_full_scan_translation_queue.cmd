@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "ROOT=%%~fI"
cd /d "%ROOT%"
set "INNER=%ROOT%\Core\tools\run_full_scan_translation_queue_inner.cmd"

title Gaia Master - Full Japanese Scan LOGFIX

echo.
echo ========================================================================
echo  GAIA MASTER - FULL JAPANESE SCAN + TRANSLATION QUEUE - LOGFIX
echo ========================================================================
echo.

if exist "%INNER%" goto inner_ok
echo [ERROR] Missing inner runner:
echo "%INNER%"
echo.
echo Package khong day du. Hay dung goi LOGFIX moi.
echo.
pause
exit /b 1

:inner_ok
if "%~1"=="" goto no_arg
"%ComSpec%" /d /k call "%INNER%" "%~f1"
exit /b %errorlevel%

:no_arg
"%ComSpec%" /d /k call "%INNER%"
exit /b %errorlevel%
