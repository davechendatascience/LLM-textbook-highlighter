#!/usr/bin/env python3
"""
Build script for creating a standalone Mac application
Uses PyInstaller to package the PDF reader with all dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed successfully")

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

def build_mac_app():
    """Build the Mac application using PyInstaller"""
    print("🚀 Building Mac application...")
    
    # PyInstaller command with optimized settings for Mac
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable
        "--windowed",                   # No console window on Mac
        "--name=PDFReader",             # App name
        "--icon=assets/icon.icns",      # App icon (if available)
        "--add-data=src:src",           # Include source modules
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui", 
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=fitz",         # PyMuPDF
        "--hidden-import=PIL",          # Pillow
        "--hidden-import=requests",
        "--collect-all=PySide6",
        "--collect-all=fitz",
        "--collect-all=PIL",
        "run_reader.py"                 # Main entry point
    ]
    
    # Remove icon option if icon doesn't exist
    if not os.path.exists("assets/icon.icns"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        print("⚠️  No icon found, building without custom icon")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Mac application built successfully!")
        print(f"📱 App location: {os.path.abspath('dist/PDFReader')}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def create_app_bundle():
    """Create a proper .app bundle for Mac"""
    print("📦 Creating .app bundle...")
    
    app_name = "PDFReader.app"
    app_path = f"dist/{app_name}"
    
    # Create app bundle structure
    bundle_cmd = [
        "pyinstaller",
        "--onedir",                     # Directory-based bundle
        "--windowed",                   # No console window
        "--name=PDFReader",             # App name
        "--icon=assets/icon.icns",      # App icon (if available)
        "--add-data=src:src",           # Include source modules
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui", 
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=fitz",         # PyMuPDF
        "--hidden-import=PIL",          # Pillow
        "--hidden-import=requests",
        "--collect-all=PySide6",
        "--collect-all=fitz",
        "--collect-all=PIL",
        "run_reader.py"                 # Main entry point
    ]
    
    # Remove icon option if icon doesn't exist
    if not os.path.exists("assets/icon.icns"):
        bundle_cmd = [arg for arg in bundle_cmd if not arg.startswith("--icon")]
    
    try:
        subprocess.run(bundle_cmd, check=True)
        print("✅ .app bundle created successfully!")
        print(f"📱 App bundle location: {os.path.abspath(app_path)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Bundle creation failed: {e}")
        return False

def create_installer():
    """Create a simple installer script"""
    installer_content = '''#!/bin/bash
# PDF Reader Installer for Mac

echo "Installing PDF Reader..."

# Copy app to Applications
cp -R "PDFReader.app" "/Applications/"

# Set permissions
chmod +x "/Applications/PDFReader.app/Contents/MacOS/PDFReader"

echo "✅ PDF Reader installed successfully!"
echo "You can now find it in your Applications folder."
'''
    
    with open("install_pdf_reader.sh", "w") as f:
        f.write(installer_content)
    
    os.chmod("install_pdf_reader.sh", 0o755)
    print("📦 Created installer script: install_pdf_reader.sh")

def main():
    """Main build process"""
    print("🍎 PDF Reader Mac App Builder")
    print("=" * 40)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build options
    print("\nChoose build type:")
    print("1. Single executable (smaller, faster startup)")
    print("2. .app bundle (more Mac-like, easier to install)")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    success = True
    
    if choice in ["1", "3"]:
        success &= build_mac_app()
    
    if choice in ["2", "3"]:
        success &= create_app_bundle()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("\nNext steps:")
        print("1. Test the application: ./dist/PDFReader")
        print("2. Create installer: ./install_pdf_reader.sh")
        print("3. Distribute the app bundle or executable")
        
        # Create installer if .app bundle was built
        if choice in ["2", "3"] and os.path.exists("dist/PDFReader.app"):
            create_installer()
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main()
