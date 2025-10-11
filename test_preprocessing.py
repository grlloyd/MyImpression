#!/usr/bin/env python3
"""
Test script to verify icon preprocessing works
"""

import json
from modules.weather_html import WeatherHTMLMode

def test_preprocessing():
    """Test if icon preprocessing works correctly."""
    
    # Create a config with custom icon source
    config = {
        'weather_html': {
            'icon_source': 'custom',
            'custom_icon_path': 'assets/icons/weather/'
        }
    }
    
    # Create a mock inky display and other dependencies
    class MockInky:
        def __init__(self):
            self.width = 800
            self.height = 480
    
    class MockDisplayUtils:
        pass
    
    # Create weather HTML mode
    weather_mode = WeatherHTMLMode(MockInky(), config, MockDisplayUtils())
    
    # Get the icon config
    icon_config = weather_mode.icon_config
    
    # Check if preprocessing worked
    print("Testing icon preprocessing:")
    
    # Check specific weather codes
    test_codes = ['0', '1', '2', '80', '81']
    
    for code in test_codes:
        if code in icon_config.get('icon_mapping', {}):
            weather_icons = icon_config['icon_mapping'][code]
            print(f"\nWeather code {code}:")
            
            # Check day icon
            if 'custom' in weather_icons:
                custom_icon = weather_icons['custom']
                if custom_icon.startswith('data:image/'):
                    print(f"  ✓ Day icon is base64 data URL (length: {len(custom_icon)})")
                else:
                    print(f"  ✗ Day icon is still filename: {custom_icon}")
            
            # Check night icon
            if 'custom_night' in weather_icons:
                custom_night_icon = weather_icons['custom_night']
                if custom_night_icon.startswith('data:image/'):
                    print(f"  ✓ Night icon is base64 data URL (length: {len(custom_night_icon)})")
                else:
                    print(f"  ✗ Night icon is still filename: {custom_night_icon}")
        else:
            print(f"  Weather code {code}: NOT FOUND")

if __name__ == "__main__":
    test_preprocessing()
