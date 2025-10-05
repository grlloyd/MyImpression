"""
Weather Dashboard Mode
Displays current weather and forecast using Open-Meteo API.
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from PIL import Image, ImageDraw, ImageFont


class WeatherDashboardMode:
    """Weather dashboard mode using Open-Meteo API."""
    
    def __init__(self, inky_display, config: dict, display_utils):
        """Initialize weather dashboard mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.logger = logging.getLogger(__name__)
        
        # Weather configuration
        self.weather_config = config.get("weather", {})
        self.latitude = self.weather_config.get("latitude", 51.5085300)
        self.longitude = self.weather_config.get("longitude", -0.1257400)
        self.location = self.weather_config.get("location", "London, UK")
        self.units = self.weather_config.get("units", "metric")
        self.update_interval = self.weather_config.get("update_interval", 1800)  # 30 minutes
        
        # Cache for weather data
        self.weather_data = None
        self.last_update = 0
        
        # Open-Meteo API base URL
        self.api_base = "https://api.open-meteo.com/v1"
    
    def _fetch_weather_data(self) -> Optional[Dict[str, Any]]:
        """Fetch current weather and forecast data from Open-Meteo API."""
        try:
            # Current weather parameters
            current_params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
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
            
            # Forecast parameters (next 7 days)
            forecast_params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "daily": [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "wind_speed_10m_max"
                ],
                "timezone": "auto"
            }
            
            # Fetch current weather
            current_url = f"{self.api_base}/forecast"
            current_response = requests.get(current_url, params=current_params, timeout=10)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            # Fetch forecast
            forecast_url = f"{self.api_base}/forecast"
            forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Combine data
            weather_data = {
                "current": current_data.get("current", {}),
                "forecast": forecast_data.get("daily", {}),
                "location": self.location,
                "timestamp": time.time()
            }
            
            self.logger.info("Weather data fetched successfully")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch weather data: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching weather data: {e}")
            return None
    
    def _get_weather_icon(self, weather_code: int) -> str:
        """Get weather icon based on weather code."""
        # WMO Weather interpretation codes
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
    
    def _get_weather_description(self, weather_code: int) -> str:
        """Get weather description based on weather code."""
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
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
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
    
    def _format_temperature(self, temp: float) -> str:
        """Format temperature with unit."""
        unit = "°C" if self.units == "metric" else "°F"
        return f"{temp:.1f}{unit}"
    
    def _format_wind_speed(self, speed: float) -> str:
        """Format wind speed with unit."""
        if self.units == "metric":
            return f"{speed:.1f} km/h"
        else:
            return f"{speed:.1f} mph"
    
    def _create_weather_display(self) -> Image.Image:
        """Create the weather display image."""
        img = self.display_utils.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        if not self.weather_data:
            # Show error if no data
            self.display_utils.draw_text_centered(
                draw, "Weather Data Unavailable", 
                self.inky.height // 2 - 50, 
                self.display_utils.get_font('large', 24), 
                self.display_utils.RED
            )
            self.display_utils.draw_text_centered(
                draw, "Check connection and try again", 
                self.inky.height // 2 + 20, 
                self.display_utils.get_font('medium', 16), 
                self.display_utils.BLACK
            )
            return img
        
        current = self.weather_data.get("current", {})
        forecast = self.weather_data.get("forecast", {})
        
        # Header
        y_pos = 20
        self.display_utils.draw_text_centered(
            draw, f"Weather - {self.location}", 
            y_pos, 
            self.display_utils.get_font('large', 20), 
            self.display_utils.BLUE
        )
        
        # Current weather
        y_pos += 50
        temp = current.get("temperature_2m", 0)
        weather_code = current.get("weather_code", 0)
        weather_icon = self._get_weather_icon(weather_code)
        weather_desc = self._get_weather_description(weather_code)
        
        # Temperature (large)
        self.display_utils.draw_text_centered(
            draw, f"{weather_icon} {self._format_temperature(temp)}", 
            y_pos, 
            self.display_utils.get_font('large', 32), 
            self.display_utils.BLACK
        )
        
        # Weather description
        y_pos += 40
        self.display_utils.draw_text_centered(
            draw, weather_desc, 
            y_pos, 
            self.display_utils.get_font('medium', 16), 
            self.display_utils.BLACK
        )
        
        # Additional current conditions
        y_pos += 60
        humidity = current.get("relative_humidity_2m", 0)
        wind_speed = current.get("wind_speed_10m", 0)
        precipitation = current.get("precipitation", 0)
        
        # Two-column layout for additional info
        left_x = self.inky.width // 4
        right_x = 3 * self.inky.width // 4
        
        # Left column
        self.display_utils.draw_text_centered(
            draw, f"Humidity: {humidity:.0f}%", 
            y_pos, 
            self.display_utils.get_font('small', 14), 
            self.display_utils.BLACK
        )
        
        self.display_utils.draw_text_centered(
            draw, f"Wind: {self._format_wind_speed(wind_speed)}", 
            y_pos + 25, 
            self.display_utils.get_font('small', 14), 
            self.display_utils.BLACK
        )
        
        # Right column
        self.display_utils.draw_text_centered(
            draw, f"Precip: {precipitation:.1f}mm", 
            y_pos, 
            self.display_utils.get_font('small', 14), 
            self.display_utils.BLACK
        )
        
        # Forecast section (next 3 days)
        y_pos += 80
        self.display_utils.draw_text_centered(
            draw, "3-Day Forecast", 
            y_pos, 
            self.display_utils.get_font('medium', 16), 
            self.display_utils.BLUE
        )
        
        # Forecast days
        forecast_days = forecast.get("time", [])[:3]
        forecast_max = forecast.get("temperature_2m_max", [])[:3]
        forecast_min = forecast.get("temperature_2m_min", [])[:3]
        forecast_codes = forecast.get("weather_code", [])[:3]
        
        y_pos += 30
        for i, (day, max_temp, min_temp, code) in enumerate(zip(forecast_days, forecast_max, forecast_min, forecast_codes)):
            if i >= 3:  # Limit to 3 days
                break
                
            # Parse date
            try:
                date_obj = datetime.fromisoformat(day.replace('Z', '+00:00'))
                day_name = date_obj.strftime('%a')
            except:
                day_name = f"Day {i+1}"
            
            # Weather icon
            icon = self._get_weather_icon(code)
            
            # Day info
            day_text = f"{day_name} {icon} {self._format_temperature(max_temp)}/{self._format_temperature(min_temp)}"
            
            self.display_utils.draw_text_centered(
                draw, day_text, 
                y_pos, 
                self.display_utils.get_font('small', 12), 
                self.display_utils.BLACK
            )
            
            y_pos += 25
        
        # Last updated timestamp
        if self.weather_data.get("timestamp"):
            update_time = datetime.fromtimestamp(self.weather_data["timestamp"])
            time_str = update_time.strftime("%H:%M")
            self.display_utils.draw_text_centered(
                draw, f"Updated: {time_str}", 
                self.inky.height - 20, 
                self.display_utils.get_font('small', 10), 
                self.display_utils.BLACK
            )
        
        return img
    
    def run(self, running_flag):
        """Run weather dashboard mode."""
        self.logger.info("Starting weather dashboard mode")
        
        while running_flag:
            try:
                # Check if we need to update weather data
                current_time = time.time()
                if (self.weather_data is None or 
                    current_time - self.last_update > self.update_interval):
                    
                    self.logger.info("Fetching weather data...")
                    self.display_utils.show_loading("Loading weather...")
                    
                    # Fetch new weather data
                    new_data = self._fetch_weather_data()
                    if new_data:
                        self.weather_data = new_data
                        self.last_update = current_time
                        self.logger.info("Weather data updated successfully")
                    else:
                        self.logger.warning("Failed to fetch weather data, using cached data if available")
                
                # Create and display weather information
                weather_img = self._create_weather_display()
                
                try:
                    self.inky.set_image(weather_img)
                    self.inky.show()
                    self.logger.debug("Weather display updated")
                except Exception as e:
                    self.logger.error(f"Failed to display weather: {e}")
                
                # Wait before next update
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                self.logger.error(f"Error in weather dashboard: {e}")
                self.display_utils.show_error(f"Weather Error:\n{str(e)}")
                time.sleep(30)  # Wait 30 seconds before retrying
