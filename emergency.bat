@echo off
echo ===========================================
echo KYBER1024 EMERGENCY RECOVERY
echo ===========================================
echo.
echo This script will try to recover your installation.
echo.

REM Check if Python exists
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if we can run the main script
if exist "kyber1024.py" (
    echo Found main script. Attempting to run...
    python kyber1024.py --recovery-mode
) else (
    echo Main script not found.
    echo Downloading from GitHub...
    powershell -Command "Invoke-WebRequest 'https://raw.githubusercontent.com/Basty-devel/-Kyber1024-Quantum-Safe-Cryptography-Suite-v3.0/main/kyber1024.py' -OutFile 'kyber1024.py'"
    if exist "kyber1024.py" (
        python kyber1024.py --recovery-mode
    ) else (
        echo Emergency recovery failed.
    )
)

pause