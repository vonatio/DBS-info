@echo off
chcp 65001 >nul
title HTML Report Publisher v2.0

echo ====================================================
echo   HTML Report Publisher v2.0
echo ====================================================
echo.
echo   [1] Publish ALL (public + internal)
echo   [2] Public only (GitHub Pages)
echo   [3] Internal only (shared folder)
echo   [4] List all registered reports
echo.

set /p choice="Select [1-4, default=1]: "

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

cd /d D:\Claude\DBS-info

if "%choice%"=="2" (
    python publish.py --public-only
) else if "%choice%"=="3" (
    python publish.py --internal-only
) else if "%choice%"=="4" (
    python publish.py --list
) else (
    python publish.py
)

pause
