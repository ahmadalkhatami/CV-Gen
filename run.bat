@echo off
title CV Generator - ATS Friendly
color 0A

echo ============================================
echo   CV Generator - ATS Friendly
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python dari https://python.org
    pause
    exit /b 1
)

:: Install dependencies if not already installed
echo Menginstall dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Gagal install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Membuka browser...
echo   URL: http://localhost:5000
echo   Tekan CTRL+C untuk berhenti
echo ============================================
echo.

:: Open browser after a short delay
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Run Flask app
python app.py

pause
