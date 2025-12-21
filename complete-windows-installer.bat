@echo off
echo =====================================================
echo  Kyber1024 Quantum-Safe Cryptography Suite - Installer
echo  Version: 3.0 | Platform: Windows
echo =====================================================
echo.

REM Function to check if a command exists
where /q %1
if %errorlevel% neq 0 (
    exit /b 1
) else (
    exit /b 0
)

:CHECK_PYTHON
echo Checking for Python...
call :CHECK_CMD python
if %errorlevel% equ 1 (
    echo Python not found. Checking for Python Launcher...
    call :CHECK_CMD py
    if %errorlevel% equ 1 (
        goto :INSTALL_PYTHON
    ) else (
        set PYTHON_CMD=py -3
        goto :CHECK_PIP
    )
) else (
    set PYTHON_CMD=python
    goto :CHECK_PIP
)

:CHECK_PIP
echo Checking for pip...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip not found. Installing pip...
    %PYTHON_CMD% -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        echo Failed to install pip.
        goto :INSTALL_PIP
    )
)

goto :RUN_INSTALLER

:INSTALL_PYTHON
echo.
echo =====================================================
echo  Python Installation Required
echo =====================================================
echo.
echo Python 3.8+ is required but not found on your system.
echo.
echo Please choose an installation method:
echo.
echo [1] Download Python from python.org (Recommended)
echo [2] Use Windows Package Manager (winget)
echo [3] Use Chocolatey (if installed)
echo [4] Exit installation
echo.
set /p CHOICE="Enter your choice (1-4): "

if "%CHOICE%"=="1" (
    start "" "https://www.python.org/downloads/"
    echo.
    echo Please download and install Python 3.8+ from the website.
    echo Make sure to check "Add Python to PATH" during installation.
    echo After installation, re-run this installer.
    pause
    exit /b 0
) else if "%CHOICE%"=="2" (
    call :CHECK_CMD winget
    if %errorlevel% equ 1 (
        echo winget not available. Installing from Microsoft Store...
        start ms-windows-store://pdp/?productid=9NBLGGH4NNS1
    ) else (
        winget install Python.Python.3.11
    )
    echo After installation, re-run this installer.
    pause
    exit /b 0
) else if "%CHOICE%"=="3" (
    call :CHECK_CMD choco
    if %errorlevel% equ 1 (
        echo Chocolatey not installed.
        echo Install from https://chocolatey.org/ then re-run.
        pause
        exit /b 0
    ) else (
        choco install python3
        echo After installation, re-run this installer.
        pause
        exit /b 0
    )
) else (
    echo Installation cancelled.
    pause
    exit /b 0
)

:INSTALL_PIP
echo.
echo =====================================================
echo  Pip Installation Required
echo =====================================================
echo.
echo pip (Python package manager) is not available.
echo.
echo [1] Download get-pip.py and install
echo [2] Install via ensurepip
echo [3] Exit installation
echo.
set /p CHOICE="Enter choice (1-3): "

if "%CHOICE%"=="1" (
    echo Downloading get-pip.py...
    powershell -Command "Invoke-WebRequest https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py"
    %PYTHON_CMD% get-pip.py
    del get-pip.py
    if %errorlevel% equ 0 (
        echo pip installed successfully.
        goto :RUN_INSTALLER
    ) else (
        echo Failed to install pip.
        pause
        exit /b 1
    )
) else if "%CHOICE%"=="2" (
    %PYTHON_CMD% -m ensurepip --upgrade
    if %errorlevel% equ 0 (
        echo pip installed successfully.
        goto :RUN_INSTALLER
    ) else (
        echo Failed to install pip.
        pause
        exit /b 1
    )
) else (
    echo Installation cancelled.
    pause
    exit /b 0
)

:RUN_INSTALLER
echo.
echo =====================================================
echo  Running Kyber1024 Installer
echo =====================================================
echo.
echo Python: %PYTHON_CMD%
echo.

REM Check if install.py exists, otherwise download it
if not exist "install.py" (
    echo Downloading installer...
    powershell -Command "Invoke-WebRequest https://raw.githubusercontent.com/Basty-devel/-Kyber1024-Quantum-Safe-Cryptography-Suite-v3.0/main/install.py -OutFile install.py"
)

%PYTHON_CMD% install.py %*

if %errorlevel% equ 0 (
    echo.
    echo =====================================================
    echo  Installation Successful!
    echo =====================================================
    echo.
    echo To run the application:
    echo   activate_venv.bat
    echo   python kyber1024.py
    echo.
    if exist "dist\Kyber1024-Suite.exe" (
        echo Or use the standalone executable:
        echo   dist\Kyber1024-Suite.exe
    )
) else (
    echo.
    echo =====================================================
    echo  Installation Failed
    echo =====================================================
)

pause