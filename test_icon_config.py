#!/usr/bin/env python3
"""
Test script to verify icon configuration is working correctly.
"""

import json
import sys
from pathlib import Path

def test_weather_html_config():
    """Test the weather HTML configuration."""
    print("Testing Weather HTML Configuration...")
    
    # Load main config
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config.json: {e}")
        return False
    
    # Check weather_html section
    weather_config = config.get('weather_html', {})
    if not weather_config:
        print("❌ No 'weather_html' section in config.json")
        return False
    
    print("✅ Found weather_html configuration")
    
    # Check icon_source
    icon_source = weather_config.get('icon_source', 'emoji')
    print(f"   icon_source: {icon_source}")
    
    if icon_source != 'custom':
        print(f"⚠️  icon_source is '{icon_source}', should be 'custom' for custom icons")
        print("   Update config.json: 'icon_source': 'custom'")
        return False
    
    # Check custom_icon_path
    custom_icon_path = weather_config.get('custom_icon_path', 'assets/icons/weather/')
    print(f"   custom_icon_path: {custom_icon_path}")
    
    # Check if path exists
    icon_dir = Path(custom_icon_path)
    if not icon_dir.exists():
        print(f"❌ Custom icon directory does not exist: {icon_dir}")
        return False
    
    print(f"✅ Custom icon directory exists: {icon_dir}")
    
    # Check for PNG files
    png_files = list(icon_dir.glob("*.png"))
    print(f"   Found {len(png_files)} PNG files")
    
    if not png_files:
        print("❌ No PNG files found in custom icon directory")
        return False
    
    for png_file in png_files:
        print(f"     ✅ {png_file.name}")
    
    return True

def test_icon_config_json():
    """Test the icon_config.json file."""
    print("\nTesting icon_config.json...")
    
    config_path = Path("assets/icons/weather/icon_config.json")
    if not config_path.exists():
        print("❌ icon_config.json not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            icon_config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading icon_config.json: {e}")
        return False
    
    print("✅ icon_config.json loaded successfully")
    
    # Check icon_sources
    icon_sources = icon_config.get('icon_sources', [])
    print(f"   icon_sources: {icon_sources}")
    
    if not icon_sources or icon_sources[0] != 'custom':
        print("⚠️  'custom' should be first in icon_sources")
        print("   Current: {icon_sources}")
        print("   Should be: ['custom', 'fontawesome', 'emoji']")
    
    # Check custom_icon_path
    custom_icon_path = icon_config.get('custom_icon_path', '')
    print(f"   custom_icon_path: {custom_icon_path}")
    
    # Check icon mapping
    icon_mapping = icon_config.get('icon_mapping', {})
    print(f"   Found {len(icon_mapping)} weather conditions")
    
    # Check a few key icons
    key_conditions = {
        '0': 'clear.png',
        '2': 'partly_cloudy.png', 
        '61': 'rain.png',
        '95': 'thunderstorm.png'
    }
    
    for code, expected_file in key_conditions.items():
        if code in icon_mapping:
            custom_icon = icon_mapping[code].get('custom', '')
            if custom_icon == expected_file:
                print(f"   ✅ Code {code}: {custom_icon}")
            else:
                print(f"   ⚠️  Code {code}: Expected {expected_file}, got {custom_icon}")
        else:
            print(f"   ❌ Code {code}: Not found in mapping")
    
    return True

def main():
    """Run configuration tests."""
    print("Icon Configuration Test")
    print("=" * 40)
    
    config_ok = test_weather_html_config()
    icon_config_ok = test_icon_config_json()
    
    print("\n" + "=" * 40)
    if config_ok and icon_config_ok:
        print("🎉 Configuration looks good!")
        print("\nIf custom icons still aren't showing, try:")
        print("1. Restart the MyImpression app")
        print("2. Check the app logs for error messages")
        print("3. Run: python debug_custom_icons.py")
    else:
        print("⚠️  Configuration issues found. Fix the issues above.")
    
    return config_ok and icon_config_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
