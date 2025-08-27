#!/usr/bin/env python3
"""
Simplified Mac app builder that addresses NumPy compatibility issues
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

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

def create_minimal_spec():
    """Create a minimal spec file that excludes problematic packages"""
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
        'fitz',
        'PIL',
        'PIL.Image',
        'requests',
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
        'rapidfuzz',
        'fasttext',
        'pdfplumber'
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
    icon='assets/llm_icon.icns' if os.path.exists('assets/llm_icon.icns') else None,
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
    
    with open("LLM_PDF_Reader_Minimal.spec", "w") as f:
        f.write(spec_content)
    
    print("📝 Created minimal .spec file")

def build_app():
    """Build the application using the minimal spec"""
    print("🚀 Building Mac application (minimal)...")
    
    # Create minimal spec file
    create_minimal_spec()
    
    # Build using the spec file
    cmd = ["pyinstaller", "LLM_PDF_Reader_Minimal.spec"]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Mac application built successfully!")
        print(f"📱 App location: {os.path.abspath('dist/LLM PDF Reader.app')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_installer():
    """Create a simple installer script"""
    installer_content = '''#!/bin/bash
# LLM PDF Reader Installer for Mac

echo "Installing LLM PDF Reader..."

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

echo "✅ LLM PDF Reader installed successfully!"
echo "You can now find it in your Applications folder."
'''
    
    with open("install_llm_pdf_reader.sh", "w") as f:
        f.write(installer_content)
    
    os.chmod("install_llm_pdf_reader.sh", 0o755)
    print("📦 Created installer script: install_llm_pdf_reader.sh")

def main():
    """Main build process"""
    print("🍎 LLM PDF Reader Mac App Builder (Minimal)")
    print("=" * 45)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build the application
    if build_app():
        print("\n🎉 Build completed successfully!")
        
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
