#!/usr/bin/env python3
"""
run.py - Quick launcher for Kyber1024 Suite
Automatically sets up environment if needed.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_venv():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def setup_venv():
    """Set up virtual environment if needed"""
    print("Setting up virtual environment...")
    
    venv_dir = Path("venv")
    
    # Create venv
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip = venv_dir / "Scripts" / "pip.exe"
        python = venv_dir / "Scripts" / "python.exe"
    else:  # Unix
        pip = venv_dir / "bin" / "pip"
        python = venv_dir / "bin" / "python"
    
    # Install requirements
    requirements = ["PyQt6", "cryptography", "liboqs-python", "appdirs"]
    for req in requirements:
        subprocess.run([str(pip), "install", req])
    
    return str(python)

def main():
    print("🚀 Kyber1024 Quantum-Safe Cryptography Suite - Quick Launcher")
    print("=" * 60)
    
    # Check if we're in venv
    if not check_venv():
        print("Virtual environment not detected.")
        
        # Check if venv already exists
        venv_dir = Path("venv")
        if venv_dir.exists():
            print("Found existing virtual environment.")
            if os.name == 'nt':
                python = venv_dir / "Scripts" / "python.exe"
            else:
                python = venv_dir / "bin" / "python"
            
            if python.exists():
                print(f"Using: {python}")
            else:
                print("Creating new virtual environment...")
                python = setup_venv()
        else:
            response = input("Create virtual environment? (Y/n): ")
            if response.lower() in ['y', 'yes', '']:
                python = setup_venv()
            else:
                print("Running without virtual environment...")
                python = sys.executable
    else:
        print("Running in virtual environment.")
        python = sys.executable
    
    # Run the application
    print(f"\nStarting Kyber1024 Suite with: {python}")
    print("=" * 60)
    
    subprocess.run([python, "kyber1024.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLaunch cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)