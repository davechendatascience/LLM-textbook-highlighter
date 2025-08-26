# LLM PDF Reader - Packaging Guide

This guide explains how to build and package the LLM PDF Reader application for distribution.

## Prerequisites

### Required Tools
- Python 3.11+ with virtual environment
- PyInstaller (installed automatically)
- macOS (for building macOS apps)

### Dependencies
All dependencies are managed in the virtual environment:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Build

### 1. Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 2. Build the App
```bash
python build_mac_app.py
```
Choose option 2 for `.app bundle` when prompted.

### 3. Create Installers
```bash
# Create DMG installer
bash create_simple_dmg.sh

# Create ZIP installer
cd dist && zip -r "../LLM-PDF-Reader-Installer.zip" "LLM PDF Reader.app" && cd ..
```

## Manual Build Process

### Step 1: Clean Previous Builds
```bash
rm -rf build dist
```

### Step 2: Build with PyInstaller
```bash
pyinstaller --onefile --windowed \
  --name="LLM PDF Reader" \
  --icon=assets/icon.icns \
  --add-data=src:src \
  --hidden-import=PySide6.QtCore \
  --hidden-import=PySide6.QtGui \
  --hidden-import=PySide6.QtWidgets \
  --hidden-import=fitz \
  --hidden-import=PIL \
  --hidden-import=requests \
  run_reader.py
```

### Step 3: Test the App
```bash
./dist/LLM\ PDF\ Reader
```

### Step 4: Create Installers

#### DMG Installer (Recommended)
```bash
bash create_simple_dmg.sh
```

#### ZIP Installer
```bash
cd dist && zip -r "../LLM-PDF-Reader-Installer.zip" "LLM PDF Reader.app" && cd ..
```

## File Structure

### Generated Files
- `dist/LLM PDF Reader` - Single executable
- `dist/LLM PDF Reader.app` - macOS app bundle
- `LLM-PDF-Reader-Installer.dmg` - DMG installer (62MB)
- `LLM-PDF-Reader-Installer.zip` - ZIP installer (119MB)

### Key Components
- **App Bundle**: Contains all dependencies and resources
- **Icon**: `assets/icon.icns` - Application icon
- **Source Code**: `src/` directory bundled with the app
- **Dependencies**: PySide6, PyMuPDF, Pillow, requests, etc.

## Troubleshooting

### Common Issues

#### 1. "No module named 'PySide6'"
**Solution**: Ensure virtual environment is activated
```bash
source .venv/bin/activate
```

#### 2. App crashes on launch
**Solution**: Check if all dependencies are installed
```bash
pip install -r requirements.txt
```

#### 3. Build fails with symlink errors
**Solution**: Use `--onefile` mode instead of `--onedir`
```bash
pyinstaller --onefile --windowed ...
```

#### 4. App opens and closes immediately
**Solution**: Run from terminal to see error messages
```bash
./dist/LLM\ PDF\ Reader
```

### Build Verification

#### Test the App
```bash
# Test executable
./dist/LLM\ PDF\ Reader

# Test app bundle
open "dist/LLM PDF Reader.app"
```

#### Check File Sizes
- Executable: ~64MB
- App Bundle: ~64MB
- DMG Installer: ~62MB
- ZIP Installer: ~119MB

## Distribution

### GitHub Release
1. Upload both installers to GitHub release
2. Update README.md with download links
3. Tag the release with version number

### File Naming Convention
- `LLM-PDF-Reader-Installer.dmg` - macOS DMG
- `LLM-PDF-Reader-Installer.zip` - Cross-platform ZIP
- Version format: `v1.0.0`, `v1.1.0`, etc.

### Release Notes Template
```markdown
## LLM PDF Reader v1.0.0

### Features
- Cross-platform PDF reading
- AI-powered question generation
- Interactive text selection
- Built-in API configuration

### Downloads
- **macOS**: [LLM-PDF-Reader-Installer.dmg](link)
- **All Platforms**: [LLM-PDF-Reader-Installer.zip](link)

### Installation
1. Download the appropriate installer
2. Follow the installation instructions
3. Configure your Perplexity API key
4. Start reading PDFs with AI assistance
```

## Advanced Configuration

### Custom Icon
```bash
# Generate new icon
python create_llm_icon.py

# Use custom icon in build
pyinstaller --icon=assets/custom_icon.icns ...
```

### Code Signing (Optional)
```bash
# Sign the app (requires Apple Developer account)
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/LLM PDF Reader.app"
```

### Notarization (Optional)
```bash
# Notarize for distribution outside App Store
xcrun altool --notarize-app --primary-bundle-id "com.llmpdfreader.app" --username "your-apple-id" --password "app-specific-password" --file "LLM-PDF-Reader-Installer.dmg"
```

## Maintenance

### Regular Tasks
1. Update dependencies: `pip install -r requirements.txt --upgrade`
2. Test build process after dependency updates
3. Update version numbers in release notes
4. Clean old builds: `rm -rf build dist *.dmg *.zip`

### Version Management
- Update version in `run_reader.py` if needed
- Tag releases with semantic versioning
- Keep changelog updated

---

**Note**: This packaging process creates standalone applications that include all dependencies. Users don't need to install Python or any additional packages to run the app.
