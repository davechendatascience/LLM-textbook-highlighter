# 🍎 Mac App Packaging Guide

This guide explains how to package the PDF Reader into a standalone Mac application that can be distributed and installed without requiring Python or dependencies.

## 📋 Prerequisites

- **macOS**: 10.13 or later
- **Python**: 3.8+ (for building)
- **Xcode Command Line Tools**: `xcode-select --install`

## 🚀 Quick Build

### Option 1: Simple Build Script
```bash
# Install build dependencies
pip install -r requirements-build.txt

# Run the build script
./build.sh
```

### Option 2: Interactive Build Script
```bash
# Run the interactive builder
python build_mac_app.py
```

### Option 3: Manual PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller PDFReader.spec
```

## 📦 Build Options

### 1. Single Executable (`--onefile`)
- **Pros**: Single file, easy to distribute
- **Cons**: Slower startup, larger memory usage
- **Use case**: Simple distribution, embedded systems

### 2. App Bundle (`--onedir`)
- **Pros**: Faster startup, more Mac-like
- **Cons**: Multiple files, larger disk space
- **Use case**: Standard Mac app installation

## 🔧 Configuration

### PyInstaller Spec File (`PDFReader.spec`)
The spec file contains advanced configuration:

- **Hidden imports**: All required dependencies
- **Data files**: Source modules and assets
- **Exclusions**: Unnecessary modules to reduce size
- **App bundle settings**: Mac-specific configuration

### Key Settings
```python
# App bundle configuration
'CFBundleName': 'PDF Reader',
'CFBundleVersion': '1.0.0',
'LSMinimumSystemVersion': '10.13.0',
'NSHighResolutionCapable': True,

# PDF file association
'CFBundleDocumentTypes': [
    {
        'CFBundleTypeName': 'PDF Document',
        'CFBundleTypeExtensions': ['pdf'],
        'CFBundleTypeRole': 'Viewer',
    }
]
```

## 📱 App Features

### Built-in Capabilities
- ✅ **PDF Association**: Opens PDFs by double-clicking
- ✅ **Native Mac UI**: Proper window management
- ✅ **High DPI Support**: Retina display compatibility
- ✅ **Dark Mode**: Automatic theme switching
- ✅ **App Sandboxing**: Secure execution environment

### File Associations
The app automatically registers as a PDF viewer:
- Double-click PDF files to open in the app
- Right-click → "Open With" → PDF Reader
- Drag and drop PDF files onto the app

## 🎨 Customization

### Adding an App Icon
1. Create an `.icns` file (512x512 recommended)
2. Place it in `assets/icon.icns`
3. Update the spec file:
```python
icon='assets/icon.icns'
```

### Custom App Name
Edit `PDFReader.spec`:
```python
name='YourAppName',
'CFBundleName': 'Your App Name',
'CFBundleDisplayName': 'Your App Name',
```

### Version Information
Update the spec file:
```python
'CFBundleVersion': '1.2.3',
'CFBundleShortVersionString': '1.2.3',
```

## 📦 Distribution

### Local Installation
```bash
# Copy to Applications
cp -R dist/PDFReader.app /Applications/

# Set permissions
chmod +x /Applications/PDFReader.app/Contents/MacOS/PDFReader
```

### Creating a DMG
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "PDF Reader" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "PDFReader.app" 175 120 \
  --hide-extension "PDFReader.app" \
  --app-drop-link 425 120 \
  "PDFReader.dmg" \
  "dist/"
```

### Code Signing (Optional)
```bash
# Sign the app (requires Apple Developer account)
codesign --force --deep --sign "Developer ID Application: Your Name" dist/PDFReader.app

# Verify signature
codesign --verify --verbose dist/PDFReader.app
```

## 🔍 Troubleshooting

### Common Issues

#### 1. "App is damaged" Error
```bash
# Remove quarantine attribute
xattr -cr dist/PDFReader.app
```

#### 2. Missing Dependencies
```bash
# Check what's missing
otool -L dist/PDFReader.app/Contents/MacOS/PDFReader

# Rebuild with explicit imports
pyinstaller --hidden-import=missing_module PDFReader.spec
```

#### 3. Large App Size
- Use `--exclude-module` to remove unused modules
- Enable UPX compression: `--upx-dir=/path/to/upx`
- Use `--onefile` for single executable

#### 4. PySide6 Issues
```bash
# Ensure PySide6 is properly included
pyinstaller --collect-all=PySide6 PDFReader.spec
```

### Debug Mode
```bash
# Build with console for debugging
pyinstaller --console PDFReader.spec

# Check app logs
Console.app → Search for "PDFReader"
```

## 📊 Performance Optimization

### Size Reduction
- **Exclude modules**: Remove unused dependencies
- **UPX compression**: Compress binaries
- **Stripping**: Remove debug symbols
- **Single file**: Use `--onefile` option

### Startup Speed
- **App bundle**: Use `--onedir` for faster startup
- **Lazy loading**: Import modules on demand
- **Precompiled**: Use `.pyc` files

## 🔒 Security Considerations

### App Sandboxing
- The app runs in a sandboxed environment
- Limited file system access
- Network access for API calls only

### Code Signing
- Sign with Apple Developer ID for distribution
- Prevents "unidentified developer" warnings
- Enables Gatekeeper compatibility

### Notarization (macOS 10.15+)
```bash
# Submit for notarization
xcrun altool --notarize-app \
  --primary-bundle-id "com.pdfreader.app" \
  --username "your-apple-id" \
  --password "app-specific-password" \
  --file "PDFReader.dmg"
```

## 📈 Advanced Features

### Auto-Updates
- Implement Sparkle framework
- Check for updates on startup
- Download and install automatically

### Crash Reporting
- Integrate Crashlytics or similar
- Collect crash reports automatically
- Send to analytics service

### Analytics
- Track app usage (with user consent)
- Monitor performance metrics
- Identify common issues

## 🎯 Best Practices

1. **Test thoroughly** on different macOS versions
2. **Use virtual machines** for testing
3. **Keep dependencies minimal** to reduce size
4. **Document installation process** for users
5. **Provide uninstall instructions**
6. **Monitor app performance** after distribution

## 📞 Support

For packaging issues:
1. Check PyInstaller documentation
2. Review macOS app development guidelines
3. Test on clean macOS installations
4. Verify all dependencies are included
