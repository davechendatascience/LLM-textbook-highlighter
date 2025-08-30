# LLM PDF Reader - Packaging Guide

This guide explains how to build and package the LLM PDF Reader application for distribution using our unified build script.

## Prerequisites

### Required Tools
- Python 3.11+ with virtual environment
- macOS (for building macOS apps)
- create-dmg (optional, for DMG creation): `brew install create-dmg`

### Dependencies
All dependencies are managed automatically by the build script:
```bash
source .venv/bin/activate
```

## Quick Build

### Single Command Build
```bash
# Activate virtual environment
source .venv/bin/activate

# Build everything (DMG + ZIP)
python build_mac_installer.py

# Or just ZIP installer
python build_mac_installer.py --no-dmg

# Or just DMG installer
python build_mac_installer.py --no-zip

# Clean build directories only
python build_mac_installer.py --clean
```

### Build Options
- `--no-dmg`: Skip DMG creation (useful if create-dmg is not installed)
- `--no-zip`: Skip ZIP creation
- `--pkg`: Create PKG installer (requires installer/ directory with plist files)
- `--clean`: Clean build directories only

## What the Build Script Does

### 1. Prerequisites Check
- ✅ Verifies Python 3.11+
- ✅ Confirms macOS platform
- ✅ Checks for create-dmg (optional)

### 2. Dependency Management
- 📦 Installs PyInstaller automatically
- 🔧 Fixes NumPy compatibility issues
- 📋 Installs all required packages with correct versions

### 3. Build Process
- 🧹 Cleans previous build artifacts
- 📝 Creates optimized PyInstaller spec file
- 🔨 Builds the application bundle
- 🛡️ Removes quarantine attributes

### 4. Installer Creation
- 💾 DMG installer (if create-dmg is available)
- 📦 ZIP installer (always created)
- 📋 PKG installer (if --pkg flag is used)

## Generated Files

### App Bundle
- `dist/LLM PDF Reader.app` - Complete macOS application bundle
- Size: ~60-80 MB
- Contains all dependencies and resources

### Installers
- `LLM-PDF-Reader-Installer.dmg` - DMG installer (~70 MB)
- `LLM-PDF-Reader-Installer.zip` - ZIP installer (~65 MB)
- `LLM-PDF-Reader-Installer.pkg` - PKG installer (~70 MB, optional)

## File Structure

### App Bundle Contents
```
LLM PDF Reader.app/
├── Contents/
│   ├── Info.plist          # App metadata
│   ├── MacOS/              # Executable
│   ├── Resources/          # App resources
│   └── Frameworks/         # Dependencies
└── src/                    # Source code
```

### Key Components
- **Icon**: `assets/icon.icns` - Application icon
- **Source Code**: `src/` directory bundled with the app
- **Dependencies**: PySide6, PyMuPDF, Pillow, requests, etc.

## Troubleshooting

### Common Issues

#### 1. "No module named 'PySide6'"
**Solution**: Ensure virtual environment is activated
```bash
source .venv/bin/activate
python build_mac_installer.py
```

#### 2. "create-dmg not found"
**Solution**: Install create-dmg or skip DMG creation
```bash
# Install create-dmg
brew install create-dmg

# Or skip DMG creation
python build_mac_installer.py --no-dmg
```

#### 3. "Permission denied" errors
**Solution**: Remove quarantine attributes manually
```bash
xattr -cr "dist/LLM PDF Reader.app"
```

#### 4. Build fails with NumPy errors
**Solution**: The script automatically handles this, but you can manually fix:
```bash
pip install "numpy<2.0.0"
```

### Build Failures

#### PyInstaller Issues
- Clean build directories: `python build_mac_installer.py --clean`
- Check Python version: Must be 3.11+
- Verify virtual environment is activated

#### DMG Creation Issues
- Install create-dmg: `brew install create-dmg`
- Or use ZIP only: `python build_mac_installer.py --no-dmg`

## Advanced Usage

### Custom Build Configuration
The build script uses a comprehensive PyInstaller spec file that includes:
- All necessary hidden imports
- Proper data file inclusion
- Optimized exclusions
- macOS-specific settings

### PKG Installer (Advanced)
To create PKG installers, you need:
1. `installer/component.plist` - Component definition
2. `installer/distribution.xml` - Distribution configuration

Then run:
```bash
python build_mac_installer.py --pkg
```

## Distribution

### Recommended Distribution Method
1. **DMG Installer**: Best for end users (drag-and-drop installation)
2. **ZIP Installer**: Good for developers and testing
3. **PKG Installer**: For enterprise deployment

### File Sizes
- App Bundle: ~60-80 MB
- DMG Installer: ~70 MB
- ZIP Installer: ~65 MB
- PKG Installer: ~70 MB

### Compatibility
- **macOS**: 10.15 (Catalina) and later
- **Architecture**: Universal (Intel + Apple Silicon)
- **Python**: 3.11+ (bundled in app)
