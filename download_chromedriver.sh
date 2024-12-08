#!/bin/bash
set -e  # Exit on error

echo "Starting ChromeDriver download..."

# Create drivers directory if it doesn't exist
mkdir -p drivers
cd drivers

# Use a fixed version of ChromeDriver that works with Chromium
CHROMEDRIVER_VERSION="119.0.6045.105"
echo "Using ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download ChromeDriver
echo "Downloading ChromeDriver..."
wget -q -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"

# Unzip ChromeDriver
echo "Extracting ChromeDriver..."
unzip -o chromedriver.zip
rm chromedriver.zip

# Make ChromeDriver executable
chmod +x chromedriver

echo "ChromeDriver installation complete!"
ls -la  # List directory contents for verification
