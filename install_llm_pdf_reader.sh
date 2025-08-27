#!/bin/bash
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
