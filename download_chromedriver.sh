#!/bin/bash

# Print each command before executing
set -x

echo "Starting ChromeDriver download..."
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Create drivers directory if it doesn't exist
mkdir -p drivers || { echo "Failed to create drivers directory"; exit 1; }
cd drivers || { echo "Failed to change to drivers directory"; exit 1; }

echo "Inside drivers directory:"
ls -la

# Use a fixed version of ChromeDriver that works with Chromium
CHROMEDRIVER_VERSION="119.0.6045.105"
echo "Using ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download ChromeDriver
echo "Downloading ChromeDriver..."
wget -q -O chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" || { echo "Failed to download ChromeDriver"; exit 1; }

# Check if download was successful
if [ ! -f chromedriver.zip ]; then
    echo "ChromeDriver zip file not found!"
    exit 1
fi

echo "ChromeDriver zip file size:"
ls -lh chromedriver.zip

# Unzip ChromeDriver
echo "Extracting ChromeDriver..."
unzip -o chromedriver.zip || { echo "Failed to extract ChromeDriver"; exit 1; }
rm chromedriver.zip

# Check if chromedriver exists
if [ ! -f chromedriver ]; then
    echo "ChromeDriver executable not found!"
    exit 1
fi

# Make ChromeDriver executable
chmod +x chromedriver || { echo "Failed to make ChromeDriver executable"; exit 1; }

echo "ChromeDriver installation complete!"
echo "Final directory contents:"
ls -la
