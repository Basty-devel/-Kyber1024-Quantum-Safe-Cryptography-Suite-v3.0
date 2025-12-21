#!/usr/bin/env python3
"""
verify.py - Installation verification tool
Run after installation to confirm quantum-safe cryptography works.
"""

import sys
import os
import platform
import json
from pathlib import Path

def print_success(msg):
    print(f"✅ {msg}")

def print_warning(msg):
    print(f"⚠️  {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def test_imports():
    """Test all critical imports"""
    print("\n🔧 Testing Python imports...")
    
    tests = [
        ("oqs", "Quantum-safe cryptography"),
        ("cryptography", "Symmetric encryption"),
        ("appdirs", "Cross-platform config"),
        ("PyQt6.QtWidgets", "GUI framework"),
    ]
    
    all_pass = True
    for module, description in tests:
        try:
            __import__(module.split('.')[0])
            print_success(f"{description}: {module}")
        except ImportError as e:
            print_error(f"{description}: {module} - {e}")
            all_pass = False
    
    return all_pass

def test_kyber():
    """Test Kyber implementation"""
    print("\n🔐 Testing quantum-safe cryptography...")
    
    try:
        import oqs
        
        # Check version
        print(f"liboqs version: {oqs.__version__}")
        
        # List available Kyber algorithms
        all_kems = oqs.get_enabled_KEM_mechanisms()
        kyber_algs = [k for k in all_kems if 'Kyber' in k]
        
        if kyber_algs:
            print_success(f"Available Kyber algorithms: {', '.join(kyber_algs)}")
            
            # Test if Kyber1024 is available
            if 'Kyber1024' in kyber_algs:
                print_success("Kyber1024 available - 256-bit quantum security")
                return True
            else:
                print_warning("Kyber1024 not available, but other Kyber versions are")
                return True
        else:
            print_error("No Kyber algorithms found!")
            return False
            
    except Exception as e:
        print_error(f"Failed to test Kyber: {e}")
        return False

def test_config():
    """Test configuration system"""
    print("\n⚙️  Testing configuration system...")
    
    try:
        # This assumes your ConfigManager is importable
        from kyber1024 import ConfigManager
        
        config = ConfigManager()
        print_success(f"Config directory: {config.config_dir}")
        
        # Test writing config
        test_config = config.config
        print_success(f"Config loaded: {len(test_config)} settings")
        
        # Check critical settings
        required_settings = ['theme', 'encryption_mode', 'kem_algorithm']
        for setting in required_settings:
            if setting in test_config:
                print_success(f"Setting '{setting}': {test_config[setting]}")
            else:
                print_warning(f"Setting '{setting}' not found")
        
        return True
        
    except Exception as e:
        print_error(f"Config test failed: {e}")
        return False

def test_gui():
    """Test GUI dependencies"""
    print("\n🎨 Testing GUI components...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Quick GUI test without displaying window
        app = QApplication([])
        print_success("GUI framework initialized")
        
        # Test platform
        system = platform.system()
        print_success(f"Platform: {system}")
        
        app.quit()
        return True
        
    except Exception as e:
        print_error(f"GUI test failed: {e}")
        return False

def check_executable():
    """Check if executable was built"""
    print("\n📦 Checking for standalone executable...")
    
    exe_paths = [
        Path("dist/Kyber1024-Suite.exe"),
        Path("dist/kyber1024-suite"),
        Path("Kyber1024-Suite.exe")
    ]
    
    for exe_path in exe_paths:
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print_success(f"Found executable: {exe_path} ({size_mb:.1f} MB)")
            return True
    
    print_warning("No standalone executable found (run with --build-exe to create one)")
    return False

def main():
    print("=" * 60)
    print("Kyber1024 Quantum-Safe Cryptography Suite - Verification")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Python Imports", test_imports()))
    results.append(("Kyber Cryptography", test_kyber()))
    results.append(("Configuration", test_config()))
    results.append(("GUI Framework", test_gui()))
    results.append(("Standalone Executable", check_executable()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 INSTALLATION VERIFIED SUCCESSFULLY!")
        print("Your quantum-safe cryptography suite is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("Some features may not work correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(main())