#!/usr/bin/env python3
"""
Test script to check Open-Meteo API data structure.
Run this to see what data we're actually getting from the API.
"""

import requests
import json

def test_api_structure():
    """Test the Open-Meteo API and show the data structure."""
    
    # London coordinates
    latitude = 51.5085300
    longitude = -0.1257400
    
    # API parameters
    params = {
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
        "hourly": [
            "temperature_2m",
            "weather_code",
            "precipitation",
            "wind_speed_10m"
        ],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max"
        ],
        "timezone": "auto"
    }
    
    try:
        print("Testing Open-Meteo API...")
        print(f"Coordinates: {latitude}, {longitude}")
        print("=" * 50)
        
        # Make the API request
        url = "https://api.open-meteo.com/v1/forecast"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("API Response Structure:")
        print("=" * 50)
        
        # Show the main structure
        print(f"Top-level keys: {list(data.keys())}")
        print()
        
        # Current weather data
        current = data.get("current", {})
        print("CURRENT WEATHER:")
        print(f"  Keys: {list(current.keys())}")
        if current:
            print(f"  Temperature: {current.get('temperature_2m', 'N/A')}")
            print(f"  Weather code: {current.get('weather_code', 'N/A')}")
            print(f"  Humidity: {current.get('relative_humidity_2m', 'N/A')}")
        print()
        
        # Hourly data
        hourly = data.get("hourly", {})
        print("HOURLY DATA:")
        print(f"  Keys: {list(hourly.keys())}")
        if hourly:
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            codes = hourly.get("weather_code", [])
            print(f"  Time entries: {len(times)}")
            print(f"  Temperature entries: {len(temps)}")
            print(f"  Weather code entries: {len(codes)}")
            if times:
                print(f"  First time: {times[0]}")
                print(f"  First temp: {temps[0] if temps else 'N/A'}")
                print(f"  First code: {codes[0] if codes else 'N/A'}")
        print()
        
        # Daily data
        daily = data.get("daily", {})
        print("DAILY DATA:")
        print(f"  Keys: {list(daily.keys())}")
        if daily:
            times = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            codes = daily.get("weather_code", [])
            print(f"  Time entries: {len(times)}")
            print(f"  Max temp entries: {len(max_temps)}")
            print(f"  Min temp entries: {len(min_temps)}")
            print(f"  Weather code entries: {len(codes)}")
            if times:
                print(f"  First day: {times[0]}")
                print(f"  First max temp: {max_temps[0] if max_temps else 'N/A'}")
                print(f"  First min temp: {min_temps[0] if min_temps else 'N/A'}")
                print(f"  First code: {codes[0] if codes else 'N/A'}")
        
        print("\n" + "=" * 50)
        print("Raw JSON (first 1000 chars):")
        print("=" * 50)
        print(json.dumps(data, indent=2)[:1000] + "...")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_api_structure()
