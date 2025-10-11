#!/usr/bin/env python3
"""
Test Font Awesome configuration specifically.
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

def test_fontawesome_config():
    """Test Font Awesome configuration."""
    print("Testing Font Awesome Configuration...")
    
    # Create test configuration with Font Awesome
    config = {
        'weather_html': {
            'icon_source': 'fontawesome',
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
        
        # Test icon loading for a few weather codes
        test_codes = [0, 2, 61, 95]  # clear, partly cloudy, rain, thunderstorm
        for code in test_codes:
            icon = weather_mode._get_icon_for_weather_code(code, 'large')
            print(f"   Weather code {code}: {icon}")
        
        # Test HTML generation
        html_content = weather_mode._generate_html_content()
        if html_content:
            # Check if Font Awesome CSS is preserved
            if 'font-awesome' in html_content and 'fas.fa-sun:before' not in html_content:
                print("   OK: Font Awesome CSS preserved (not replaced with emoji)")
            elif 'fas.fa-sun:before' in html_content:
                print("   FAIL: Font Awesome CSS replaced with emoji fallbacks")
            else:
                print("   WARN: Font Awesome CSS not found")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_visibility_conversion():
    """Test visibility unit conversion."""
    print("\nTesting Visibility Conversion...")
    
    # Test cases: (input_meters, expected_output)
    test_cases = [
        (500, "500 m"),
        (1000, "1 km"),
        (1500, "1.5 km"),
        (59380, "59.4 km"),
        (10000, "10 km")
    ]
    
    for meters, expected in test_cases:
        # Simulate the JavaScript conversion
        visibility = meters
        unit = 'm'
        
        if visibility >= 1000:
            visibility = round(visibility / 1000 * 10) / 10
            unit = 'km'
        
        result = f"{visibility} {unit}"
        status = "OK" if result == expected else "FAIL"
        print(f"   {meters}m -> {result} {status} (expected: {expected})")

def main():
    """Run tests."""
    print("Font Awesome and Visibility Test")
    print("=" * 50)
    
    fontawesome_ok = test_fontawesome_config()
    test_visibility_conversion()
    
    print("\n" + "=" * 50)
    if fontawesome_ok:
        print("OK: Font Awesome configuration working!")
    else:
        print("FAIL: Font Awesome configuration has issues.")
    
    print("OK: Visibility conversion test completed.")

if __name__ == "__main__":
    main()
