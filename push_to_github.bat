@echo off
echo ========================================================
echo Pushing NestKerala to GitHub (kerala-trip)
echo ========================================================

cd /d "C:\Users\Dell\Documents\nestkerala"

REM Check if git is available
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your system PATH.
    echo Please install Git for Windows from: https://git-scm.com/download/win
    echo Then run this file again.
    pause
    exit /b 1
)

echo [1/5] Initializing Git repository...
if not exist ".git" (
    git init
)

echo [2/5] Staging files...
git add .

echo [3/5] Creating commit...
git commit -m "Complete NestKerala Platform with Feedback & Reviews System"

echo [4/5] Setting main branch and remote origin...
git branch -M main
git remote remove origin 2>nul
git remote add origin git@github.com:fathimafarhana8714-rgb/kerala-trip.git

echo [5/5] Pushing to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo SUCCESS! Your project has been pushed to GitHub:
    echo git@github.com:fathimafarhana8714-rgb/kerala-trip.git
    echo ========================================================
) else (
    echo.
    echo [NOTE] If SSH key is not configured, try pushing via HTTPS:
    echo git remote set-url origin https://github.com/fathimafarhana8714-rgb/kerala-trip.git
    echo git push -u origin main
)

pause
