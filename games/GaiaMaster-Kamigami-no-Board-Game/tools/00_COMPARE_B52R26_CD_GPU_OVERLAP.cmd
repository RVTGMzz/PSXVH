@echo off
setlocal
chcp 65001 >nul
if "%~2"=="" (
 echo Gaia Master B52R26 CD-to-GPU overlap analyzer
 echo.
 echo Chạy với 2 file:
 echo   GaiaMaster_B52R24_TRACE.tsv
 echo   GaiaMaster_B52R26_CD_DMA_TRACE.tsv
 pause
 exit /b 2
)
python "%~dp0gaia_b52r26_cd_gpu_overlap_analyzer.py" "%~1" "%~2"
set ERR=%ERRORLEVEL%
echo.
if "%ERR%"=="0" echo [OK] B52R26 overlap analysis complete.
if not "%ERR%"=="0" echo [FAIL] exit code %ERR%
pause
exit /b %ERR%
