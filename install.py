#!/usr/bin/env python3
"""
Kyber1024 Quantum-Safe Cryptography Suite - Installation Script
Cross-platform installer for Windows, Linux, and macOS
Version: 3.0
"""

import sys
import os
import platform
import subprocess
import venv
import argparse
import shutil
import stat
import tempfile
import textwrap
from pathlib import Path
from typing import List, Tuple, Dict, Optional

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Installer:
    """Cross-platform installer for Kyber1024 Cryptography Suite"""
    
    def __init__(self, args):
        self.args = args
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.is_macos = self.system == "Darwin"
        self.script_dir = Path(__file__).parent.absolute()
        self.project_root = self.script_dir
        
        # Platform-specific paths
        if self.is_windows:
            self.venv_path = self.project_root / "venv"
            self.pip_cmd = str(self.venv_path / "Scripts" / "pip.exe")
            self.python_cmd = str(self.venv_path / "Scripts" / "python.exe")
            self.activate_cmd = str(self.venv_path / "Scripts" / "activate.bat")
        else:
            self.venv_path = self.project_root / "venv"
            self.pip_cmd = str(self.venv_path / "bin" / "pip")
            self.python_cmd = str(self.venv_path / "bin" / "python")
            self.activate_cmd = f"source {self.venv_path / 'bin' / 'activate'}"
        
        # Platform-specific requirements
        self.platform_requirements = {
            "Windows": ["pywin32>=306"],
            "Linux": [],
            "Darwin": []
        }
        
        # Common requirements
        self.base_requirements = [
            "PyQt6>=6.5.0",
            "cryptography>=42.0.0",
            "liboqs-python>=0.8.0",
            "appdirs>=1.4.4"
        ]
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   check: bool = True, capture: bool = False) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            if cwd is None:
                cwd = self.project_root
            
            if capture:
                result = subprocess.run(
                    cmd, cwd=cwd, check=check,
                    capture_output=True, text=True, shell=self.is_windows
                )
                return True, result.stdout
            else:
                result = subprocess.run(
                    cmd, cwd=cwd, check=check,
                    text=True, shell=self.is_windows
                )
                return True, ""
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if capture else str(e)
            return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible (>= 3.8)"""
        self.print_header("Checking Python Version")
        
        major, minor = sys.version_info[:2]
        required = (3, 8)
        
        print(f"Detected Python: {sys.version.split()[0]}")
        print(f"Required: Python {required[0]}.{required[1]}+")
        
        if (major, minor) >= required:
            self.print_success(f"Python {major}.{minor} is compatible")
            return True
        else:
            self.print_error(f"Python {major}.{minor} is too old. Need 3.8+")
            
            # Platform-specific installation instructions
            if self.is_windows:
                print("\nTo install Python 3.8+ on Windows:")
                print("1. Download from https://python.org/downloads/")
                print("2. Run installer with 'Add Python to PATH' checked")
            elif self.is_linux:
                print("\nTo install Python 3.8+ on Ubuntu/Debian:")
                print("  sudo apt update && sudo apt install python3 python3-pip python3-venv")
            elif self.is_macos:
                print("\nTo install Python 3.8+ on macOS:")
                print("  brew install python@3.10")
            
            return False
    
    def check_system_dependencies(self) -> bool:
        """Check and install system-level dependencies"""
        self.print_header("Checking System Dependencies")
        
        # Linux-specific dependencies
        if self.is_linux:
            print("Checking for Linux system packages...")
            
            # Common build dependencies for liboqs
            linux_packages = [
                "build-essential", "cmake", "ninja-build", 
                "gcc", "g++", "python3-dev", "libssl-dev"
            ]
            
            # Check if apt is available (Debian/Ubuntu)
            apt_check, _ = self.run_command(["which", "apt-get"], check=False)
            
            if apt_check:
                print("Detected apt-based system (Debian/Ubuntu)")
                
                # Update package list
                self.run_command(["sudo", "apt", "update"], check=False)
                
                # Install missing packages
                for pkg in linux_packages:
                    check_cmd = ["dpkg", "-s", pkg]
                    installed, _ = self.run_command(check_cmd, check=False)
                    
                    if not installed:
                        print(f"Installing {pkg}...")
                        success, _ = self.run_command(
                            ["sudo", "apt", "install", "-y", pkg], check=False
                        )
                        if success:
                            self.print_success(f"Installed {pkg}")
                        else:
                            self.print_warning(f"Failed to install {pkg}")
                    else:
                        self.print_success(f"{pkg} already installed")
        
        # macOS-specific dependencies
        elif self.is_macos:
            print("Checking for macOS system dependencies...")
            
            # Check if Homebrew is installed
            brew_check, _ = self.run_command(["which", "brew"], check=False)
            
            if brew_check:
                print("Homebrew detected, checking for packages...")
                
                # Packages needed for liboqs
                mac_packages = ["cmake", "ninja"]
                
                for pkg in mac_packages:
                    check_cmd = ["brew", "list", pkg]
                    installed, _ = self.run_command(check_cmd, check=False)
                    
                    if not installed:
                        print(f"Installing {pkg} via Homebrew...")
                        success, _ = self.run_command(
                            ["brew", "install", pkg], check=False
                        )
                        if success:
                            self.print_success(f"Installed {pkg}")
                        else:
                            self.print_warning(f"Failed to install {pkg}")
                    else:
                        self.print_success(f"{pkg} already installed")
            else:
                self.print_warning("Homebrew not found. Some dependencies may need manual installation.")
        
        self.print_success("System dependency check complete")
        return True
    
    def create_virtual_environment(self) -> bool:
        """Create a Python virtual environment"""
        self.print_header("Creating Virtual Environment")
        
        if self.venv_path.exists():
            print(f"Virtual environment already exists at: {self.venv_path}")
            
            if self.args.force:
                print("Force flag set, removing existing venv...")
                shutil.rmtree(self.venv_path)
            else:
                print("Using existing virtual environment")
                return True
        
        print(f"Creating virtual environment at: {self.venv_path}")
        
        try:
            # Create venv with system site packages disabled
            builder = venv.EnvBuilder(
                system_site_packages=False,
                clear=True,
                symlinks=not self.is_windows,
                with_pip=True
            )
            builder.create(str(self.venv_path))
            
            self.print_success("Virtual environment created successfully")
            
            # Create activation instructions file
            self.create_activation_instructions()
            
            return True
        except Exception as e:
            self.print_error(f"Failed to create virtual environment: {e}")
            return False
    
    def create_activation_instructions(self):
        """Create platform-specific activation instructions"""
        instructions = []
        
        if self.is_windows:
            instructions = [
                f"cd /d \"{self.project_root}\"",
                f"{self.activate_cmd}",
                "REM To run the application:",
                f"{self.python_cmd} kyber1024.py"
            ]
        else:
            instructions = [
                f"cd \"{self.project_root}\"",
                self.activate_cmd,
                "# To run the application:",
                f"{self.python_cmd} kyber1024.py"
            ]
        
        # Create activation script
        if self.is_windows:
            script_path = self.project_root / "activate_venv.bat"
            content = "@echo off\n" + "\n".join(instructions)
        else:
            script_path = self.project_root / "activate_venv.sh"
            content = "#!/bin/bash\n" + "\n".join(instructions)
            # Make it executable
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        
        with open(script_path, "w") as f:
            f.write(content)
        
        self.print_success(f"Created activation script: {script_path.name}")
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies in virtual environment"""
        self.print_header("Installing Python Dependencies")
        
        # Upgrade pip first
        print("Upgrading pip...")
        success, output = self.run_command(
            [self.pip_cmd, "install", "--upgrade", "pip"],
            capture=True
        )
        
        if not success:
            self.print_warning(f"Failed to upgrade pip: {output}")
        
        # Build requirement list
        requirements = self.base_requirements.copy()
        
        # Add platform-specific requirements
        if self.system in self.platform_requirements:
            requirements.extend(self.platform_requirements[self.system])
        
        # Add PyInstaller if building executable
        if self.args.build_exe:
            requirements.append("pyinstaller>=6.16.0")
        
        # Install from requirements.txt if it exists
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            print(f"Installing from {req_file.name}...")
            success, output = self.run_command(
                [self.pip_cmd, "install", "-r", str(req_file)],
                capture=True
            )
            
            if success:
                self.print_success("Dependencies installed from requirements.txt")
            else:
                self.print_error(f"Failed to install from requirements.txt: {output}")
                return False
        else:
            # Install individual packages
            print("No requirements.txt found, installing packages individually...")
            
            for req in requirements:
                print(f"Installing {req}...")
                success, output = self.run_command(
                    [self.pip_cmd, "install", req],
                    capture=True
                )
                
                if success:
                    self.print_success(f"Installed {req}")
                else:
                    self.print_error(f"Failed to install {req}: {output}")
                    if not self.args.continue_on_error:
                        return False
        
        self.print_success("All dependencies installed successfully")
        return True
    
    def build_executable(self) -> bool:
        """Build standalone executable with PyInstaller"""
        if not self.args.build_exe:
            return True
        
        self.print_header("Building Standalone Executable")
        
        if not self.is_windows:
            self.print_warning("Executable building is optimized for Windows")
            self.print_warning("Building on Linux/macOS will create platform-specific binaries")
        
        # Check if we're in the virtual environment
        if not Path(self.python_cmd).exists():
            self.print_error("Virtual environment not found. Activate it first.")
            return False
        
        # Build command based on platform
        if self.is_windows:
            build_cmd = [
                self.python_cmd, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name", "Kyber1024-Suite",
                "--icon", str(self.project_root / "kybersec.ico"),
                "--add-data", f"{self.project_root / 'kybersec.png'};.",
                "--hidden-import", "oqs",
                "--hidden-import", "cryptography",
                "--hidden-import", "appdirs",
                "--hidden-import", "PyQt6.QtCore",
                "--hidden-import", "PyQt6.QtGui",
                "--hidden-import", "PyQt6.QtWidgets",
                "--clean",
                str(self.project_root / "kyber1024.py")
            ]
        else:
            # Generic build for Linux/macOS
            exe_name = "kyber1024-suite"
            if self.is_macos:
                exe_name = "Kyber1024-Suite"
            
            build_cmd = [
                self.python_cmd, "-m", "PyInstaller",
                "--onefile",
                "--name", exe_name,
                "--hidden-import", "oqs",
                "--hidden-import", "cryptography",
                "--hidden-import", "appdirs",
                "--hidden-import", "PyQt6.QtCore",
                "--hidden-import", "PyQt6.QtGui",
                "--hidden-import", "PyQt6.QtWidgets",
                "--clean",
                str(self.project_root / "kyber1024.py")
            ]
        
        print(f"Building with command: {' '.join(build_cmd[3:])}")
        
        success, output = self.run_command(build_cmd, capture=True)
        
        if success:
            exe_path = self.project_root / "dist"
            if exe_path.exists():
                executables = list(exe_path.glob("*"))
                if executables:
                    exe_file = executables[0]
                    size_mb = exe_file.stat().st_size / (1024 * 1024)
                    self.print_success(f"Executable built successfully!")
                    print(f"  Location: {exe_file}")
                    print(f"  Size: {size_mb:.1f} MB")
                    print(f"  Platform: {self.system}")
                    
                    # Make executable on Unix systems
                    if not self.is_windows:
                        exe_file.chmod(exe_file.stat().st_mode | stat.S_IEXEC)
                    
                    return True
        
        self.print_error(f"Build failed: {output}")
        return False
    
    def run_tests(self) -> bool:
        """Run verification tests"""
        self.print_header("Running Verification Tests")
        
        tests = [
            ("Python Version", self._test_python_version),
            ("Virtual Environment", self._test_venv),
            ("Critical Imports", self._test_imports),
            ("Quantum-Safe Libraries", self._test_quantum_libs),
            ("Configuration", self._test_configuration),
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            print(f"\nTesting: {test_name}...")
            passed, message = test_func()
            
            if passed:
                self.print_success(f"{test_name}: {message}")
            else:
                self.print_error(f"{test_name}: {message}")
                all_passed = False
        
        if all_passed:
            self.print_success("All tests passed!")
        else:
            self.print_warning("Some tests failed. Check the output above.")
        
        return all_passed
    
    def _test_python_version(self) -> Tuple[bool, str]:
        """Test Python version compatibility"""
        major, minor = sys.version_info[:2]
        if (major, minor) >= (3, 8):
            return True, f"Python {major}.{minor} OK"
        return False, f"Python {major}.{minor} - need 3.8+"
    
    def _test_venv(self) -> Tuple[bool, str]:
        """Test virtual environment"""
        if Path(self.python_cmd).exists():
            # Check if we're running in venv
            cmd = [self.python_cmd, "-c", "import sys; print(sys.prefix != sys.base_prefix)"]
            success, output = self.run_command(cmd, capture=True)
            
            if success and "True" in output.strip():
                return True, "Running in virtual environment"
        return False, "Not in virtual environment"
    
    def _test_imports(self) -> Tuple[bool, str]:
        """Test critical imports"""
        test_code = """
import sys
missing = []
modules = ['oqs', 'cryptography', 'appdirs', 'PyQt6.QtCore', 'PyQt6.QtWidgets']

for mod in modules:
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)

if missing:
    print(f"Missing: {missing}")
    sys.exit(1)
else:
    print("All imports OK")
        """
        
        success, output = self.run_command(
            [self.python_cmd, "-c", test_code],
            capture=True
        )
        
        if success:
            return True, "All critical imports available"
        return False, output.strip()
    
    def _test_quantum_libs(self) -> Tuple[bool, str]:
        """Test quantum-safe libraries"""
        test_code = """
try:
    import oqs
    print(f"liboqs v{oqs.__version__}")
    
    kyber_algs = [a for a in oqs.get_enabled_KEM_mechanisms() if 'Kyber' in a]
    if kyber_algs:
        print(f"Kyber algorithms: {kyber_algs}")
        if 'Kyber1024' in kyber_algs:
            print("Kyber1024: AVAILABLE")
        else:
            print("Kyber1024: NOT AVAILABLE")
    else:
        print("No Kyber algorithms found")
    
except Exception as e:
    print(f"Error: {e}")
        """
        
        success, output = self.run_command(
            [self.python_cmd, "-c", test_code],
            capture=True
        )
        
        if success and "Kyber1024: AVAILABLE" in output:
            return True, "Quantum-safe libraries available"
        return False, output.strip()
    
    def _test_configuration(self) -> Tuple[bool, str]:
        """Test application configuration"""
        test_code = """
import tempfile
import json
from pathlib import Path

# Create a test config
test_config = {
    'test': 'success',
    'platform': 'test_platform'
}

# Write and read back
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(test_config, f)
    temp_path = f.name

try:
    with open(temp_path, 'r') as f:
        loaded = json.load(f)
    
    if loaded.get('test') == 'success':
        print("Configuration test: PASSED")
    else:
        print("Configuration test: FAILED")
        
finally:
    Path(temp_path).unlink(missing_ok=True)
        """
        
        success, output = self.run_command(
            [self.python_cmd, "-c", test_code],
            capture=True
        )
        
        if success and "PASSED" in output:
            return True, "Configuration system works"
        return False, "Configuration test failed"
    
    def print_summary(self):
        """Print installation summary"""
        self.print_header("Installation Summary")
        
        print(f"{Colors.BOLD}Platform:{Colors.ENDC} {self.system}")
        print(f"{Colors.BOLD}Project Directory:{Colors.ENDC} {self.project_root}")
        print(f"{Colors.BOLD}Virtual Environment:{Colors.ENDC} {self.venv_path}")
        
        if Path(self.python_cmd).exists():
            print(f"{Colors.BOLD}Python Executable:{Colors.ENDC} {self.python_cmd}")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        
        if self.is_windows:
            print("1. Activate the virtual environment:")
            print(f"   {self.activate_cmd}")
            print("2. Run the application:")
            print(f"   {self.python_cmd} kyber1024.py")
            
            if self.args.build_exe:
                exe_path = self.project_root / "dist" / "Kyber1024-Suite.exe"
                if exe_path.exists():
                    print(f"3. Or run the standalone executable:")
                    print(f"   {exe_path}")
        else:
            print("1. Activate the virtual environment:")
            print(f"   {self.activate_cmd}")
            print("2. Run the application:")
            print(f"   {self.python_cmd} kyber1024.py")
        
        print(f"\n{Colors.OKGREEN}Installation complete!{Colors.ENDC}")
    
    def run(self) -> bool:
        """Run the complete installation process"""
        print(f"{Colors.BOLD}Kyber1024 Quantum-Safe Cryptography Suite Installer{Colors.ENDC}")
        print(f"Platform: {self.system}")
        print(f"Version: 3.0")
        print()
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check system dependencies (non-blocking)
        if self.args.system_deps:
            self.check_system_dependencies()
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Build executable if requested
        if self.args.build_exe:
            if not self.build_executable():
                if not self.args.continue_on_error:
                    return False
        
        # Run tests if requested
        if self.args.test:
            if not self.run_tests():
                if not self.args.continue_on_error:
                    return False
        
        # Print summary
        self.print_summary()
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Install Kyber1024 Quantum-Safe Cryptography Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          # Basic installation
          python install.py
          
          # Install with system dependencies and build executable
          python install.py --system-deps --build-exe
          
          # Install with tests
          python install.py --test
          
          # Force reinstall (clean venv)
          python install.py --force
        """)
    )
    
    parser.add_argument(
        "--system-deps",
        action="store_true",
        help="Install system-level dependencies (requires sudo/brew)"
    )
    
    parser.add_argument(
        "--build-exe",
        action="store_true",
        help="Build standalone executable after installation"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run verification tests after installation"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreation of virtual environment"
    )
    
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue installation even if some steps fail"
    )
    
    parser.add_argument(
        "--venv-path",
        type=Path,
        default=None,
        help="Custom path for virtual environment"
    )
    
    args = parser.parse_args()
    
    try:
        installer = Installer(args)
        success = installer.run()
        
        if success:
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Installation cancelled by user{Colors.ENDC}")
        return 130
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())