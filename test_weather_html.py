#!/usr/bin/env python3
"""
Test script for HTML Weather Mode
Tests the HTML weather display without requiring the full application.
"""

import json
import logging
from pathlib import Path
from modules.weather_html import WeatherHTMLMode
from modules.display_utils import DisplayUtils

# Mock Inky display for testing
class MockInky:
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
    
    def set_image(self, img):
        print(f"Mock display: Setting image {img.size}")
        # Save the image for inspection
        img.save("test_weather_output.png")
        print("Test image saved as 'test_weather_output.png'")
    
    def show(self):
        print("Mock display: Showing image")

def main():
    """Test the HTML weather mode."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create mock display
    mock_inky = MockInky()
    
    # Load test configuration
    config = {
        "weather": {
            "latitude": 51.5074,
            "longitude": -0.1278,
            "display_time": 300,
            "update_interval": 1800,
            "cache_duration": 3600
        }
    }
    
    # Initialize display utils
    display_utils = DisplayUtils(mock_inky, config)
    
    # Initialize HTML weather mode
    weather_html = WeatherHTMLMode(mock_inky, config, display_utils)
    
    print("Testing HTML Weather Mode...")
    print("This will attempt to generate a weather display using HTML rendering.")
    print("Playwright browser automation is required for this mode to work.")
    
    try:
        # Force an update
        weather_html.update_display()
        print("HTML weather mode test completed successfully!")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
