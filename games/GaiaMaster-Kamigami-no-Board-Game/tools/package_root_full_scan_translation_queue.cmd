@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "ROOT=%%~fI"
cd /d "%ROOT%"

title Gaia Master - Full Japanese Scan + Translation Queue

set "SCANNER=%ROOT%\Core\tools\scan_full_japanese_text_06380.py"
set "QUEUE=%ROOT%\Core\tools\prepare_full_scan_translation_queue_20260915.py"
set "BIN="

echo.
echo ========================================================================
echo  GAIA MASTER - FULL JAPANESE SCAN + REVIEWED-DEDUPED TRANSLATION QUEUE
echo ========================================================================
echo.

if not exist "%SCANNER%" (
  echo [ERROR] Missing scanner:
  echo         %SCANNER%
  goto :fail
)
if not exist "%QUEUE%" (
  echo [ERROR] Missing queue builder:
  echo         %QUEUE%
  goto :fail
)

if not "%~1"=="" (
  set "BIN=%~f1"
)

if not defined BIN (
  for %%F in ("%ROOT%\*.bin") do (
    if not defined BIN set "BIN=%%~fF"
  )
)

if not defined BIN (
  echo [ERROR] Khong tim thay file .BIN.
  echo.
  echo Dat CLEAN Gaia Master Japan .BIN canh file CMD nay,
  echo hoac keo-tha CLEAN .BIN truc tiep len CMD.
  echo.
  echo CLEAN SHA1 bat buoc:
  echo f4d5298583c90d89c4b7e51d2dde160ee07f2aec
  goto :fail
)

if not exist "%BIN%" (
  echo [ERROR] BIN khong ton tai:
  echo         %BIN%
  goto :fail
)

for %%I in ("%BIN%") do set "OUTDIR=%%~dpI"
set "SCANCSV=%OUTDIR%GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN.csv"
set "QUEUEDIR=%OUTDIR%GaiaMaster_TRANSLATION_QUEUE"

echo [INPUT] %BIN%
echo [OUT]   %OUTDIR%
echo.

where py >nul 2>nul
if not errorlevel 1 (
  echo [STEP 1/2] Quet toan bo Japanese text...
  py -3 "%SCANNER%" "%BIN%"
  if errorlevel 1 goto :scan_fail
  echo.
  echo [STEP 2/2] Tao reviewed-deduped translation queue...
  py -3 "%QUEUE%" "%SCANCSV%" --out-dir "%QUEUEDIR%"
  if errorlevel 1 goto :queue_fail
  goto :done
)

where python >nul 2>nul
if not errorlevel 1 (
  echo [STEP 1/2] Quet toan bo Japanese text...
  python "%SCANNER%" "%BIN%"
  if errorlevel 1 goto :scan_fail
  echo.
  echo [STEP 2/2] Tao reviewed-deduped translation queue...
  python "%QUEUE%" "%SCANCSV%" --out-dir "%QUEUEDIR%"
  if errorlevel 1 goto :queue_fail
  goto :done
)

echo [ERROR] Khong tim thay Python 3.
echo Cai Python 3 va bat tuy chon Add Python to PATH, sau do chay lai.
goto :fail

:scan_fail
echo.
echo [FAILED] Scanner dung lai.
echo Kiem tra dung CLEAN Japan BIN SHA1:
echo f4d5298583c90d89c4b7e51d2dde160ee07f2aec
goto :fail

:queue_fail
echo.
echo [FAILED] Scanner da tao CSV nhung translation queue builder bi loi.
echo Gui lai cac file sau neu can chan doan:
echo   %SCANCSV%
echo   %OUTDIR%GaiaMaster_0.6.38.0_FULL_JAPANESE_SCAN_REPORT.txt
goto :fail

:done
echo.
echo ========================================================================
echo  DONE
echo ========================================================================
echo Full scanner CSV:
echo   %SCANCSV%
echo.
echo Translation queue folder:
echo   %QUEUEDIR%
echo.
echo Uu tien gui file:
echo   GaiaMaster_TRANSLATION_QUEUE_HIGH_FIRST.csv
echo.
echo Luu y: day la source-translation queue, KHONG phai Runtime PASS.
echo.
pause
exit /b 0

:fail
echo.
pause
exit /b 1
