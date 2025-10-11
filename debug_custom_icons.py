#!/usr/bin/env python3
"""
Debug script to test custom icon loading on Raspberry Pi.
Run this on your Pi to diagnose custom icon issues.
"""

import json
import logging
from pathlib import Path
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_icon_config():
    """Test icon configuration loading."""
    print("=== Testing Icon Configuration ===")
    
    # Test 1: Check if config.json exists and has weather_html section
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json not found!")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        weather_config = config.get('weather_html', {})
        icon_source = weather_config.get('icon_source', 'emoji')
        custom_icon_path = weather_config.get('custom_icon_path', 'assets/icons/weather/')
        
        print(f"✅ config.json found")
        print(f"   icon_source: {icon_source}")
        print(f"   custom_icon_path: {custom_icon_path}")
        
        if icon_source != 'custom':
            print(f"⚠️  icon_source is '{icon_source}', should be 'custom'")
            return False
            
    except Exception as e:
        print(f"❌ Error reading config.json: {e}")
        return False
    
    return True

def test_icon_directory():
    """Test if icon directory exists and contains PNG files."""
    print("\n=== Testing Icon Directory ===")
    
    # Get custom icon path from config
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        custom_icon_path = config.get('weather_html', {}).get('custom_icon_path', 'assets/icons/weather/')
    except:
        custom_icon_path = 'assets/icons/weather/'
    
    icon_dir = Path(custom_icon_path)
    print(f"Checking directory: {icon_dir.absolute()}")
    
    if not icon_dir.exists():
        print(f"❌ Directory does not exist: {icon_dir}")
        return False
    
    print(f"✅ Directory exists: {icon_dir}")
    
    # Check for PNG files
    png_files = list(icon_dir.glob("*.png"))
    print(f"Found {len(png_files)} PNG files:")
    
    if not png_files:
        print("❌ No PNG files found in directory!")
        return False
    
    for png_file in png_files:
        print(f"   ✅ {png_file.name}")
    
    return True

def test_icon_config_json():
    """Test icon_config.json file."""
    print("\n=== Testing icon_config.json ===")
    
    config_path = Path("assets/icons/weather/icon_config.json")
    if not config_path.exists():
        print("❌ icon_config.json not found!")
        return False
    
    try:
        with open(config_path, 'r') as f:
            icon_config = json.load(f)
        
        print("✅ icon_config.json found")
        print(f"   icon_sources: {icon_config.get('icon_sources', [])}")
        print(f"   custom_icon_path: {icon_config.get('custom_icon_path', '')}")
        
        # Check if custom is first in icon_sources
        sources = icon_config.get('icon_sources', [])
        if sources and sources[0] != 'custom':
            print(f"⚠️  First icon source is '{sources[0]}', should be 'custom'")
        
        # Check icon mapping
        icon_mapping = icon_config.get('icon_mapping', {})
        print(f"   Found {len(icon_mapping)} weather conditions")
        
        # Check a few specific icons
        test_codes = ['0', '2', '61', '95']  # clear, partly cloudy, rain, thunderstorm
        for code in test_codes:
            if code in icon_mapping:
                custom_icon = icon_mapping[code].get('custom', '')
                print(f"   Code {code}: {custom_icon}")
            else:
                print(f"   Code {code}: Not found in mapping")
        
    except Exception as e:
        print(f"❌ Error reading icon_config.json: {e}")
        return False
    
    return True

def test_icon_loading():
    """Test actual icon loading."""
    print("\n=== Testing Icon Loading ===")
    
    try:
        # Load icon config
        with open("assets/icons/weather/icon_config.json", 'r') as f:
            icon_config = json.load(f)
        
        custom_icon_path = icon_config.get('custom_icon_path', 'assets/icons/weather/')
        icon_mapping = icon_config.get('icon_mapping', {})
        
        # Test loading a few icons
        test_codes = ['0', '2', '61', '95']
        for code in test_codes:
            if code in icon_mapping:
                custom_icon = icon_mapping[code].get('custom', '')
                if custom_icon:
                    icon_path = Path(custom_icon_path) / custom_icon
                    print(f"Testing {custom_icon}...")
                    
                    if icon_path.exists():
                        try:
                            with Image.open(icon_path) as img:
                                print(f"   ✅ {custom_icon}: {img.size}, mode: {img.mode}")
                        except Exception as e:
                            print(f"   ❌ {custom_icon}: Error loading - {e}")
                    else:
                        print(f"   ❌ {custom_icon}: File not found at {icon_path}")
                else:
                    print(f"   ⚠️  Code {code}: No custom icon defined")
            else:
                print(f"   ⚠️  Code {code}: Not in icon mapping")
    
    except Exception as e:
        print(f"❌ Error testing icon loading: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Custom Icon Debug Script")
    print("=" * 50)
    
    tests = [
        test_icon_config,
        test_icon_directory,
        test_icon_config_json,
        test_icon_loading
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Configuration: {'✅' if results[0] else '❌'}")
    print(f"Directory: {'✅' if results[1] else '❌'}")
    print(f"Config JSON: {'✅' if results[2] else '❌'}")
    print(f"Icon Loading: {'✅' if results[3] else '❌'}")
    
    if all(results):
        print("\n🎉 All tests passed! Custom icons should work.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("\nCommon fixes:")
        print("1. Set icon_source: 'custom' in config.json")
        print("2. Ensure PNG files are in the correct directory")
        print("3. Check file permissions on the icon directory")
        print("4. Verify icon filenames match icon_config.json")

if __name__ == "__main__":
    main()
