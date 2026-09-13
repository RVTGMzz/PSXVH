@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
  echo.
  echo Gaia Master Font Mapping Initializer Scanner 0.2
  echo READ ONLY - khong sua ROM.
  echo.
  echo Keo file CLEAN BIN vao file CMD nay,
  echo hoac dat BIN cung thu muc voi tool.
  echo.
  python font_mapping_initializer_scanner_0.2.py
) else (
  python font_mapping_initializer_scanner_0.2.py "%~1"
)

echo.
echo Nhan phim bat ky de dong.
pause >nul
endlocal
