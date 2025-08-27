#!/usr/bin/env python3
"""
Comprehensive Mac Installer Builder for LLM PDF Reader
Handles building, packaging, and creating installers in a single script
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

class MacInstallerBuilder:
    def __init__(self):
        self.app_name = "LLM PDF Reader"
        self.app_bundle = f"{self.app_name}.app"
        self.dmg_name = "LLM-PDF-Reader-Installer.dmg"
        self.zip_name = "LLM-PDF-Reader-Installer.zip"
        self.pkg_name = "LLM-PDF-Reader-Installer.pkg"
        
    def print_banner(self):
        """Print a nice banner"""
        print("=" * 60)
        print("🚀 LLM PDF Reader - Mac Installer Builder")
        print("=" * 60)
        
    def check_prerequisites(self):
        """Check if all required tools are available"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 11):
            print("❌ Python 3.11+ required")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check if we're on macOS
        if sys.platform != "darwin":
            print("❌ This script is for macOS only")
            return False
        print("✅ macOS detected")
        
        # Check for create-dmg
        try:
            subprocess.run(["create-dmg", "--version"], capture_output=True, check=True)
            print("✅ create-dmg is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  create-dmg not found. Install with: brew install create-dmg")
            print("   DMG creation will be skipped")
        
        return True
    
    def install_dependencies(self):
        """Install and fix dependencies"""
        print("\n📦 Installing and fixing dependencies...")
        
        # Downgrade NumPy to avoid compatibility issues
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
        
        # Install all required packages
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
    
    def clean_build_dirs(self):
        """Clean previous build artifacts"""
        print("\n🧹 Cleaning previous build artifacts...")
        
        dirs_to_clean = ["build", "dist", "__pycache__"]
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                print(f"   Removing {dir_name}...")
                shutil.rmtree(dir_name)
        
        # Clean .spec files
        for spec_file in Path(".").glob("*.spec"):
            spec_file.unlink()
            print(f"   Removed {spec_file}")
        
        print("✅ Build directories cleaned")
    
    def create_spec_file(self):
        """Create a comprehensive .spec file"""
        print("\n📝 Creating PyInstaller spec file...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

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
    hooksconfig={{}},
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
    name='{self.app_name}',
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
    name='{self.app_name}',
)

