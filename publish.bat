@echo off
chcp 65001 >nul
title Publish to GitHub Pages

echo ====================================================
echo   DBS Info - Publish to GitHub Pages
echo ====================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

cd /d D:\Claude\DBS-info
python publish.py

pause
