#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "====================================================="
echo " Kyber1024 Quantum-Safe Cryptography Suite - Installer"
echo " Version: 3.0 | Platform: $(uname -s)"
echo "====================================================="
echo -e "${NC}"

check_command() {
    command -v "$1" >/dev/null 2>&1
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to install Python based on platform
install_python() {
    print_warning "Python 3.8+ is required but not found."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_info "Linux detected. Installing Python..."
        
        if check_command apt-get; then
            # Debian/Ubuntu
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            PYTHON_CMD="python3"
            
        elif check_command dnf; then
            # Fedora
            sudo dnf install -y python3 python3-pip python3-virtualenv
            PYTHON_CMD="python3"
            
        elif check_command pacman; then
            # Arch
            sudo pacman -S --noconfirm python python-pip python-virtualenv
            PYTHON_CMD="python"
            
        elif check_command zypper; then
            # openSUSE
            sudo zypper install -y python3 python3-pip python3-virtualenv
            PYTHON_CMD="python3"
            
        else
            print_error "Unsupported package manager. Please install Python manually."
            echo "Visit: https://www.python.org/downloads/"
            exit 1
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "macOS detected."
        
        if check_command brew; then
            print_info "Installing Python via Homebrew..."
            brew install python@3.10
            PYTHON_CMD="python3"
        else
            print_warning "Homebrew not found. Please choose:"
            echo "1) Install Homebrew first (recommended)"
            echo "2) Download Python from python.org"
            echo "3) Use built-in Python (may be outdated)"
            echo -n "Choice [1-3]: "
            read -r choice
            
            case $choice in
                1)
                    print_info "Installing Homebrew..."
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                    brew install python@3.10
                    PYTHON_CMD="python3"
                    ;;
                2)
                    open "https://www.python.org/downloads/macos/"
                    print_info "Please download and install Python, then re-run this script."
                    exit 0
                    ;;
                3)
                    if check_command python3; then
                        PYTHON_CMD="python3"
                    else
                        print_error "Python not found. Please install Python first."
                        exit 1
                    fi
                    ;;
                *)
                    print_error "Invalid choice."
                    exit 1
                    ;;
            esac
        fi
    else
        print_error "Unsupported operating system."
        exit 1
    fi
}

# Function to install pip
install_pip() {
    print_warning "pip not found. Installing pip..."
    
    if check_command curl; then
        curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    elif check_command wget; then
        wget -q https://bootstrap.pypa.io/get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    else
        $PYTHON_CMD -m ensurepip --upgrade
    fi
    
    if [ $? -eq 0 ]; then
        print_success "pip installed successfully"
    else
        print_error "Failed to install pip"
        exit 1
    fi
}

# Function to install system dependencies for liboqs
install_system_deps() {
    print_info "Installing system dependencies for quantum-safe cryptography..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if check_command apt-get; then
            sudo apt install -y build-essential cmake ninja-build gcc g++ python3-dev libssl-dev
        elif check_command dnf; then
            sudo dnf install -y gcc gcc-c++ cmake ninja-build python3-devel openssl-devel
        elif check_command pacman; then
            sudo pacman -S --noconfirm base-devel cmake ninja gcc python openssl
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if check_command brew; then
            brew install cmake ninja openssl
        else
            print_warning "Some system dependencies may need manual installation"
        fi
    fi
}

# Main installation flow
main() {
    # Check for Python
    if check_command python3; then
        PYTHON_CMD="python3"
        print_success "Python found: $(python3 --version)"
    elif check_command python; then
        # Check Python version
        python_version=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [[ $(echo "$python_version >= 3.8" | bc) -eq 1 ]]; then
            PYTHON_CMD="python"
            print_success "Python found: $(python --version)"
        else
            print_warning "Python $python_version is too old. Need 3.8+"
            install_python
        fi
    else
        install_python
    fi
    
    # Check for pip
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        install_pip
    else
        print_success "pip found: $($PYTHON_CMD -m pip --version | head -1)"
    fi
    
    # Install system dependencies
    read -p "Install system dependencies for liboqs? (recommended) [Y/n]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_system_deps
    fi
    
    # Download installer if not present
    if [ ! -f "install.py" ]; then
        print_info "Downloading installer..."
        if check_command curl; then
            curl -sSL https://raw.githubusercontent.com/Basty-devel/-Kyber1024-Quantum-Safe-Cryptography-Suite-v3.0/main/install.py -o install.py
        elif check_command wget; then
            wget -q https://raw.githubusercontent.com/Basty-devel/-Kyber1024-Quantum-Safe-Cryptography-Suite-v3.0/main/install.py
        else
            print_error "curl or wget not found. Please download install.py manually."
            exit 1
        fi
    fi
    
    # Make installer executable
    chmod +x install.py
    
    # Run the installer
    print_info "Running Kyber1024 installer..."
    echo -e "${CYAN}=====================================================${NC}"
    
    $PYTHON_CMD install.py --system-deps --test "$@"
    
    if [ $? -eq 0 ]; then
        echo -e "${CYAN}=====================================================${NC}"
        print_success "Installation completed successfully!"
        echo
        print_info "To activate the virtual environment and run:"
        echo "  source activate_venv.sh"
        echo "  python kyber1024.py"
        echo
        if [ -f "dist/kyber1024-suite" ] || [ -f "dist/Kyber1024-Suite" ]; then
            print_info "Or use the standalone executable:"
            find dist -type f -executable 2>/dev/null | head -1
        fi
    else
        echo -e "${CYAN}=====================================================${NC}"
        print_error "Installation failed. See errors above."
        exit 1
    fi
}

# Run main function
main "$@"