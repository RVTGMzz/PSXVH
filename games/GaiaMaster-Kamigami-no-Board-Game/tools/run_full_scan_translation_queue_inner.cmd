@echo off
setlocal EnableExtensions
for %%I in ("%~dp0..\..\..") do set "ROOT=%%~fI"
cd /d "%ROOT%"

set "SCANNER=%ROOT%\Core\tools\scan_full_japanese_text_06380.py"
set "QUEUE=%ROOT%\Core\tools\prepare_full_scan_translation_queue_20260915.py"
set "LOG=%ROOT%\FULL_SCAN_TRANSLATION_QUEUE_LOG.txt"
set "BIN="

>"%LOG%" echo GAIA MASTER FULL SCAN TRANSLATION QUEUE LOGFIX
>>"%LOG%" echo ROOT=%ROOT%
>>"%LOG%" echo START=%DATE% %TIME%

echo.
echo ========================================================================
echo  GAIA MASTER - FULL JAPANESE SCAN + TRANSLATION QUEUE - LOGFIX
echo ========================================================================
echo.

if not exist "%SCANNER%" goto missing_scanner
if not exist "%QUEUE%" goto missing_queue

if not "%~1"=="" set "BIN=%~f1"
if defined BIN goto have_bin

for %%F in ("%ROOT%\*.bin") do if exist "%%~fF" if not defined BIN set "BIN=%%~fF"

:have_bin
if not defined BIN goto missing_bin
if not exist "%BIN%" goto missing_bin

for %%I in ("%BIN%") do set "OUTDIR=%%~dpI"
set "SCANCSV=%OUTDIR%GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv"
set "QUEUEDIR=%OUTDIR%GaiaMaster_TRANSLATION_QUEUE"

echo [INPUT] %BIN%
echo [OUT]   %OUTDIR%
>>"%LOG%" echo BIN=%BIN%
>>"%LOG%" echo OUTDIR=%OUTDIR%

where py >nul 2>nul
if not errorlevel 1 goto use_py
where python >nul 2>nul
if not errorlevel 1 goto use_python
goto missing_python

:use_py
>>"%LOG%" echo PYTHON=py -3
echo.
echo [STEP 1/2] Quet Japanese text...
py -3 "%SCANNER%" "%BIN%" >>"%LOG%" 2>&1
if errorlevel 1 goto scan_fail
echo [STEP 2/2] Tao translation queue...
py -3 "%QUEUE%" "%SCANCSV%" --out-dir "%QUEUEDIR%" >>"%LOG%" 2>&1
if errorlevel 1 goto queue_fail
goto done

:use_python
>>"%LOG%" echo PYTHON=python
echo.
echo [STEP 1/2] Quet Japanese text...
python "%SCANNER%" "%BIN%" >>"%LOG%" 2>&1
if errorlevel 1 goto scan_fail
echo [STEP 2/2] Tao translation queue...
python "%QUEUE%" "%SCANCSV%" --out-dir "%QUEUEDIR%" >>"%LOG%" 2>&1
if errorlevel 1 goto queue_fail
goto done

:missing_scanner
echo [ERROR] Missing scanner: %SCANNER%
>>"%LOG%" echo ERROR=missing scanner %SCANNER%
goto fail

:missing_queue
echo [ERROR] Missing queue builder: %QUEUE%
>>"%LOG%" echo ERROR=missing queue builder %QUEUE%
goto fail

:missing_bin
echo [ERROR] Khong tim thay CLEAN Japan .BIN canh launcher.
echo Dat file BIN vao cung thu muc package roi chay lai.
>>"%LOG%" echo ERROR=clean BIN not found
goto fail

:missing_python
echo [ERROR] Khong tim thay Python 3.
>>"%LOG%" echo ERROR=Python 3 not found
goto fail

:scan_fail
echo [ERROR] Scanner failed. Xem FULL_SCAN_TRANSLATION_QUEUE_LOG.txt
>>"%LOG%" echo ERROR=scanner failed
goto fail

:queue_fail
echo [ERROR] Queue builder failed. Xem FULL_SCAN_TRANSLATION_QUEUE_LOG.txt
>>"%LOG%" echo ERROR=queue builder failed
goto fail

:done
>>"%LOG%" echo STATUS=SUCCESS
>>"%LOG%" echo END=%DATE% %TIME%
echo.
echo ========================================================================
echo  DONE
echo ========================================================================
echo Queue:
echo   %QUEUEDIR%
echo.
echo Gui Ta file:
echo   GaiaMaster_TRANSLATION_QUEUE_HIGH_FIRST.csv
echo.
echo Log:
echo   %LOG%
echo.
echo Cua so nay se GIU NGUYEN de a xem ket qua.
exit /b 0

:fail
>>"%LOG%" echo STATUS=FAILED
>>"%LOG%" echo END=%DATE% %TIME%
echo.
echo Log da luu tai:
echo   %LOG%
echo.
echo Cua so nay se GIU NGUYEN. Gui Ta file log neu can.
exit /b 1
