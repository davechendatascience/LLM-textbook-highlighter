#!/usr/bin/env python3
"""
Windows Installer Builder for LLM Textbook Highlighter
Handles complete installation including Pandoc and all dependencies
"""

import os
import sys
import subprocess
import shutil
import zipfile
import urllib.request
import tempfile
from pathlib import Path
import json

class WindowsInstallerBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.installer_name = "LLM_Textbook_Highlighter_Setup"
        
    def clean_build_dirs(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning build directories...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        print("✅ Build directories cleaned")
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("✅ Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def download_pandoc(self):
        """Download Pandoc for Windows"""
        print("📥 Downloading Pandoc for Windows...")
        
        # Get latest Pandoc version
        pandoc_url = "https://github.com/jgm/pandoc/releases/download/3.1.9/pandoc-3.1.9-windows-x86_64.zip"
        pandoc_dir = self.build_dir / "pandoc"
        pandoc_dir.mkdir(exist_ok=True)
        
        try:
            # Download Pandoc
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            urllib.request.urlretrieve(pandoc_url, temp_file.name)
            
            # Extract Pandoc
            with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                zip_ref.extractall(pandoc_dir)
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            print("✅ Pandoc downloaded and extracted")
            return True
        except Exception as e:
            print(f"❌ Failed to download Pandoc: {e}")
            return False
    
    def create_installer_script(self):
        """Create NSIS installer script"""
        print("📝 Creating NSIS installer script...")
        
        nsis_script = f"""
# NSIS Installer Script for LLM Textbook Highlighter

!define APP_NAME "LLM Textbook Highlighter"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "LLM Textbook Highlighter Team"
!define APP_EXE "run_reader.py"

!include "MUI2.nsh"

Name "${{APP_NAME}}"
OutFile "${{OUTDIR}}\\{self.installer_name}.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""

RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_UNICON "assets\\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    # Copy application files
    File /r "src\\"
    File "run_reader.py"
    File "requirements.txt"
    File "README.md"
    File "LICENSE"
    
    # Copy Pandoc
    SetOutPath "$INSTDIR\\pandoc"
    File /r "build\\pandoc\\"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    # Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\run_reader.py"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    # Create desktop shortcut
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\run_reader.py"
    
    # Write registry keys
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayIcon" "$INSTDIR\\assets\\icon.ico"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    
    # Install Python dependencies
    DetailPrint "Installing Python dependencies..."
    ExecWait 'python -m pip install -r "$INSTDIR\\requirements.txt"'
    
    # Set up Pandoc
    DetailPrint "Setting up Pandoc..."
    ExecWait 'python -c "from src.utils.pandoc_installer import setup_pandoc; setup_pandoc()"'
SectionEnd

Section "Uninstall"
    # Remove files
    RMDir /r "$INSTDIR\\src"
    RMDir /r "$INSTDIR\\pandoc"
    Delete "$INSTDIR\\run_reader.py"
    Delete "$INSTDIR\\requirements.txt"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\LICENSE"
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir "$INSTDIR"
    
    # Remove shortcuts
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    # Remove registry keys
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
"""
        
        nsis_file = self.build_dir / "installer.nsi"
        with open(nsis_file, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        print("✅ NSIS script created")
        return nsis_file
    
    def build_installer(self):
        """Build the installer using NSIS"""
        print("🔨 Building installer with NSIS...")
        
        nsis_script = self.create_installer_script()
        
        try:
            # Check if NSIS is installed
            subprocess.run(['makensis', '/VERSION'], capture_output=True, check=True)
            
            # Build installer
            subprocess.check_call([
                'makensis', 
                f'/DOUTDIR={self.dist_dir}',
                str(nsis_script)
            ])
            
            print("✅ Installer built successfully")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ NSIS not found. Installer script created but not compiled.")
            print("   To build the installer, install NSIS from: https://nsis.sourceforge.io/")
            print(f"   Then run: makensis /DOUTDIR={self.dist_dir} {nsis_script}")
            return False
    
    def create_portable_package(self):
        """Create a portable package (alternative to installer)"""
        print("📦 Creating portable package...")
        
        portable_dir = self.dist_dir / "LLM_Textbook_Highlighter_Portable"
        portable_dir.mkdir(exist_ok=True)
        
        # Copy application files
        shutil.copytree("src", portable_dir / "src", dirs_exist_ok=True)
        shutil.copy("run_reader.py", portable_dir)
        shutil.copy("requirements.txt", portable_dir)
        shutil.copy("README.md", portable_dir)
        
        # Copy Pandoc
        if (self.build_dir / "pandoc").exists():
            shutil.copytree(self.build_dir / "pandoc", portable_dir / "pandoc", dirs_exist_ok=True)
        
        # Create batch file for easy execution
        batch_content = """@echo off
echo Starting LLM Textbook Highlighter...
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Starting application...
python run_reader.py
pause
"""
        
        with open(portable_dir / "run.bat", 'w') as f:
            f.write(batch_content)
        
        # Create portable zip
        portable_zip = self.dist_dir / "LLM_Textbook_Highlighter_Portable.zip"
        with zipfile.ZipFile(portable_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(portable_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, portable_dir)
                    zipf.write(file_path, arcname)
        
        print("✅ Portable package created")
        return portable_zip
    
    def build(self):
        """Main build process"""
        print("🚀 Starting Windows installer build process...")
        print("=" * 60)
        
        # Step 1: Clean build directories
        self.clean_build_dirs()
        
        # Step 2: Install Python dependencies
        if not self.install_python_dependencies():
            print("❌ Build failed: Could not install Python dependencies")
            return False
        
        # Step 3: Download Pandoc
        if not self.download_pandoc():
            print("⚠️  Warning: Could not download Pandoc. Installer will prompt user to install it.")
        
        # Step 4: Build installer
        installer_success = self.build_installer()
        
        # Step 5: Create portable package
        portable_zip = self.create_portable_package()
        
        print("=" * 60)
        print("🎉 Build process completed!")
        
        if installer_success:
            print(f"✅ Installer created: {self.dist_dir / f'{self.installer_name}.exe'}")
        
        print(f"✅ Portable package created: {portable_zip}")
        print(f"📁 Build artifacts in: {self.dist_dir}")
        
        return True

def main():
    """Main function"""
    builder = WindowsInstallerBuilder()
    
    try:
        success = builder.build()
        if success:
            print("\n🎯 Build successful! You can now distribute the installer.")
        else:
            print("\n❌ Build failed. Check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Build cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
