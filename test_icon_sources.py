#!/usr/bin/env python3
"""
Test script to verify different icon sources work correctly.
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

def test_icon_source(icon_source, description):
    """Test a specific icon source."""
    print(f"\n=== Testing {description} ===")
    
    # Create test configuration
    config = {
        'weather_html': {
            'icon_source': icon_source,
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
        print(f"   Custom icon path: {icon_config.get('custom_icon_path', '')}")
        
        # Test icon loading for a few weather codes
        test_codes = [0, 2, 61, 95]  # clear, partly cloudy, rain, thunderstorm
        for code in test_codes:
            icon = weather_mode._get_icon_for_weather_code(code, 'large')
            # Handle Unicode characters safely
            try:
                print(f"   Weather code {code}: {icon}")
            except UnicodeEncodeError:
                print(f"   Weather code {code}: [Unicode icon]")
        
        return True
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Test all icon sources."""
    print("Icon Source Test")
    print("=" * 40)
    
    # Test different icon sources
    tests = [
        ('emoji', 'Emoji Icons'),
        ('fontawesome', 'Font Awesome Icons'),
        ('custom', 'Custom PNG Icons')
    ]
    
    results = []
    for icon_source, description in tests:
        result = test_icon_source(icon_source, description)
        results.append(result)
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    for i, (icon_source, description) in enumerate(tests):
        status = "OK" if results[i] else "FAIL"
        print(f"{description}: {status}")
    
    if all(results):
        print("\nAll icon sources working correctly!")
    else:
        print("\nSome icon sources have issues.")

if __name__ == "__main__":
    main()
