#!/bin/bash
set -e  # Exit on error

echo "Starting ChromeDriver download..."

# Create drivers directory if it doesn't exist
mkdir -p drivers
cd drivers

# Get Chrome version
CHROME_VERSION=$(chromium-browser --version | grep -oP "[\d.]+")
echo "Chrome version: $CHROME_VERSION"

# Get matching ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

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
