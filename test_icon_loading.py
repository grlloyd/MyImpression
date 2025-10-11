#!/usr/bin/env python3
"""
Test script to debug icon loading on Raspberry Pi
"""

import json
import os
from pathlib import Path

def test_icon_loading():
    """Test if icon files can be found and loaded."""
    
    # Test the icon path
    icon_path = Path("assets/icons/weather/")
    print(f"Testing icon path: {icon_path.absolute()}")
    print(f"Path exists: {icon_path.exists()}")
    
    if icon_path.exists():
        print(f"Contents of {icon_path}:")
        for file in sorted(icon_path.iterdir()):
            print(f"  {file.name}")
    
    # Test specific icon files
    test_files = [
        "clear.png",
        "clear-night.png", 
        "partly_cloudy.png",
        "partly_cloudy-night.png",
        "showers.png",
        "showers-night.png"
    ]
    
    print(f"\nTesting specific icon files:")
    for filename in test_files:
        file_path = icon_path / filename
        exists = file_path.exists()
        print(f"  {filename}: {'✓' if exists else '✗'}")
        if exists:
            print(f"    Size: {file_path.stat().st_size} bytes")
    
    # Test the icon config loading
    config_path = icon_path / "icon_config.json"
    print(f"\nTesting icon config: {config_path}")
    print(f"Config exists: {config_path.exists()}")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print(f"Config loaded successfully")
            print(f"Icon sources: {config.get('icon_sources', [])}")
            print(f"Custom icon path: {config.get('custom_icon_path', 'NOT SET')}")
            
            # Check a few weather codes
            icon_mapping = config.get('icon_mapping', {})
            test_codes = ['0', '1', '2', '80', '81']
            
            print(f"\nChecking weather codes:")
            for code in test_codes:
                if code in icon_mapping:
                    weather_icons = icon_mapping[code]
                    print(f"  Code {code}:")
                    print(f"    custom: {weather_icons.get('custom', 'NOT SET')}")
                    print(f"    custom_night: {weather_icons.get('custom_night', 'NOT SET')}")
                else:
                    print(f"  Code {code}: NOT FOUND")
                    
        except Exception as e:
            print(f"Error loading config: {e}")

if __name__ == "__main__":
    test_icon_loading()
