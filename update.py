#!/usr/bin/env python3
"""
update.py - Update Kyber1024 Suite to latest version
"""

import subprocess
import sys
import os
from pathlib import Path

def update_from_git():
    """Update from git repository"""
    print("Updating from Git...")
    
    # Check if we're in a git repo
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Not a git repository.")
        return False
    
    # Pull latest changes
    print("Pulling latest changes...")
    result = subprocess.run(["git", "pull"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Git update successful")
        
        # Update dependencies
        print("Updating dependencies...")
        if Path("requirements.txt").exists():
            pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"]
        else:
            pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "PyQt6", "cryptography", "liboqs-python", "appdirs"]
        
        subprocess.run(pip_cmd)
        return True
    else:
        print("✗ Git update failed")
        return False

def update_from_google_drive():
    """Update executable from Google Drive"""
    print("Updating executable from Google Drive...")
    
    # This would download the latest executable
    # Implementation depends on your distribution method
    print("Please download the latest version from:")
    print("https://drive.google.com/file/d/17ZKDp2sPPV7zmGDpFsWHtVzUA7fczhCJ/view")
    return False

def rebuild_executable():
    """Rebuild the executable"""
    response = input("\nRebuild executable? (y/N): ")
    if response.lower() == 'y':
        print("Rebuilding executable...")
        
        # Check if install.py has build capability
        if Path("install.py").exists():
            subprocess.run([sys.executable, "install.py", "--build-exe"])
        else:
            print("install.py not found for building")
    
    return True

def main():
    print("🔄 Kyber1024 Suite Updater")
    print("=" * 50)
    
    print("\nChoose update method:")
    print("1. Update from Git (source code)")
    print("2. Download latest executable")
    print("3. Check for updates")
    print("4. Exit")
    
    choice = input("\nChoice [1-4]: ")
    
    if choice == "1":
        success = update_from_git()
        if success:
            rebuild_executable()
    elif choice == "2":
        update_from_google_drive()
    elif choice == "3":
        print("\nCurrent version: 3.0")
        print("Latest version: Check GitHub for updates")
        print("https://github.com/Basty-devel/-Kyber1024-Quantum-Safe-Cryptography-Suite-v3.0")
    else:
        print("Update cancelled.")
        return
    
    print("\n✅ Update process complete!")

if __name__ == "__main__":
    main()