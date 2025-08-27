#!/usr/bin/env python3
"""
Release Helper Script for LLM PDF Reader
Automates the release process and creates release notes
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime

def run_command(cmd, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def get_git_status():
    """Get current git status"""
    status = run_command("git status --porcelain")
    if status:
        print("⚠️  Uncommitted changes detected:")
        print(status)
        return False
    return True

def get_current_version():
    """Get current version from git tags"""
    tags = run_command("git tag --sort=-version:refname")
    if tags:
        latest_tag = tags.split('\n')[0]
        return latest_tag
    return "v0.0.0"

def create_release_notes(version, previous_version=None):
    """Create release notes template"""
    if not previous_version:
        previous_version = "v0.0.0"
    
    # Get commits since last release
    commits = run_command(f"git log --oneline {previous_version}..HEAD")
    
    template = f"""# Release Notes

## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### 🎉 Release Summary

Brief description of what's new in this release.

### ✨ New Features

- **Feature 1**: Description of new feature
- **Feature 2**: Description of new feature

### 🔧 Improvements

- **Improvement 1**: Description of improvement
- **Improvement 2**: Description of improvement

### 🐛 Bug Fixes

- **Fix 1**: Description of bug fix
- **Fix 2**: Description of bug fix

### 📋 Changes Since {previous_version}

```
{commits if commits else "No commits found"}
```

### 🚀 Installation

#### Quick Start
1. Download the appropriate installer for your system
2. Follow the installation instructions
3. Configure your Perplexity API key
4. Start reading PDFs with AI assistance

### 📊 File Information

#### Installer Sizes
- **App Bundle**: ~60-80 MB
- **DMG Installer**: ~70 MB
- **ZIP Installer**: ~65 MB

### 🔮 What's Next

Planned features for the next release:
- **Feature 1**: Description
- **Feature 2**: Description

---

**Note**: This release includes various improvements and bug fixes. We welcome feedback and suggestions for future improvements.
"""
    
    return template

def build_release(version):
    """Build the release packages"""
    print(f"🔨 Building release {version}...")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    run_command("python build_mac_installer.py --clean")
    
    # Build new packages
    print("📦 Building packages...")
    success = run_command("python build_mac_installer.py")
    
    if success:
        print("✅ Build completed successfully")
        return True
    else:
        print("❌ Build failed")
        return False

def create_git_tag(version, message=None):
    """Create a git tag for the release"""
    if not message:
        message = f"Release {version}"
    
    print(f"🏷️  Creating git tag {version}...")
    success = run_command(f'git tag -a {version} -m "{message}"')
    
    if success:
        print(f"✅ Tag {version} created successfully")
        return True
    else:
        print(f"❌ Failed to create tag {version}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create a new release of LLM PDF Reader")
    parser.add_argument("version", help="Version number (e.g., v1.1.0)")
    parser.add_argument("--build", action="store_true", help="Build release packages")
    parser.add_argument("--tag", action="store_true", help="Create git tag")
    parser.add_argument("--notes", action="store_true", help="Create release notes")
    parser.add_argument("--message", help="Tag message")
    
    args = parser.parse_args()
    
    print("🚀 LLM PDF Reader - Release Helper")
    print("=" * 50)
    
    # Check git status
    if not get_git_status():
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")
    print(f"🎯 Target version: {args.version}")
    
    # Create release notes
    if args.notes:
        print("\n📝 Creating release notes...")
        notes = create_release_notes(args.version, current_version)
        
        notes_file = f"RELEASE_NOTES_{args.version}.md"
        with open(notes_file, 'w') as f:
            f.write(notes)
        
        print(f"✅ Release notes created: {notes_file}")
    
    # Build packages
    if args.build:
        if not build_release(args.version):
            print("❌ Build failed, stopping release process")
            return
    
    # Create git tag
    if args.tag:
        if not create_git_tag(args.version, args.message):
            print("❌ Tag creation failed")
            return
    
    print("\n🎉 Release process completed!")
    print(f"📦 Version: {args.version}")
    
    if args.build:
        print("📱 App bundle: dist/LLM PDF Reader.app")
        print("💾 DMG installer: LLM-PDF-Reader-Installer.dmg")
        print("📦 ZIP installer: LLM-PDF-Reader-Installer.zip")
    
    if args.notes:
        print(f"📝 Release notes: RELEASE_NOTES_{args.version}.md")

if __name__ == "__main__":
    main()
