#!/bin/bash

# Create drivers directory if it doesn't exist
mkdir -p drivers

# Download latest ChromeDriver
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -q -O drivers/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip

# Unzip ChromeDriver
cd drivers
unzip -o chromedriver.zip
rm chromedriver.zip

# Make ChromeDriver executable
chmod +x chromedriver
