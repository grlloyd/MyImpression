#!/usr/bin/env python3
"""
Test script to verify weather data processing.
This will help debug why weather data isn't displaying.
"""

import requests
from datetime import datetime

def test_weather_processing():
    """Test the weather data processing logic."""
    
    # London coordinates
    latitude = 51.5085300
    longitude = -0.1257400
    
    # API parameters (same as in weather_dashboard.py)
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
        print("Testing Weather Data Processing...")
        print("=" * 50)
        
        # Make the API request
        url = "https://api.open-meteo.com/v1/forecast"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Test current weather processing
        print("CURRENT WEATHER:")
        current = data.get("current", {})
        temp = current.get("temperature_2m", 0)
        weather_code = current.get("weather_code", 0)
        humidity = current.get("relative_humidity_2m", 0)
        wind_speed = current.get("wind_speed_10m", 0)
        
        print(f"  Temperature: {temp}°C")
        print(f"  Weather Code: {weather_code}")
        print(f"  Humidity: {humidity}%")
        print(f"  Wind Speed: {wind_speed} km/h")
        
        # Test hourly data processing
        print("\nHOURLY FORECAST (Next 6 hours):")
        hourly = data.get("hourly", {})
        hourly_times = hourly.get("time", [])[:6]
        hourly_temps = hourly.get("temperature_2m", [])[:6]
        hourly_codes = hourly.get("weather_code", [])[:6]
        
        for i, (time_str, temp, code) in enumerate(zip(hourly_times, hourly_temps, hourly_codes)):
            try:
                time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                hour_str = time_obj.strftime('%H:%M')
            except:
                hour_str = f"H{i+1}"
            
            print(f"  {hour_str}: {temp}°C (code: {code})")
        
        # Test daily data processing
        print("\nDAILY FORECAST (Next 5 days):")
        daily = data.get("daily", {})
        daily_times = daily.get("time", [])[:5]
        daily_max = daily.get("temperature_2m_max", [])[:5]
        daily_min = daily.get("temperature_2m_min", [])[:5]
        daily_codes = daily.get("weather_code", [])[:5]
        
        for i, (day, max_temp, min_temp, code) in enumerate(zip(daily_times, daily_max, daily_min, daily_codes)):
            try:
                date_obj = datetime.fromisoformat(day.replace('Z', '+00:00'))
                day_name = date_obj.strftime('%a')
            except:
                day_name = f"Day {i+1}"
            
            print(f"  {day_name}: {max_temp}°C/{min_temp}°C (code: {code})")
        
        print("\n" + "=" * 50)
        print("Data processing test completed successfully!")
        print("If you see data above, the weather display should work.")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_weather_processing()
