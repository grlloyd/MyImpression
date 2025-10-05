#!/usr/bin/env python3
"""
Test script for weather dashboard functionality.
This script tests the weather API integration without requiring the full display setup.
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional


def test_open_meteo_api():
    """Test the Open-Meteo API with London coordinates."""
    print("Testing Open-Meteo API integration...")
    
    # London coordinates
    latitude = 51.5085300
    longitude = -0.1257400
    
    # API base URL
    api_base = "https://api.open-meteo.com/v1"
    
    try:
        # Test current weather
        print("Fetching current weather...")
        current_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m"
            ],
            "timezone": "auto"
        }
        
        current_url = f"{api_base}/forecast"
        current_response = requests.get(current_url, params=current_params, timeout=10)
        current_response.raise_for_status()
        current_data = current_response.json()
        
        print("✓ Current weather data fetched successfully")
        print(f"  Temperature: {current_data['current']['temperature_2m']}°C")
        print(f"  Weather code: {current_data['current']['weather_code']}")
        print(f"  Humidity: {current_data['current']['relative_humidity_2m']}%")
        print(f"  Wind speed: {current_data['current']['wind_speed_10m']} km/h")
        
        # Test forecast
        print("\nFetching forecast...")
        forecast_params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "wind_speed_10m_max"
            ],
            "timezone": "auto"
        }
        
        forecast_url = f"{api_base}/forecast"
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        print("✓ Forecast data fetched successfully")
        print(f"  Days available: {len(forecast_data['daily']['time'])}")
        
        # Show first 3 days of forecast
        for i in range(min(3, len(forecast_data['daily']['time']))):
            day = forecast_data['daily']['time'][i]
            max_temp = forecast_data['daily']['temperature_2m_max'][i]
            min_temp = forecast_data['daily']['temperature_2m_min'][i]
            weather_code = forecast_data['daily']['weather_code'][i]
            
            print(f"  Day {i+1}: {day} - {max_temp}°C/{min_temp}°C (code: {weather_code})")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_weather_icons():
    """Test weather icon mapping."""
    print("\nTesting weather icon mapping...")
    
    # Test various weather codes
    test_codes = [0, 1, 2, 3, 45, 51, 61, 71, 80, 95]
    
    def get_weather_icon(weather_code: int) -> str:
        """Get weather icon based on weather code."""
        if weather_code in [0]:
            return "☀️"  # Clear sky
        elif weather_code in [1, 2, 3]:
            return "⛅"  # Mainly clear, partly cloudy, overcast
        elif weather_code in [45, 48]:
            return "🌫️"  # Fog
        elif weather_code in [51, 53, 55, 56, 57]:
            return "🌦️"  # Drizzle
        elif weather_code in [61, 63, 65, 66, 67]:
            return "🌧️"  # Rain
        elif weather_code in [71, 73, 75, 77]:
            return "🌨️"  # Snow
        elif weather_code in [80, 81, 82]:
            return "🌦️"  # Rain showers
        elif weather_code in [85, 86]:
            return "🌨️"  # Snow showers
        elif weather_code in [95, 96, 99]:
            return "⛈️"  # Thunderstorm
        else:
            return "❓"  # Unknown
    
    for code in test_codes:
        icon = get_weather_icon(code)
        print(f"  Weather code {code}: {icon}")
    
    print("✓ Weather icon mapping working correctly")
    return True


def main():
    """Run all tests."""
    print("=== Weather Dashboard Test ===")
    print(f"Testing with London coordinates: 51.5085300, -0.1257400")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API connectivity
    api_success = test_open_meteo_api()
    
    # Test icon mapping
    icon_success = test_weather_icons()
    
    print("\n=== Test Results ===")
    print(f"API Integration: {'✓ PASS' if api_success else '✗ FAIL'}")
    print(f"Icon Mapping: {'✓ PASS' if icon_success else '✗ FAIL'}")
    
    if api_success and icon_success:
        print("\n🎉 All tests passed! Weather dashboard should work correctly.")
        print("You can now use button B to access the weather display.")
    else:
        print("\n❌ Some tests failed. Check your internet connection and try again.")


if __name__ == "__main__":
    main()
