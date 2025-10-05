"""
Weather Dashboard Mode
Displays current weather and forecast using Open-Meteo API with HTML rendering.
"""

import json
import time
import logging
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from .weather_icons import WeatherIconManager
from .html_weather_renderer import HTMLWeatherRenderer, FallbackHTMLWeatherRenderer


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
        
        # Initialize HTML renderer
        try:
            self.html_renderer = HTMLWeatherRenderer()
            self.logger.info("HTML weather renderer initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize HTML renderer, using fallback: {e}")
            self.html_renderer = FallbackHTMLWeatherRenderer()
        
        # Cache for rendered images
        self.rendered_image_cache = None
        self.last_render_time = 0
    
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
        """Create the weather display using HTML rendering."""
        if not self.weather_data:
            # Show error if no data
            img = self.display_utils.create_blank_image(self.display_utils.WHITE)
            draw = ImageDraw.Draw(img)
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
        
        # Check if we have a cached rendered image
        current_time = time.time()
        if (self.rendered_image_cache and 
            current_time - self.last_render_time < 300):  # Cache for 5 minutes
            return self.rendered_image_cache
        
        # Create output directory for rendered images
        output_dir = Path("data/cache/weather")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PNG from HTML
        png_path = output_dir / "weather_dashboard.png"
        html_path = output_dir / "weather_dashboard.html"
        
        try:
            # Try to render as PNG first
            if hasattr(self.html_renderer, 'render_weather_dashboard'):
                success = self.html_renderer.render_weather_dashboard(self.weather_data, str(png_path))
                if success and png_path.exists():
                    # Load the rendered PNG
                    img = Image.open(png_path)
                    # Convert to display format if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    # Resize to display dimensions if needed
                    if img.size != (self.inky.width, self.inky.height):
                        img = img.resize((self.inky.width, self.inky.height), Image.Resampling.LANCZOS)
                    
                    # Cache the image
                    self.rendered_image_cache = img
                    self.last_render_time = current_time
                    return img
            
            # Fallback: create HTML file only
            self.logger.info("Creating HTML weather dashboard (PNG capture not available)")
            if hasattr(self.html_renderer, 'render_weather_dashboard'):
                self.html_renderer.render_weather_dashboard(self.weather_data, str(html_path))
            
            # Create a simple fallback display
            return self._create_fallback_display()
            
        except Exception as e:
            self.logger.error(f"Failed to render HTML weather dashboard: {e}")
            return self._create_fallback_display()
    
    def _create_fallback_display(self) -> Image.Image:
        """Create a simple fallback display when HTML rendering fails."""
        img = self.display_utils.create_blank_image(self.display_utils.WHITE)
        draw = ImageDraw.Draw(img)
        
        current = self.weather_data.get("current", {})
        
        # Simple current weather display
        temp = current.get("temperature_2m", 0)
        weather_code = current.get("weather_code", 0)
        weather_desc = self._get_weather_description(weather_code)
        
        # Location
        self.display_utils.draw_text_centered(
            draw, f"{self.location}", 
            20, 
            self.display_utils.get_font('medium', 16), 
            self.display_utils.BLUE
        )
        
        # Temperature
        temp_text = self._format_temperature(temp)
        self.display_utils.draw_text_centered(
            draw, temp_text, 
            self.inky.height // 2 - 20, 
            self.display_utils.get_font('large', 48), 
            self.display_utils.BLACK
        )
        
        # Weather description
        self.display_utils.draw_text_centered(
            draw, weather_desc, 
            self.inky.height // 2 + 30, 
            self.display_utils.get_font('medium', 14), 
            self.display_utils.BLACK
        )
        
        # Last updated
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
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'html_renderer') and self.html_renderer:
            self.html_renderer.close()