app = BUNDLE(
    coll,
    name='{self.app_bundle}',
    icon='assets/icon.icns',
    bundle_identifier='com.llmpdfreader.app',
    info_plist={{
        'CFBundleName': '{self.app_name}',
        'CFBundleDisplayName': '{self.app_name}',
        'CFBundleVersion': '2.1.0',
        'CFBundleShortVersionString': '2.1.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
    }},
)
'''
        
        with open(f"{self.app_name}.spec", "w") as f:
            f.write(spec_content)
        
        print("✅ Spec file created")
    
    def build_app(self):
        """Build the application using PyInstaller"""
        print(f"\n🔨 Building {self.app_name}...")
        
        try:
            # Build using the spec file
            subprocess.run([
                sys.executable, "-m", "PyInstaller", 
                f"{self.app_name}.spec",
                "--clean"
            ], check=True)
            
            if os.path.exists(f"dist/{self.app_bundle}"):
                print(f"✅ {self.app_name} built successfully")
                return True
            else:
                print(f"❌ {self.app_name} not found in dist/")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def remove_quarantine(self):
        """Remove quarantine attributes from the app"""
        print("\n🛡️ Removing quarantine attributes...")
        
        app_path = f"dist/{self.app_bundle}"
        if os.path.exists(app_path):
            subprocess.run(["xattr", "-cr", app_path], check=False)
            print("✅ Quarantine attributes removed")
        else:
            print("⚠️  App not found, skipping quarantine removal")
    
    def create_dmg(self):
        """Create a DMG installer"""
        print(f"\n📦 Creating DMG installer: {self.dmg_name}")
        
        app_path = f"dist/{self.app_bundle}"
        if not os.path.exists(app_path):
            print("❌ App not found. Please build the app first.")
            return False
        
        # Check if create-dmg is available
        try:
            subprocess.run(["create-dmg", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ create-dmg not found. Install with: brew install create-dmg")
            return False
        
        # Create DMG
        cmd = [
            "create-dmg",
            "--volname", self.app_name,
            "--window-pos", "200", "120",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--icon", self.app_bundle, "175", "120",
            "--hide-extension", self.app_bundle,
            "--app-drop-link", "425", "120",
            "--no-internet-enable",
            self.dmg_name,
            "dist/"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ DMG created: {self.dmg_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ DMG creation failed: {e}")
            return False
    
    def create_zip(self):
        """Create a ZIP installer"""
        print(f"\n📦 Creating ZIP installer: {self.zip_name}")
        
        app_path = f"dist/{self.app_bundle}"
        if not os.path.exists(app_path):
            print("❌ App not found. Please build the app first.")
            return False
        
        try:
            # Remove existing ZIP
            if os.path.exists(self.zip_name):
                os.remove(self.zip_name)
            
            # Create ZIP
            subprocess.run([
                "zip", "-r", self.zip_name, self.app_bundle
            ], cwd="dist", check=True)
            
            print(f"✅ ZIP created: {self.zip_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ ZIP creation failed: {e}")
            return False
    
    def create_pkg(self):
        """Create a PKG installer"""
        print(f"\n📦 Creating PKG installer: {self.pkg_name}")
        
        app_path = f"dist/{self.app_bundle}"
        if not os.path.exists(app_path):
            print("❌ App not found. Please build the app first.")
            return False
        
        # Create temporary directory for packaging
        pkg_dir = "pkg_temp"
        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)
        os.makedirs(pkg_dir)
        
        try:
            # Copy app to temp directory
            shutil.copytree(app_path, f"{pkg_dir}/{self.app_bundle}")
            
            # Create component package
            component_pkg = "LLM-PDF-Reader-Component.pkg"
            cmd = [
                "pkgbuild",
                "--root", pkg_dir,
                "--component-plist", "installer/component.plist",
                "--install-location", "/Applications",
                component_pkg
            ]
            
            subprocess.run(cmd, check=True)
            
            # Create distribution package
            cmd = [
                "productbuild",
                "--distribution", "installer/distribution.xml",
                "--package-path", ".",
                self.pkg_name
            ]
            
            subprocess.run(cmd, check=True)
            
            # Clean up
            shutil.rmtree(pkg_dir)
            os.remove(component_pkg)
            
            print(f"✅ PKG created: {self.pkg_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ PKG creation failed: {e}")
            # Clean up on failure
            if os.path.exists(pkg_dir):
                shutil.rmtree(pkg_dir)
            if os.path.exists("LLM-PDF-Reader-Component.pkg"):
                os.remove("LLM-PDF-Reader-Component.pkg")
            return False
    
    def show_file_sizes(self):
        """Show the sizes of created files"""
        print("\n📊 File sizes:")
        
        files_to_check = [
            (f"dist/{self.app_bundle}", "App Bundle"),
            (self.dmg_name, "DMG Installer"),
            (self.zip_name, "ZIP Installer"),
            (self.pkg_name, "PKG Installer")
        ]
        
        for file_path, description in files_to_check:
            if os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                print(f"   {description}: {size_mb:.1f} MB")
            else:
                print(f"   {description}: Not created")
    
    def run(self, create_dmg=True, create_zip=True, create_pkg=False):
        """Run the complete build process"""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Install dependencies
        self.install_dependencies()
        
        # Clean build directories
        self.clean_build_dirs()
        
        # Create spec file
        self.create_spec_file()
        
        # Build the app
        if not self.build_app():
            return False
        
        # Remove quarantine attributes
        self.remove_quarantine()
        
        # Create installers
        success = True
        
        if create_dmg:
            if not self.create_dmg():
                success = False
        
        if create_zip:
            if not self.create_zip():
                success = False
        
        if create_pkg:
            if not self.create_pkg():
                success = False
        
        # Show results
        self.show_file_sizes()
        
        if success:
            print("\n🎉 Build completed successfully!")
            print(f"📱 App bundle: dist/{self.app_bundle}")
            if create_dmg and os.path.exists(self.dmg_name):
                print(f"💾 DMG installer: {self.dmg_name}")
            if create_zip and os.path.exists(self.zip_name):
                print(f"📦 ZIP installer: {self.zip_name}")
            if create_pkg and os.path.exists(self.pkg_name):
                print(f"📋 PKG installer: {self.pkg_name}")
        else:
            print("\n⚠️  Build completed with some errors")
        
        return success

def main():
    parser = argparse.ArgumentParser(description="Build LLM PDF Reader for macOS")
    parser.add_argument("--no-dmg", action="store_true", help="Skip DMG creation")
    parser.add_argument("--no-zip", action="store_true", help="Skip ZIP creation")
    parser.add_argument("--pkg", action="store_true", help="Create PKG installer")
    parser.add_argument("--clean", action="store_true", help="Clean build directories only")
    
    args = parser.parse_args()
    
    builder = MacInstallerBuilder()
    
    if args.clean:
        builder.clean_build_dirs()
        return
    
    # Run the build process
    builder.run(
        create_dmg=not args.no_dmg,
        create_zip=not args.no_zip,
        create_pkg=args.pkg
    )

if __name__ == "__main__":
    main()
