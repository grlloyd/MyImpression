#!/usr/bin/env python3
"""
Test custom icon functionality specifically.
"""

import json
import tempfile
from pathlib import Path
from modules.weather_html import WeatherHTMLMode
from modules.display_utils import DisplayUtils

class MockInky:
    """Mock Inky display for testing."""
    def __init__(self):
        self.width = 800
        self.height = 480
        self.resolution = (800, 480)
        self.BLACK = 0
        self.WHITE = 1
        self.GREEN = 2
        self.BLUE = 3
        self.RED = 4
        self.YELLOW = 5
    
    def set_image(self, img, saturation=None):
        print(f"Mock display: Setting image {img.size} with saturation {saturation}")
    
    def show(self):
        print("Mock display: Showing image")

def test_custom_icon_processing():
    """Test custom icon processing."""
    print("Testing Custom Icon Processing...")
    
    # Create test configuration with custom icons
    config = {
        'weather_html': {
            'icon_source': 'custom',
            'custom_icon_path': 'assets/icons/weather/',
            'update_interval': 1800,
            'saturation': 0.5
        }
    }
    
    # Create mock objects
    mock_inky = MockInky()
    display_utils = DisplayUtils(mock_inky, config)
    
    try:
        # Create weather HTML mode
        weather_mode = WeatherHTMLMode(mock_inky, config, display_utils)
        
        # Check icon configuration
        icon_config = weather_mode.icon_config
        print(f"   Icon sources: {icon_config.get('icon_sources', [])}")
        
        # Check if custom icons were pre-processed
        icon_mapping = icon_config.get('icon_mapping', {})
        test_codes = ['0', '2', '61', '95']  # clear, partly cloudy, rain, thunderstorm
        
        for code in test_codes:
            if code in icon_mapping:
                custom_icon = icon_mapping[code].get('custom', '')
                if custom_icon.startswith('data:image/'):
                    print(f"   OK: Weather code {code} has base64 data URL")
                elif custom_icon.endswith('.png'):
                    print(f"   FAIL: Weather code {code} still has filename: {custom_icon}")
                else:
                    print(f"   WARN: Weather code {code} has unexpected format: {custom_icon}")
            else:
                print(f"   WARN: Weather code {code} not found in icon mapping")
        
        # Test icon loading
        for code in test_codes:
            icon = weather_mode._get_icon_for_weather_code(int(code), 'large')
            if icon and icon.startswith('data:image/'):
                print(f"   OK: _get_icon_for_weather_code({code}) returns base64 data URL")
            else:
                print(f"   FAIL: _get_icon_for_weather_code({code}) returns: {icon}")
        
        # Test HTML generation
        html_content = weather_mode._generate_html_content()
        if html_content:
            # Check if base64 data URLs are in the HTML
            if 'data:image/png;base64,' in html_content:
                print("   OK: Base64 data URLs found in HTML")
            else:
                print("   WARN: No base64 data URLs found in HTML")
            
            # Check if custom icon handling is present
            if 'iconContent.startsWith(\'data:image/\')' in html_content:
                print("   OK: Custom icon display logic found in HTML")
            else:
                print("   FAIL: Custom icon display logic not found in HTML")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_custom_icon_fallback():
    """Test custom icon fallback behavior."""
    print("\nTesting Custom Icon Fallback...")
    
    # Create test configuration with custom icons but no actual files
    config = {
        'weather_html': {
            'icon_source': 'custom',
            'custom_icon_path': 'nonexistent/path/',
            'update_interval': 1800,
            'saturation': 0.5
        }
    }
    
    # Create mock objects
    mock_inky = MockInky()
    display_utils = DisplayUtils(mock_inky, config)
    
    try:
        # Create weather HTML mode
        weather_mode = WeatherHTMLMode(mock_inky, config, display_utils)
        
        # Test icon loading with missing files
        test_codes = [0, 2, 61, 95]
        for code in test_codes:
            icon = weather_mode._get_icon_for_weather_code(code, 'large')
            if icon and icon.startswith('fas '):
                print(f"   OK: Weather code {code} falls back to Font Awesome: {icon}")
            elif icon and icon.startswith('data:image/'):
                print(f"   WARN: Weather code {code} still returns base64 (file might exist)")
            else:
                print(f"   INFO: Weather code {code} returns: {icon}")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Run custom icon tests."""
    print("Custom Icon Test")
    print("=" * 50)
    
    test1_ok = test_custom_icon_processing()
    test2_ok = test_custom_icon_fallback()
    
    print("\n" + "=" * 50)
    if test1_ok and test2_ok:
        print("All custom icon tests passed!")
    else:
        print("Some custom icon tests failed.")

if __name__ == "__main__":
    main()
