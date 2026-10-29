@echo off
title NestKerala Platform
echo ===================================================
echo Starting NestKerala Real Estate Rental Platform
echo Find Your Perfect Home in Kerala
echo ===================================================
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" app.py
) else (
    call .venv\Scripts\activate.bat
    python app.py
)
pause
