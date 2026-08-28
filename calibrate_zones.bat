@echo off
echo ========================================
echo AutoGuard Zone Calibrator
echo ========================================
echo.
echo This tool helps you set up detection zones for your camera
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python -m src.zone_calibrator
pause
