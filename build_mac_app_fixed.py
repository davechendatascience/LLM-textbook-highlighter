#!/usr/bin/env python3
"""
Improved build script for creating a standalone Mac application
Addresses NumPy compatibility issues and missing dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Install and fix dependencies"""
    print("📦 Installing and fixing dependencies...")
    
    # First, downgrade NumPy to avoid compatibility issues
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "numpy<2.0.0"], check=True)
        print("✅ NumPy downgraded to avoid compatibility issues")
    except subprocess.CalledProcessError:
        print("⚠️  NumPy downgrade failed, continuing...")
    
    # Install PyInstaller if not already installed
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed successfully")
    
    # Ensure all required packages are installed
    required_packages = [
        "PySide6>=6.5.0",
        "PyMuPDF==1.23.8", 
        "Pillow==10.0.1",
        "requests==2.31.0",
        "numpy<2.0.0",
        "pdfplumber",
        "fasttext-wheel"
    ]
    
    for package in required_packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed/updated")
        except subprocess.CalledProcessError:
            print(f"⚠️  Failed to install {package}")

def clean_build_dirs():
    """Clean previous build artifacts"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 Removed {spec_file}")

def create_spec_file():
    """Create a custom .spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_reader.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        'fitz',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageEnhance',
        'requests',
        'numpy',
        'pdfplumber',
        'fasttext',
        'fasttext.util',
        'llm',
        'config',
        'utils'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'pyarrow',
        'rapidfuzz'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LLM PDF Reader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LLM PDF Reader',
)

app = BUNDLE(
    coll,
    name='LLM PDF Reader.app',
    icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
    bundle_identifier='com.llm.pdfreader',
    info_plist={
        'CFBundleName': 'LLM PDF Reader',
        'CFBundleDisplayName': 'LLM PDF Reader',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
    },
)
'''
    
    with open("LLM_PDF_Reader.spec", "w") as f:
        f.write(spec_content)
    
    print("📝 Created custom .spec file")

def build_mac_app():
    """Build the Mac application using the custom spec file"""
    print("🚀 Building Mac application...")
    
    # Create custom spec file
    create_spec_file()
    
    # Build using the spec file
    cmd = ["pyinstaller", "LLM_PDF_Reader.spec"]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Mac application built successfully!")
        print(f"📱 App location: {os.path.abspath('dist/LLM PDF Reader.app')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def test_app():
    """Test the built application"""
    app_path = "dist/LLM PDF Reader.app"
    if os.path.exists(app_path):
        print("🧪 Testing built application...")
        try:
            # Test if the app can be launched
            result = subprocess.run(["open", app_path], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Application launched successfully!")
            else:
                print("⚠️  Application launch test inconclusive")
        except Exception as e:
            print(f"⚠️  Could not test application: {e}")
    else:
        print("❌ Application not found for testing")

def create_installer():
    """Create an improved installer script"""
    installer_content = '''#!/bin/bash
# LLM PDF Reader Installer for Mac

set -e

echo "Installing LLM PDF Reader..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this installer as root"
    exit 1
fi

# Check if app exists
if [ ! -d "LLM PDF Reader.app" ]; then
    echo "❌ LLM PDF Reader.app not found in current directory"
    exit 1
fi

# Remove existing installation if present
if [ -d "/Applications/LLM PDF Reader.app" ]; then
    echo "Removing existing installation..."
    rm -rf "/Applications/LLM PDF Reader.app"
fi

# Copy app to Applications
echo "Copying application to /Applications..."
cp -R "LLM PDF Reader.app" "/Applications/"

# Set proper permissions
echo "Setting permissions..."
chmod +x "/Applications/LLM PDF Reader.app/Contents/MacOS/LLM PDF Reader"

# Create desktop shortcut (optional)
read -p "Create desktop shortcut? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ln -sf "/Applications/LLM PDF Reader.app" ~/Desktop/
    echo "✅ Desktop shortcut created"
fi

echo "✅ LLM PDF Reader installed successfully!"
echo "You can now find it in your Applications folder."
echo "First launch may take a moment as macOS verifies the application."
'''
    
    with open("install_llm_pdf_reader.sh", "w") as f:
        f.write(installer_content)
    
    os.chmod("install_llm_pdf_reader.sh", 0o755)
    print("📦 Created improved installer script: install_llm_pdf_reader.sh")

def main():
    """Main build process"""
    print("🍎 LLM PDF Reader Mac App Builder (Fixed)")
    print("=" * 50)
    
    # Install and fix dependencies
    install_dependencies()
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build the application
    if build_mac_app():
        print("\n🎉 Build completed successfully!")
        
        # Test the application
        test_app()
        
        # Create installer
        create_installer()
        
        print("\n📋 Next steps:")
        print("1. Test the application: open 'dist/LLM PDF Reader.app'")
        print("2. Run installer: ./install_llm_pdf_reader.sh")
        print("3. Distribute the app bundle")
        
        # Show file sizes
        app_path = "dist/LLM PDF Reader.app"
        if os.path.exists(app_path):
            size = subprocess.run(["du", "-sh", app_path], capture_output=True, text=True)
            print(f"📊 App bundle size: {size.stdout.strip()}")
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
