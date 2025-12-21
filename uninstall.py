#!/usr/bin/env python3
"""
uninstall.py - Clean removal of Kyber1024 Suite
"""

import os
import sys
import shutil
from pathlib import Path

def get_config_dirs():
    """Get all configuration directories"""
    dirs = []
    
    # Platform-specific config directories
    if sys.platform == "win32":
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        if local_appdata:
            dirs.append(Path(local_appdata) / "KyberVault")
    else:
        # Unix-like systems
        dirs.append(Path.home() / ".kyber_vault")
        dirs.append(Path.home() / ".config" / "KyberCryptographySuite")
    
    # Current directory artifacts
    dirs.extend([
        Path("venv"),
        Path("dist"),
        Path("build"),
        Path("__pycache__"),
        Path("keys")
    ])
    
    return [d for d in dirs if d.exists()]

def main():
    print("🗑️  Kyber1024 Suite Uninstaller")
    print("=" * 50)
    
    # Find what to delete
    to_delete = get_config_dirs()
    
    if not to_delete:
        print("No Kyber1024 artifacts found to delete.")
        return
    
    print("The following will be deleted:")
    for item in to_delete:
        print(f"  - {item}")
    
    print("\n⚠️  WARNING: This will delete all your keys and configuration!")
    print("   Make sure you have backups if needed.")
    
    response = input("\nContinue? (type 'DELETE' to confirm): ")
    if response != "DELETE":
        print("Cancelled.")
        return
    
    # Delete items
    for item in to_delete:
        try:
            if item.is_file():
                item.unlink()
                print(f"Deleted file: {item}")
            else:
                shutil.rmtree(item)
                print(f"Deleted directory: {item}")
        except Exception as e:
            print(f"Failed to delete {item}: {e}")
    
    print("\n✅ Uninstall complete!")
    print("\nNote: Source files (kyber1024.py, etc.) were not deleted.")
    print("You can delete the entire folder manually if desired.")

if __name__ == "__main__":
    main()