#!/bin/bash
# Setup script for HTML Weather Dashboard on Raspberry Pi

echo "Setting up HTML Weather Dashboard for Raspberry Pi..."

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install Chrome/Chromium and ChromeDriver
echo "Installing Chrome/Chromium and ChromeDriver..."
sudo apt install -y chromium-browser chromium-chromedriver

# Install Python dependencies
echo "Installing Python dependencies..."
pip install selenium Pillow requests

# Create necessary directories
echo "Creating directories..."
mkdir -p data/cache/weather
mkdir -p templates
mkdir -p assets/icons/weather

# Set permissions
echo "Setting permissions..."
chmod +x *.sh

echo "Setup complete!"
echo ""
echo "To test the weather dashboard:"
echo "1. Run: python test_weather_html.py"
echo "2. Check: data/cache/weather/test_weather.html"
echo ""
echo "If Chrome/ChromeDriver issues occur, the system will fall back to HTML-only mode."


