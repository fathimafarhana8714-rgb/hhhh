@echo off
echo ========================================================
echo Pushing NestKerala to GitHub (fathimafarhana8714-rgb/kerala-trip)
echo ========================================================

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo Using secure Python SSH push runner...
    ".venv\Scripts\python.exe" push_with_key.py
    pause
    exit /b %errorlevel%
)

where git >nul 2>nul
if %errorlevel% equ 0 (
    git add .
    git commit -m "Update NestKerala repository"
    git push -u origin main
    pause
    exit /b %errorlevel%
)

echo [ERROR] Neither Python venv nor git found.
pause
