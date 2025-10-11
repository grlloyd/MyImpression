"""
Weather API Client Module
Handles fetching weather data from Open-Meteo API.
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path


class WeatherAPIClient:
    """Client for fetching weather data from Open-Meteo API."""
    
    def __init__(self, config: dict):
        """Initialize the weather API client."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Get weather configuration
        self.weather_config = config.get('weather', {})
        self.latitude = self.weather_config.get('latitude', 51.5074)  # Default to London
        self.longitude = self.weather_config.get('longitude', -0.1278)
        self.update_interval = self.weather_config.get('update_interval', 1800)  # 30 minutes
        self.cache_duration = self.weather_config.get('cache_duration', 3600)  # 1 hour
        
        # Cache file path
        self.cache_file = Path("data/cache/weather_data.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # API base URL
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def get_weather_data(self) -> Optional[Dict[str, Any]]:
        """Get weather data, using cache if available and fresh."""
        # Check if we have fresh cached data
        cached_data = self._load_from_cache()
        if cached_data and self._is_cache_fresh(cached_data):
            self.logger.info("Using cached weather data")
            return cached_data
        
        # Fetch fresh data from API
        try:
            fresh_data = self._fetch_from_api()
            if fresh_data:
                self._save_to_cache(fresh_data)
                return fresh_data
        except Exception as e:
            self.logger.error(f"Failed to fetch weather data: {e}")
            
            # Return cached data even if stale as fallback
            if cached_data:
                self.logger.warning("Using stale cached data as fallback")
                return cached_data
        
        return None
    
    def _fetch_from_api(self) -> Optional[Dict[str, Any]]:
        """Fetch weather data from Open-Meteo API."""
        params = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'current': 'temperature_2m,weather_code,apparent_temperature,wind_speed_10m,relative_humidity_2m,surface_pressure,visibility,uv_index',
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max',
            'hourly': 'temperature_2m,weather_code',
            'forecast_days': 5,
            'timezone': 'auto'
        }
        
        self.logger.info(f"Fetching weather data for {self.latitude}, {self.longitude}")
        
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Process and structure the data
        processed_data = self._process_api_data(data)
        processed_data['fetched_at'] = datetime.now().isoformat()
        
        return processed_data
    
    def _process_api_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw API data into our internal format."""
        current = api_data.get('current', {})
        daily = api_data.get('daily', {})
        hourly = api_data.get('hourly', {})
        
        # Process current weather
        current_weather = {
            'temperature': round(current.get('temperature_2m', 0)),
            'weather_code': current.get('weather_code', 0),
            'time': current.get('time', ''),
            'feels_like': round(current.get('apparent_temperature', 0)),
            'wind_speed': round(current.get('wind_speed_10m', 0)),
            'humidity': round(current.get('relative_humidity_2m', 0)),
            'pressure': round(current.get('surface_pressure', 0)),
            'visibility': round(current.get('visibility', 0)),
            'uv_index': round(current.get('uv_index', 0))
        }
        
        # Process daily forecast (5 days)
        daily_forecast = []
        daily_times = daily.get('time', [])
        daily_codes = daily.get('weather_code', [])
        daily_max = daily.get('temperature_2m_max', [])
        daily_min = daily.get('temperature_2m_min', [])
        daily_sunrise = daily.get('sunrise', [])
        daily_sunset = daily.get('sunset', [])
        daily_uv = daily.get('uv_index_max', [])
        
        for i in range(min(5, len(daily_times))):
            daily_forecast.append({
                'time': daily_times[i],
                'weather_code': daily_codes[i] if i < len(daily_codes) else 0,
                'temp_max': round(daily_max[i]) if i < len(daily_max) else 0,
                'temp_min': round(daily_min[i]) if i < len(daily_min) else 0,
                'sunrise': daily_sunrise[i] if i < len(daily_sunrise) else '',
                'sunset': daily_sunset[i] if i < len(daily_sunset) else '',
                'uv_index': round(daily_uv[i]) if i < len(daily_uv) else 0
            })
        
        # Process hourly forecast (next 12 hours)
        hourly_forecast = []
        hourly_times = hourly.get('time', [])
        hourly_codes = hourly.get('weather_code', [])
        hourly_temps = hourly.get('temperature_2m', [])
        
        # Get current hour and next 11 hours
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        for i in range(12):
            target_time = current_hour + timedelta(hours=i)
            target_time_str = target_time.strftime('%Y-%m-%dT%H:00')
            
            # Find matching hour in API data
            for j, api_time in enumerate(hourly_times):
                if api_time.startswith(target_time_str):
                    hourly_forecast.append({
                        'time': api_time,
                        'weather_code': hourly_codes[j] if j < len(hourly_codes) else 0,
                        'temperature': round(hourly_temps[j]) if j < len(hourly_temps) else 0
                    })
                    break
            else:
                # If no exact match, use closest available
                if i < len(hourly_times):
                    hourly_forecast.append({
                        'time': hourly_times[i],
                        'weather_code': hourly_codes[i] if i < len(hourly_codes) else 0,
                        'temperature': round(hourly_temps[i]) if i < len(hourly_temps) else 0
                    })
        
        return {
            'current': current_weather,
            'daily': daily_forecast,
            'hourly': hourly_forecast,
            'location': {
                'name': self.get_location_name(),
                'latitude': self.latitude,
                'longitude': self.longitude
            }
        }
    
    def _load_from_cache(self) -> Optional[Dict[str, Any]]:
        """Load weather data from cache file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load cache: {e}")
        return None
    
    def _save_to_cache(self, data: Dict[str, Any]):
        """Save weather data to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
    
    def _is_cache_fresh(self, cached_data: Dict[str, Any]) -> bool:
        """Check if cached data is still fresh."""
        try:
            fetched_at = cached_data.get('fetched_at')
            if not fetched_at:
                return False
            
            fetch_time = datetime.fromisoformat(fetched_at)
            age = datetime.now() - fetch_time
            
            return age.total_seconds() < self.cache_duration
        except Exception as e:
            self.logger.error(f"Error checking cache freshness: {e}")
            return False
    
    def get_weather_description(self, weather_code: int) -> str:
        """Get human-readable weather description from weather code."""
        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return descriptions.get(weather_code, "Unknown")
    
    def get_day_name(self, date_str: str) -> str:
        """Get day name from date string."""
        try:
            date_obj = datetime.fromisoformat(date_str)
            return date_obj.strftime('%a')  # Mon, Tue, Wed, etc.
        except:
            return "???"
    
    def format_hour(self, time_str: str) -> str:
        """Format time string to hour display."""
        try:
            time_obj = datetime.fromisoformat(time_str)
            return time_obj.strftime('%H')  # 24-hour format
        except:
            return "??"
    
    def get_location_name(self) -> str:
        """Get location name from coordinates using reverse geocoding."""
        try:
            # Use Nominatim (OpenStreetMap) free reverse geocoding API
            geocoding_url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'en'
            }
            
            # Add user agent header (required by Nominatim)
            headers = {
                'User-Agent': 'MyImpression Weather App (contact@example.com)'
            }
            
            response = requests.get(geocoding_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            address = data.get('address', {})
            
            if address:
                # Extract city/town name
                city = (address.get('city') or 
                       address.get('town') or 
                       address.get('village') or 
                       address.get('hamlet') or 
                       address.get('municipality') or
                       address.get('suburb'))
                
                # Extract state/province
                state = (address.get('state') or 
                        address.get('province') or 
                        address.get('county'))
                
                # Extract country
                country = address.get('country')
                
                # Format the location string
                if city and country:
                    if state and state != city:
                        return f"{city}, {state}, {country}"
                    else:
                        return f"{city}, {country}"
                elif country:
                    return country
                else:
                    # Fallback to coordinates if no useful address found
                    return self._format_coordinates()
            else:
                # Fallback to coordinates if no address found
                return self._format_coordinates()
                
        except Exception as e:
            self.logger.warning(f"Failed to get city name: {e}")
            # Fallback to coordinates
            return self._format_coordinates()
    
    def _format_coordinates(self) -> str:
        """Format coordinates as a readable location string."""
        lat_dir = "N" if self.latitude >= 0 else "S"
        lon_dir = "E" if self.longitude >= 0 else "W"
        
        lat_abs = abs(self.latitude)
        lon_abs = abs(self.longitude)
        
        return f"{lat_abs:.2f}°{lat_dir}, {lon_abs:.2f}°{lon_dir}"
    
    def format_date_display(self, date_str: str) -> str:
        """Format date string to 'Day, Month DD' format."""
        try:
            date_obj = datetime.fromisoformat(date_str)
            return date_obj.strftime('%A, %B %d')  # Thursday, March 13
        except:
            return "Unknown Date"
    
    def format_sunrise_sunset(self, time_str: str) -> str:
        """Format sunrise/sunset time to HH:MM format."""
        try:
            time_obj = datetime.fromisoformat(time_str)
            return time_obj.strftime('%H:%M')
        except:
            return "??:??"
