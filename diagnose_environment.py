#!/usr/bin/env python3
"""
AIRISS v4.1 Environment Diagnostic Script
Checks Python environment and package compatibility
"""

import sys
import subprocess
import pkg_resources
from pathlib import Path

def check_python_version():
    print("=" * 50)
    print("PYTHON VERSION CHECK")
    print("=" * 50)
    print(f"Current Python: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if Python 3.11 is available
    try:
        result = subprocess.run(['py', '-3.11', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Python 3.11 available: {result.stdout.strip()}")
        else:
            print("Python 3.11 NOT available")
    except:
        print("Python launcher 'py' not available")

def check_virtual_env():
    print("\n" + "=" * 50)
    print("VIRTUAL ENVIRONMENT CHECK")
    print("=" * 50)
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    print(f"In virtual environment: {in_venv}")
    
    if in_venv:
        print(f"Virtual env path: {sys.prefix}")
    
    # Check for venv folders
    venv_folders = ['venv', 'venv_new', 'venv_stable', 'venv_backup']
    for folder in venv_folders:
        if Path(folder).exists():
            print(f"Found folder: {folder}")

def check_packages():
    print("\n" + "=" * 50)
    print("PACKAGE CHECK")
    print("=" * 50)
    
    required_packages = [
        'fastapi==0.104.1',
        'uvicorn==0.24.0', 
        'sqlalchemy==2.0.23',
        'pandas==2.1.3',
        'pydantic==2.5.0'
    ]
    
    for package_spec in required_packages:
        package_name = package_spec.split('==')[0]
        try:
            package = pkg_resources.get_distribution(package_name)
            print(f"✅ {package_name}: {package.version}")
        except pkg_resources.DistributionNotFound:
            print(f"❌ {package_name}: NOT INSTALLED")

def check_rust():
    print("\n" + "=" * 50)
    print("RUST COMPILER CHECK")
    print("=" * 50)
    
    try:
        result = subprocess.run(['cargo', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Rust/Cargo available: {result.stdout.strip()}")
        else:
            print("❌ Rust/Cargo not available")
    except:
        print("❌ Rust/Cargo not found in PATH")

def check_airiss_files():
    print("\n" + "=" * 50)
    print("AIRISS PROJECT FILES CHECK")
    print("=" * 50)
    
    required_files = [
        'app/main.py',
        'requirements.txt',
        'app/templates/index.html',
        'init_database.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")

def main():
    print("AIRISS v4.1 Environment Diagnostic")
    print("Generated on:", subprocess.run(['date', '/t'], 
                                         capture_output=True, text=True).stdout.strip())
    
    check_python_version()
    check_virtual_env()
    check_packages()
    check_rust()
    check_airiss_files()
    
    print("\n" + "=" * 50)
    print("RECOMMENDATION")
    print("=" * 50)
    
    if sys.version_info >= (3, 13):
        print("🔄 Use Python 3.11 instead of 3.13+ for better compatibility")
    
    print("\n🚀 Next steps:")
    print("1. If Python 3.11 not available: install it")
    print("2. Run: quick_fix.bat")
    print("3. Or manually copy commands from: manual_commands.txt")

if __name__ == "__main__":
    main()
