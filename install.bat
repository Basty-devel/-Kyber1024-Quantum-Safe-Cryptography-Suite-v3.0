@echo off
echo ============================================
echo  Kyber1024 Suite Installer (Windows)
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Run the installer
python install.py %*

if errorlevel 0 (
    echo.
    echo Installation successful!
    echo.
    echo To activate the virtual environment and run:
    echo   activate_venv.bat
    echo   python kyber1024.py
    echo.
    pause
) else (
    echo.
    echo Installation failed!
    pause
    exit /b %errorlevel%
)