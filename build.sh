#!/bin/bash

# PDF Reader Mac App Builder
# Simple script to build a standalone Mac application

echo "🍎 Building PDF Reader for Mac..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist __pycache__ *.spec

# Build the app using the spec file
echo "🚀 Building application..."
pyinstaller PDFReader.spec

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📱 App location: $(pwd)/dist/PDFReader.app"
    echo ""
    echo "🎉 You can now:"
    echo "1. Test the app: open dist/PDFReader.app"
    echo "2. Install to Applications: cp -R dist/PDFReader.app /Applications/"
    echo "3. Create a DMG for distribution"
else
    echo "❌ Build failed!"
    exit 1
fi
