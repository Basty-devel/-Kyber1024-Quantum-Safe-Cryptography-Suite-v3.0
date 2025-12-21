#!/bin/bash

echo "============================================"
echo " Kyber1024 Suite Installer (Linux/macOS)"
echo "============================================"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Please install Python 3.8+ first."
    echo ""
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "Fedora: sudo dnf install python3 python3-pip"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS: brew install python@3.10"
    fi
    
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_MAJOR=3
REQUIRED_MINOR=8

if [[ $(echo "$PYTHON_VERSION < $REQUIRED_MAJOR.$REQUIRED_MINOR" | bc) -eq 1 ]]; then
    echo "Python $PYTHON_VERSION is too old. Need 3.8+"
    exit 1
fi

echo "Using Python $PYTHON_VERSION"
echo ""

# Make install.py executable
chmod +x install.py

# Run installer
python3 install.py "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo "Installation successful!"
    echo ""
    echo "To activate the virtual environment and run:"
    echo "  source activate_venv.sh"
    echo "  python kyber1024.py"
    echo ""
else
    echo ""
    echo "Installation failed!"
    exit 1
fi