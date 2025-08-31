#!/usr/bin/env python3
"""
Windows Installer Builder for LLM Textbook Highlighter
Creates both an NSIS installer and a portable package
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

def print_step(message):
    """Print a formatted step message"""
    print(f"🔨 {message}")

def print_success(message):
    """Print a formatted success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print a formatted error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print a formatted warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print a formatted info message"""
    print(f"ℹ️  {message}")

def check_nsis_installation():
    """Check if NSIS is installed and return the path to makensis"""
    # Common NSIS installation paths
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\NSIS\makensis.exe"
    ]
    
    for path in nsis_paths:
        if os.path.exists(path):
            return path
    
    return None

def create_nsis_script(build_dir, dist_dir):
    """Create the NSIS installer script"""
    # Copy required files to build directory
    if os.path.exists("LICENSE"):
        shutil.copy("LICENSE", build_dir)
    if os.path.exists("assets/llm_icon.ico"):
        shutil.copy("assets/llm_icon.ico", build_dir)
    
    # Copy the onedir executable directory
    onedir_path = "dist/LLM-Textbook-Highlighter"
    onedir_exe = "dist/LLM-Textbook-Highlighter/LLM-Textbook-Highlighter.exe"
    if os.path.exists(onedir_exe):
        # Copy the entire onedir directory
        if os.path.exists(os.path.join(build_dir, "LLM-Textbook-Highlighter")):
            shutil.rmtree(os.path.join(build_dir, "LLM-Textbook-Highlighter"))
        shutil.copytree(onedir_path, os.path.join(build_dir, "LLM-Textbook-Highlighter"))
        print_success("Onedir executable directory copied to build directory")
    else:
        print_error(f"Onedir executable not found: {onedir_exe}")
        print_info("Please run the onedir build first: python packaging/build_onedir_exe.py")
        return None
    
    # Copy documentation files
    for file in ["README.md"]:
        if os.path.exists(file):
            shutil.copy(file, build_dir)
    

    
    nsis_script = f"""# NSIS Installer Script for LLM Textbook Highlighter

!define APP_NAME "LLM Textbook Highlighter"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "LLM Textbook Highlighter Team"
!define APP_EXE "LLM-Textbook-Highlighter.exe"

!include "MUI2.nsh"

Name "${{APP_NAME}}"
OutFile "${{OUTDIR}}\\LLM_Textbook_Highlighter_Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""

RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "llm_icon.ico"
!define MUI_UNICON "llm_icon.ico"

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
    
    # Copy onedir executable directory and documentation
    File /r "LLM-Textbook-Highlighter"
    File "README.md"
    File "LICENSE"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    # Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\LLM-Textbook-Highlighter\\${{APP_EXE}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    
    # Create desktop shortcut
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\LLM-Textbook-Highlighter\\${{APP_EXE}}"
    
    # Write registry keys
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayIcon" "$INSTDIR\\LLM-Textbook-Highlighter\\${{APP_EXE}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    
    DetailPrint "Installing standalone application..."
    DetailPrint "No Python installation required - this is a standalone executable!"
SectionEnd

Section "Uninstall"
    # Remove files
    RMDir /r "$INSTDIR\\LLM-Textbook-Highlighter"
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
    
    script_path = os.path.join(build_dir, "installer.nsi")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    return script_path

def build_installer(nsis_script_path, dist_dir):
    """Build the NSIS installer"""
    nsis_path = check_nsis_installation()
    
    if not nsis_path:
        print_error("NSIS not found. Installer script created but not compiled.")
        print_info("To build the installer, install NSIS from: https://nsis.sourceforge.io/")
        print_info(f"Then run: makensis /DOUTDIR={dist_dir} {nsis_script_path}")
        return False
    
    try:
        # Build the installer using NSIS
        cmd = [
            nsis_path,
            f"/DOUTDIR={dist_dir}",
            nsis_script_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print_success("NSIS installer built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"NSIS build failed: {e}")
        print_error(f"NSIS output: {e.stdout}")
        print_error(f"NSIS error: {e.stderr}")
        return False

def create_portable_package(dist_dir):
    """Create a portable package (zip file) with onedir executable"""
    portable_dir = os.path.join(dist_dir, "portable")
    
    # Create portable directory structure
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    os.makedirs(portable_dir)
    
    # Copy onedir executable directory and documentation
    onedir_path = "dist/LLM-Textbook-Highlighter"
    onedir_exe = "dist/LLM-Textbook-Highlighter/LLM-Textbook-Highlighter.exe"
    if os.path.exists(onedir_exe):
        # Copy the entire onedir directory
        shutil.copytree(onedir_path, os.path.join(portable_dir, "LLM-Textbook-Highlighter"))
        print_success("Onedir executable directory copied to portable package")
    else:
        print_error(f"Onedir executable not found: {onedir_exe}")
        print_info("Please run the onedir build first: python packaging/build_onedir_exe.py")
        return None
    
    shutil.copy("README.md", portable_dir)
    shutil.copy("LICENSE", portable_dir)
    
    # Create a simple batch file to run the application
    batch_content = """@echo off
echo Starting LLM Textbook Highlighter...
echo This is a standalone executable - no Python installation required!
echo.
cd LLM-Textbook-Highlighter
LLM-Textbook-Highlighter.exe
pause
"""
    
    with open(os.path.join(portable_dir, "run.bat"), 'w') as f:
        f.write(batch_content)
    
    # Create zip file
    zip_path = os.path.join(dist_dir, "LLM_Textbook_Highlighter_Portable.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, portable_dir)
                zipf.write(file_path, arcname)
    
    # Clean up portable directory
    try:
        shutil.rmtree(portable_dir)
    except PermissionError:
        print_warning("Could not clean up portable directory - you may need to manually delete it")
    
    return zip_path

def build_onedir_if_needed():
    """Build the onedir executable if it doesn't exist"""
    onedir_exe = "dist/LLM-Textbook-Highlighter/LLM-Textbook-Highlighter.exe"
    
    if os.path.exists(onedir_exe):
        print_success("Onedir executable found - skipping build")
        return True
    
    print_step("Onedir executable not found - building it first...")
    
    try:
        # Run the onedir build script
        build_script = "packaging/build_onedir_exe.py"
        if not os.path.exists(build_script):
            print_error(f"Build script not found: {build_script}")
            return False
        
        result = subprocess.run([sys.executable, build_script], 
                              capture_output=True, text=True, check=True)
        print_success("Onedir build completed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Onedir build failed: {e}")
        if e.stdout:
            print(f"Build output: {e.stdout}")
        if e.stderr:
            print(f"Build error: {e.stderr}")
        return False

def main():
    """Main build process"""
    print("🚀 Starting Windows installer build process...")
    
    # Setup directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    build_dir = os.path.join(script_dir, "build")
    dist_dir = os.path.join(script_dir, "dist")
    
    # Change to project root
    os.chdir(project_root)
    
    # Create build and dist directories
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)
    
    # Build onedir executable if needed
    if not build_onedir_if_needed():
        return False
    
    # Check if onedir executable exists
    onedir_exe = "dist/LLM-Textbook-Highlighter/LLM-Textbook-Highlighter.exe"
    if not os.path.exists(onedir_exe):
        print_error(f"Onedir executable not found: {onedir_exe}")
        return False
    
    print_success("Onedir executable found - proceeding with installer build")
    
    # Build installer with NSIS
    print_step("Building installer with NSIS...")
    
    # Create NSIS script
    print_step("Creating NSIS installer script...")
    nsis_script_path = create_nsis_script(build_dir, dist_dir)
    if not nsis_script_path:
        return False
    print_success("NSIS script created")
    
    # Build the installer
    installer_success = build_installer(nsis_script_path, dist_dir)
    
    # Create portable package
    print_step("Creating portable package...")
    portable_path = create_portable_package(dist_dir)
    if not portable_path:
        return False
    print_success("Portable package created")
    
    # Summary
    print("=" * 60)
    print("🎉 Build process completed!")
    
    if installer_success:
        print_success("NSIS installer created")
        print("📁 Build artifacts in: " + dist_dir)
        print("🎯 Build successful! You can now distribute the installer.")
        print_info("Users don't need Python installed - this is a standalone application!")
        print_info("Uses onedir format for faster startup and better performance!")
    else:
        print_error("NSIS installer failed to build")
        print_info("Portable package created: " + portable_path)
        print_info("You can still distribute the portable package.")
        print_info("Uses onedir format for faster startup and better performance!")
    
    return True

if __name__ == "__main__":
    main()
