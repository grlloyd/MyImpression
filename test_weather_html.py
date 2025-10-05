#!/usr/bin/env python3
"""
Test script for HTML weather dashboard
"""

import json
import time
from pathlib import Path
from modules.html_weather_renderer import HTMLWeatherRenderer, FallbackHTMLWeatherRenderer

def create_test_weather_data():
    """Create sample weather data for testing."""
    return {
        "current": {
            "temperature_2m": 22.5,
            "relative_humidity_2m": 65,
            "apparent_temperature": 24.1,
            "precipitation": 0.0,
            "weather_code": 1,
            "cloud_cover": 25,
            "wind_speed_10m": 12.3,
            "wind_direction_10m": 180
        },
        "hourly": {
            "time": [
                "2024-01-15T12:00", "2024-01-15T13:00", "2024-01-15T14:00", "2024-01-15T15:00",
                "2024-01-15T16:00", "2024-01-15T17:00", "2024-01-15T18:00", "2024-01-15T19:00",
                "2024-01-15T20:00", "2024-01-15T21:00", "2024-01-15T22:00", "2024-01-15T23:00"
            ],
            "temperature_2m": [22, 23, 24, 25, 24, 23, 22, 21, 20, 19, 18, 17],
            "weather_code": [1, 1, 2, 2, 3, 3, 2, 1, 0, 0, 0, 0],
            "precipitation": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "wind_speed_10m": [10, 12, 14, 16, 15, 13, 11, 9, 8, 7, 6, 5]
        },
        "daily": {
            "time": [
                "2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18", "2024-01-19"
            ],
            "weather_code": [1, 2, 3, 61, 95],
            "temperature_2m_max": [25, 23, 21, 18, 16],
            "temperature_2m_min": [15, 13, 11, 8, 6],
            "precipitation_sum": [0, 0, 0, 5.2, 12.8],
            "wind_speed_10m_max": [15, 18, 20, 25, 30]
        },
        "location": "London, UK",
        "timestamp": time.time()
    }

def test_html_weather_renderer():
    """Test the HTML weather renderer."""
    print("Testing HTML Weather Renderer...")
    
    # Create test data
    weather_data = create_test_weather_data()
    
    # Test with fallback renderer first (no browser required)
    print("Testing fallback renderer...")
    fallback_renderer = FallbackHTMLWeatherRenderer()
    
    output_path = "data/cache/weather/test_weather.html"
    Path("data/cache/weather").mkdir(parents=True, exist_ok=True)
    
    success = fallback_renderer.render_weather_dashboard(weather_data, output_path)
    if success:
        print(f"✓ Fallback renderer created HTML file: {output_path}")
    else:
        print("✗ Fallback renderer failed")
    
    # Test with full renderer (requires Chrome)
    print("\nTesting full HTML renderer...")
    try:
        html_renderer = HTMLWeatherRenderer()
        
        png_path = "data/cache/weather/test_weather.png"
        success = html_renderer.render_weather_dashboard(weather_data, png_path)
        
        if success and Path(png_path).exists():
            print(f"✓ Full renderer created PNG file: {png_path}")
        else:
            print("✗ Full renderer failed to create PNG")
        
        html_renderer.close()
        
    except Exception as e:
        print(f"✗ Full renderer failed: {e}")
        print("This is expected if Chrome/ChromeDriver is not installed")

def test_weather_icons():
    """Test weather icon mapping."""
    print("\nTesting weather icon mapping...")
    
    # Test various weather codes
    test_codes = [0, 1, 2, 3, 45, 61, 65, 71, 75, 95]
    
    for code in test_codes:
        # This would test the icon mapping in the HTML template
        print(f"Weather code {code}: Would map to FontAwesome icon")

if __name__ == "__main__":
    print("HTML Weather Dashboard Test")
    print("=" * 40)
    
    test_html_weather_renderer()
    test_weather_icons()
    
    print("\nTest completed!")
    print("\nTo view the HTML dashboard:")
    print("1. Open data/cache/weather/test_weather.html in a web browser")
    print("2. The page should show a weather dashboard with FontAwesome icons")
    print("3. If Chrome is available, a PNG screenshot should also be created")
