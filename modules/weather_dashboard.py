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
from .weather_icons import WeatherIconManager


class WeatherDashboardMode:
    """Weather dashboard mode using Open-Meteo API."""
    
    def __init__(self, inky_display, config: dict, display_utils, main_app=None):
        """Initialize weather dashboard mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.main_app = main_app  # Reference to main app for mode switching
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
        
        # Initialize weather icon manager
        self.icon_manager = WeatherIconManager()
    
    def _fetch_weather_data(self) -> Optional[Dict[str, Any]]:
        """Fetch current weather and forecast data from Open-Meteo API."""
        try:
            # Combined parameters for current, hourly, and daily data
            params = {
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
            
            # Fetch all weather data in one request
            url = f"{self.api_base}/forecast"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Combine data
            weather_data = {
                "current": data.get("current", {}),
                "hourly": data.get("hourly", {}),
                "daily": data.get("daily", {}),
                "location": self.location,
                "timestamp": time.time()
            }
            
            self.logger.info("Weather data fetched successfully")
            # Debug: Log the structure of the data
            self.logger.debug(f"Current data keys: {list(data.get('current', {}).keys())}")
            self.logger.debug(f"Hourly data keys: {list(data.get('hourly', {}).keys())}")
            self.logger.debug(f"Daily data keys: {list(data.get('daily', {}).keys())}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch weather data: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching weather data: {e}")
            return None
    
    
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
        """Create the weather display image with white background and 3-section layout."""
        # Create image with white background
        img = self.display_utils.create_blank_image(self.display_utils.WHITE)
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
        hourly = self.weather_data.get("hourly", {})
        daily = self.weather_data.get("daily", {})
        
        # Calculate section heights (divide screen into thirds)
        section_height = self.inky.height // 3
        current_section = 0
        hourly_section = section_height
        daily_section = section_height * 2
        
        # === TOP SECTION: CURRENT WEATHER ===
        self._draw_current_weather(draw, current, current_section, section_height)
        
        # === MIDDLE SECTION: 12-HOUR FORECAST ===
        self._draw_hourly_forecast(draw, hourly, hourly_section, section_height)
        
        # === BOTTOM SECTION: 5-DAY FORECAST ===
        self._draw_daily_forecast(draw, daily, daily_section, section_height)
        
        # Last updated timestamp
        if self.weather_data.get("timestamp"):
            update_time = datetime.fromtimestamp(self.weather_data["timestamp"])
            time_str = update_time.strftime("%H:%M")
            self.display_utils.draw_text_centered(
                draw, f"Updated: {time_str}", 
                self.inky.height - 10, 
                self.display_utils.get_font('small', 8), 
                self.display_utils.BLACK
            )
        
        return img
    
    def _draw_current_weather(self, draw: ImageDraw.Draw, current: dict, start_y: int, height: int):
        """Draw current weather section."""
        center_y = start_y + height // 2
        
        # Location header
        self.display_utils.draw_text_centered(
            draw, f"{self.location}", 
            start_y + 10, 
            self.display_utils.get_font('medium', 14), 
            self.display_utils.BLUE
        )
        
        # Current temperature and weather icon
        temp = current.get("temperature_2m", 0)
        weather_code = current.get("weather_code", 0)
        weather_desc = self._get_weather_description(weather_code)
        
        # Get weather icon
        icon_img = self.icon_manager.get_icon_image(weather_code, (40, 40))
        
        # Draw temperature
        temp_text = self._format_temperature(temp)
        self.display_utils.draw_text_centered(
            draw, temp_text, 
            center_y - 10, 
            self.display_utils.get_font('large', 32), 
            self.display_utils.BLACK
        )
        
        # Draw weather icon if available
        if icon_img:
            icon_x = (self.inky.width - 40) // 2
            icon_y = center_y - 30
            # Convert icon to display format and paste
            try:
                # Create a temporary image for the icon
                icon_display = self.display_utils.create_blank_image(self.display_utils.WHITE)
                icon_display.paste(icon_img, (icon_x, icon_y), icon_img if icon_img.mode == 'RGBA' else None)
                # Paste the icon onto main image
                img = draw._image
                img.paste(icon_display, (0, 0))
            except Exception as e:
                self.logger.warning(f"Failed to draw weather icon: {e}")
        
        # Weather description
        self.display_utils.draw_text_centered(
            draw, weather_desc, 
            center_y + 25, 
            self.display_utils.get_font('small', 12), 
            self.display_utils.BLACK
        )
        
        # Current conditions
        humidity = current.get("relative_humidity_2m", 0)
        wind_speed = current.get("wind_speed_10m", 0)
        precipitation = current.get("precipitation", 0)
        
        conditions_text = f"H: {humidity:.0f}% | W: {self._format_wind_speed(wind_speed)} | P: {precipitation:.1f}mm"
        self.display_utils.draw_text_centered(
            draw, conditions_text, 
            start_y + height - 15, 
            self.display_utils.get_font('small', 10), 
            self.display_utils.BLACK
        )
    
    def _draw_hourly_forecast(self, draw: ImageDraw.Draw, hourly: dict, start_y: int, height: int):
        """Draw 12-hour forecast section."""
        # Section header
        self.display_utils.draw_text_centered(
            draw, "12-Hour Forecast", 
            start_y + 5, 
            self.display_utils.get_font('small', 12), 
            self.display_utils.BLUE
        )
        
        # Get hourly data for next 12 hours
        hourly_times = hourly.get("time", [])[:12]
        hourly_temps = hourly.get("temperature_2m", [])[:12]
        hourly_codes = hourly.get("weather_code", [])[:12]
        
        if hourly_times and hourly_temps and hourly_codes:
            # Calculate layout for 12 hours in 2 rows of 6
            items_per_row = 6
            item_width = self.inky.width // items_per_row
            row_height = (height - 30) // 2  # Leave space for header
            
            for i, (time_str, temp, code) in enumerate(zip(hourly_times, hourly_temps, hourly_codes)):
                if i >= 12:  # Limit to 12 hours
                    break
                
                # Calculate position
                col = i % items_per_row
                row = i // items_per_row
                
                x = col * item_width + item_width // 2
                y = start_y + 25 + row * row_height
                
                # Parse time
                try:
                    time_obj = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    hour_str = time_obj.strftime('%H:%M')
                except:
                    hour_str = f"H{i+1}"
                
                # Draw time
                draw.text((x - 20, y - 15), hour_str, 
                         font=self.display_utils.get_font('small', 8), 
                         fill=self.display_utils.BLACK)
                
                # Draw weather icon
                icon_img = self.icon_manager.get_icon_image(code, (20, 20))
                if icon_img:
                    try:
                        icon_x = x - 10
                        icon_y = y - 5
                        # Create temporary image for icon
                        icon_display = self.display_utils.create_blank_image(self.display_utils.WHITE)
                        icon_display.paste(icon_img, (icon_x, icon_y), icon_img if icon_img.mode == 'RGBA' else None)
                        # Paste onto main image
                        img = draw._image
                        img.paste(icon_display, (0, 0))
                    except Exception as e:
                        self.logger.warning(f"Failed to draw hourly icon: {e}")
                
                # Draw temperature
                temp_text = self._format_temperature(temp)
                draw.text((x - 15, y + 10), temp_text, 
                         font=self.display_utils.get_font('small', 8), 
                         fill=self.display_utils.BLACK)
        else:
            # Show error message if no hourly data
            self.display_utils.draw_text_centered(
                draw, "No hourly data available", 
                start_y + height // 2, 
                self.display_utils.get_font('small', 10), 
                self.display_utils.RED
            )
    
    def _draw_daily_forecast(self, draw: ImageDraw.Draw, daily: dict, start_y: int, height: int):
        """Draw 5-day forecast section."""
        # Section header
        self.display_utils.draw_text_centered(
            draw, "5-Day Forecast", 
            start_y + 5, 
            self.display_utils.get_font('small', 12), 
            self.display_utils.BLUE
        )
        
        # Get daily data for next 5 days
        daily_times = daily.get("time", [])[:5]
        daily_max = daily.get("temperature_2m_max", [])[:5]
        daily_min = daily.get("temperature_2m_min", [])[:5]
        daily_codes = daily.get("weather_code", [])[:5]
        
        if daily_times and daily_max and daily_min and daily_codes:
            # Calculate layout for 5 days
            item_height = (height - 30) // 5  # Leave space for header
            
            for i, (day, max_temp, min_temp, code) in enumerate(zip(daily_times, daily_max, daily_min, daily_codes)):
                y = start_y + 25 + i * item_height
                
                # Parse date
                try:
                    date_obj = datetime.fromisoformat(day.replace('Z', '+00:00'))
                    day_name = date_obj.strftime('%a')
                except:
                    day_name = f"Day {i+1}"
                
                # Draw day name
                draw.text((10, y - 5), day_name, 
                         font=self.display_utils.get_font('small', 10), 
                         fill=self.display_utils.BLACK)
                
                # Draw weather icon
                icon_img = self.icon_manager.get_icon_image(code, (24, 24))
                if icon_img:
                    try:
                        icon_x = 80
                        icon_y = y - 12
                        # Create temporary image for icon
                        icon_display = self.display_utils.create_blank_image(self.display_utils.WHITE)
                        icon_display.paste(icon_img, (icon_x, icon_y), icon_img if icon_img.mode == 'RGBA' else None)
                        # Paste onto main image
                        img = draw._image
                        img.paste(icon_display, (0, 0))
                    except Exception as e:
                        self.logger.warning(f"Failed to draw daily icon: {e}")
                
                # Draw temperatures
                temp_text = f"{self._format_temperature(max_temp)}/{self._format_temperature(min_temp)}"
                draw.text((120, y - 5), temp_text, 
                         font=self.display_utils.get_font('small', 10), 
                         fill=self.display_utils.BLACK)
        else:
            # Show error message if no daily data
            self.display_utils.draw_text_centered(
                draw, "No daily data available", 
                start_y + height // 2, 
                self.display_utils.get_font('small', 10), 
                self.display_utils.RED
            )
    
    def _flash_led_loading(self):
        """Flash LED to indicate data loading."""
        # This would need access to the button handler's LED control
        # For now, we'll just log the action
        self.logger.debug("LED: Loading weather data...")
    
    def _flash_led_success(self):
        """Flash LED to indicate successful data fetch."""
        self.logger.debug("LED: Weather data loaded successfully")
    
    def _flash_led_error(self):
        """Flash LED to indicate error."""
        self.logger.debug("LED: Weather data fetch failed")
    
    def update_display(self):
        """Update the weather display if it's time."""
        current_time = time.time()
        
        # Check if we need to update weather data
        if (self.weather_data is None or 
            current_time - self.last_update > self.update_interval):
            
            self.logger.info("Fetching weather data...")
            self.display_utils.show_loading("Loading weather...")
            
            # Flash LED to indicate data loading
            self._flash_led_loading()
            
            # Fetch new weather data
            new_data = self._fetch_weather_data()
            if new_data:
                self.weather_data = new_data
                self.last_update = current_time
                self.logger.info("Weather data updated successfully")
                # Flash LED to indicate successful data fetch
                self._flash_led_success()
            else:
                self.logger.warning("Failed to fetch weather data, using cached data if available")
                # Flash LED to indicate error
                self._flash_led_error()
        
        # Create and display weather information
        try:
            weather_img = self._create_weather_display()
            self.inky.set_image(weather_img)
            self.inky.show()
            self.logger.debug("Weather display updated")
        except Exception as e:
            self.logger.error(f"Error in weather dashboard: {e}")
            self.display_utils.show_error(f"Weather Error:\n{str(e)}")
