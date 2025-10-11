#!/usr/bin/env python3
"""
Test metric icons with different icon sources.
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

def test_metric_icons(icon_source, description):
    """Test metric icons with a specific icon source."""
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
        
        # Generate HTML content
        html_content = weather_mode._generate_html_content()
        if not html_content:
            print("   FAIL: Could not generate HTML content")
            return False
        
        # Check if metric icons are present in HTML
        metrics = ['sunrise', 'wind', 'pressure', 'visibility', 'sunset', 'humidity', 'uv-index', 'air-quality']
        all_found = True
        
        for metric in metrics:
            icon_id = f"{metric}-icon"
            if icon_id in html_content:
                print(f"   OK: {metric} icon ID found")
            else:
                print(f"   FAIL: {metric} icon ID not found")
                all_found = False
        
        # Check if getMetricIcon function is present
        if 'getMetricIcon' in html_content:
            print("   OK: getMetricIcon function found")
        else:
            print("   FAIL: getMetricIcon function not found")
            all_found = False
        
        # Check if updateMetricIcons function is present
        if 'updateMetricIcons' in html_content:
            print("   OK: updateMetricIcons function found")
        else:
            print("   FAIL: updateMetricIcons function not found")
            all_found = False
        
        # Check icon source specific behavior
        if icon_source == 'fontawesome':
            if 'fas fa-' in html_content:
                print("   OK: Font Awesome classes found in HTML")
            else:
                print("   WARN: Font Awesome classes not found in HTML")
        elif icon_source == 'emoji':
            if 'fas fa-' not in html_content or 'fas.fa-sun:before' in html_content:
                print("   OK: Font Awesome replaced with emoji fallbacks")
            else:
                print("   WARN: Font Awesome not replaced with emoji fallbacks")
        
        return all_found
        
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    """Test metric icons with different icon sources."""
    print("Metric Icons Test")
    print("=" * 50)
    
    # Test different icon sources
    tests = [
        ('emoji', 'Emoji Icons'),
        ('fontawesome', 'Font Awesome Icons'),
        ('custom', 'Custom PNG Icons')
    ]
    
    results = []
    for icon_source, description in tests:
        result = test_metric_icons(icon_source, description)
        results.append(result)
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for i, (icon_source, description) in enumerate(tests):
        status = "OK" if results[i] else "FAIL"
        print(f"{description}: {status}")
    
    if all(results):
        print("\nAll metric icon tests passed!")
    else:
        print("\nSome metric icon tests failed.")

if __name__ == "__main__":
    main()
