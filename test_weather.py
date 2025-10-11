#!/usr/bin/env python3
"""
Test script for the weather mode functionality.
This script can be used to test the weather display without running the full application.
"""

import json
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from modules.weather_api import WeatherAPIClient
from modules.weather import WeatherMode


def test_weather_api():
    """Test the weather API client."""
    print("Testing Weather API Client...")
    
    # Create test configuration
    config = {
        'weather': {
            'latitude': 51.5074,  # London
            'longitude': -0.1278,
            'update_interval': 1800,
            'cache_duration': 3600
        }
    }
    
    # Initialize API client
    api_client = WeatherAPIClient(config)
    
    # Test weather data fetching
    print("Fetching weather data...")
    weather_data = api_client.get_weather_data()
    
    if weather_data:
        print("✓ Weather data fetched successfully!")
        print(f"Current temperature: {weather_data['current']['temperature']}°C")
        print(f"Current conditions: {api_client.get_weather_description(weather_data['current']['weather_code'])}")
        print(f"5-day forecast: {len(weather_data['daily'])} days")
        print(f"Hourly forecast: {len(weather_data['hourly'])} hours")
        
        # Test weather descriptions
        print("\nTesting weather descriptions:")
        test_codes = [0, 1, 2, 3, 45, 61, 65, 71, 75, 95]
        for code in test_codes:
            desc = api_client.get_weather_description(code)
            print(f"  Code {code}: {desc}")
        
        return weather_data
    else:
        print("✗ Failed to fetch weather data")
        return None


def test_weather_mode():
    """Test the weather mode (without display)."""
    print("\nTesting Weather Mode...")
    
    # Create test configuration
    config = {
        'weather': {
            'latitude': 51.5074,  # London
            'longitude': -0.1278,
            'display_time': 300,
            'update_interval': 1800,
            'cache_duration': 3600
        }
    }
    
    # Mock display utilities
    class MockDisplayUtils:
        def __init__(self):
            self.BLACK = 0
            self.WHITE = 1
            self.GREEN = 2
            self.BLUE = 3
            self.RED = 4
            self.YELLOW = 5
        
        def create_image_with_palette(self):
            from PIL import Image
            return Image.new('P', (800, 480), self.WHITE)
        
        def get_font(self, size, font_size=None):
            from PIL import ImageFont
            return ImageFont.load_default()
        
        def draw_text_centered(self, draw, text, y, font, color):
            print(f"Drawing text: '{text}' at y={y}")
        
        def optimize_for_display(self, img):
            return img
        
        def show_error(self, message):
            print(f"Error: {message}")
    
    # Mock inky display
    class MockInky:
        def __init__(self):
            self.resolution = (800, 480)
        
        def set_image(self, img):
            print("Display image set")
        
        def show(self):
            print("Display updated")
    
    # Initialize weather mode
    mock_inky = MockInky()
    mock_display_utils = MockDisplayUtils()
    
    weather_mode = WeatherMode(mock_inky, config, mock_display_utils)
    
    # Test weather icon generation
    print("Testing weather icon generation...")
    test_codes = [0, 1, 2, 3, 45, 61, 65, 71, 75, 95]
    for code in test_codes:
        icon = weather_mode._get_weather_icon(code, size=40)
        if icon:
            print(f"  ✓ Generated icon for weather code {code}")
        else:
            print(f"  ✗ Failed to generate icon for weather code {code}")
    
    # Test display generation
    print("Testing display generation...")
    try:
        weather_mode.weather_data = weather_mode.weather_api.get_weather_data()
        if weather_mode.weather_data:
            img = weather_mode._generate_weather_display()
            if img:
                print("✓ Weather display generated successfully!")
                print(f"Image size: {img.size}")
                print(f"Image mode: {img.mode}")
            else:
                print("✗ Failed to generate weather display")
        else:
            print("✗ No weather data available for display test")
    except Exception as e:
        print(f"✗ Error generating display: {e}")


def main():
    """Run all tests."""
    print("Weather Mode Test Suite")
    print("=" * 50)
    
    # Test API client
    weather_data = test_weather_api()
    
    # Test weather mode
    test_weather_mode()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    
    if weather_data:
        print("\nSample weather data structure:")
        print(json.dumps({
            'current': weather_data['current'],
            'daily': weather_data['daily'][:2],  # First 2 days
            'hourly': weather_data['hourly'][:3]  # First 3 hours
        }, indent=2))


if __name__ == "__main__":
    main()
