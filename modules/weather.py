"""
Weather Mode
Displays current weather, 5-day forecast, and hourly forecast using Open-Meteo API.
"""

import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

from .weather_api import WeatherAPIClient


class WeatherMode:
    """Weather display mode for the e-ink display."""
    
    def __init__(self, inky_display, config: dict, display_utils, main_app=None):
        """Initialize weather mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Get weather configuration
        self.weather_config = config.get('weather', {})
        self.display_time = self.weather_config.get('display_time', 300)  # 5 minutes
        
        # Initialize weather API client
        self.weather_api = WeatherAPIClient(config)
        
        # Weather data cache
        self.weather_data = None
        self.last_update = 0
        
        # Create assets directory
        Path("assets/icons/weather").mkdir(parents=True, exist_ok=True)
    
    def update_display(self):
        """Update the weather display."""
        current_time = time.time()
        
        # Check if we need to update the display
        if current_time - self.last_update < self.display_time:
            return
        
        try:
            # Get fresh weather data
            self.weather_data = self.weather_api.get_weather_data()
            
            if self.weather_data:
                # Generate and show weather display
                weather_img = self._generate_weather_display()
                if weather_img:
                    # Optimize for display
                    optimized_img = self.display_utils.optimize_for_display(weather_img)
                    
                    # Show on display
                    self.inky.set_image(optimized_img)
                    self.inky.show()
                    
                    self.last_update = current_time
                    self.logger.info("Weather display updated successfully")
            else:
                self.logger.warning("No weather data available")
                self.display_utils.show_error("Weather data unavailable")
                
        except Exception as e:
            self.logger.error(f"Weather display error: {e}")
            self.display_utils.show_error(f"Weather Error: {str(e)}")
    
    def _generate_weather_display(self) -> Optional[Image.Image]:
        """Generate the weather display image."""
        if not self.weather_data:
            return None
        
        # Create base image with proper color palette
        img = self.display_utils.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        # Draw top half (today's weather + 5-day forecast)
        self._draw_top_half(draw, img)
        
        # Draw bottom half (hourly forecast)
        self._draw_bottom_half(draw, img)
        
        return img
    
    def _draw_top_half(self, draw: ImageDraw.Draw, img: Image.Image):
        """Draw the top half of the display (today + 5-day forecast)."""
        # Top half dimensions: 800x400
        top_height = 400
        
        # Draw separator line
        draw.line([(0, top_height), (800, top_height)], fill=self.display_utils.BLACK, width=2)
        
        # Draw today's weather (left side)
        self._draw_todays_weather(draw, img)
        
        # Draw 5-day forecast (right side)
        self._draw_five_day_forecast(draw, img)
    
    def _draw_todays_weather(self, draw: ImageDraw.Draw, img: Image.Image):
        """Draw today's weather section (left side)."""
        current = self.weather_data['current']
        
        # Today's weather area: 0-320px width, 0-400px height
        today_width = 320
        today_height = 400
        
        # Draw weather icon (large, 80x80)
        weather_icon = self._get_weather_icon(current['weather_code'], size=80)
        if weather_icon:
            icon_x = (today_width - 80) // 2
            icon_y = 60
            img.paste(weather_icon, (icon_x, icon_y))
        
        # Draw temperature (large font)
        temp_text = f"{current['temperature']}°C"
        font_large = self.display_utils.get_font('large', 48)
        self.display_utils.draw_text_centered(draw, temp_text, 180, font_large, self.display_utils.BLACK)
        
        # Draw conditions text
        conditions = self.weather_api.get_weather_description(current['weather_code'])
        font_medium = self.display_utils.get_font('medium', 18)
        self.display_utils.draw_text_centered(draw, conditions, 240, font_medium, self.display_utils.BLUE)
        
        # Draw "TODAY" label
        font_small = self.display_utils.get_font('small', 14)
        self.display_utils.draw_text_centered(draw, "TODAY", 20, font_small, self.display_utils.BLACK)
        
        # Draw vertical separator line
        draw.line([(today_width, 0), (today_width, today_height)], fill=self.display_utils.BLACK, width=1)
    
    def _draw_five_day_forecast(self, draw: ImageDraw.Draw, img: Image.Image):
        """Draw 5-day forecast section (right side)."""
        daily_forecast = self.weather_data['daily']
        
        # 5-day forecast area: 320-800px width, 0-400px height
        forecast_start_x = 340
        forecast_width = 460
        day_width = forecast_width // 5  # 92px per day
        
        # Draw "5-DAY FORECAST" label
        font_small = self.display_utils.get_font('small', 14)
        self.display_utils.draw_text_centered(draw, "5-DAY FORECAST", 20, font_small, self.display_utils.BLACK)
        
        for i, day in enumerate(daily_forecast[:5]):
            x = forecast_start_x + (i * day_width)
            
            # Draw day name
            day_name = self.weather_api.get_day_name(day['time'])
            self.display_utils.draw_text_centered(draw, day_name, 50, font_small, self.display_utils.BLACK)
            
            # Draw weather icon (50x50)
            weather_icon = self._get_weather_icon(day['weather_code'], size=50)
            if weather_icon:
                icon_x = x + (day_width - 50) // 2
                icon_y = 80
                img.paste(weather_icon, (icon_x, icon_y))
            
            # Draw high temperature
            high_temp = f"{day['temp_max']}°"
            font_medium = self.display_utils.get_font('medium', 16)
            self.display_utils.draw_text_centered(draw, high_temp, 150, font_medium, self.display_utils.RED)
            
            # Draw low temperature
            low_temp = f"{day['temp_min']}°"
            self.display_utils.draw_text_centered(draw, low_temp, 180, font_medium, self.display_utils.BLUE)
            
            # Draw vertical separator between days
            if i < 4:  # Don't draw after the last day
                draw.line([(x + day_width, 40), (x + day_width, 200)], fill=self.display_utils.BLACK, width=1)
    
    def _draw_bottom_half(self, draw: ImageDraw.Draw, img: Image.Image):
        """Draw the bottom half of the display (hourly forecast)."""
        hourly_forecast = self.weather_data['hourly']
        
        # Bottom half dimensions: 800x80
        bottom_y = 400
        bottom_height = 80
        
        # Draw "HOURLY FORECAST" label
        font_small = self.display_utils.get_font('small', 12)
        self.display_utils.draw_text_centered(draw, "HOURLY FORECAST", bottom_y + 5, font_small, self.display_utils.BLACK)
        
        # Calculate hourly display parameters
        max_hours = 12
        hour_width = 60
        start_x = 20
        
        for i, hour in enumerate(hourly_forecast[:max_hours]):
            x = start_x + (i * hour_width)
            
            # Draw time
            time_text = self.weather_api.format_hour(hour['time'])
            font_tiny = self.display_utils.get_font('small', 10)
            self.display_utils.draw_text_centered(draw, time_text, bottom_y + 20, font_tiny, self.display_utils.BLACK)
            
            # Draw weather icon (30x30)
            weather_icon = self._get_weather_icon(hour['weather_code'], size=30)
            if weather_icon:
                icon_x = x + (hour_width - 30) // 2
                icon_y = bottom_y + 35
                img.paste(weather_icon, (icon_x, icon_y))
            
            # Draw temperature
            temp_text = f"{hour['temperature']}°"
            self.display_utils.draw_text_centered(draw, temp_text, bottom_y + 70, font_tiny, self.display_utils.BLACK)
    
    def _get_weather_icon(self, weather_code: int, size: int = 40) -> Optional[Image.Image]:
        """Generate weather icon based on weather code."""
        try:
            # Create icon with proper palette
            icon = Image.new('P', (size, size), self.display_utils.WHITE)
            draw = ImageDraw.Draw(icon)
            
            # Set palette
            icon.putpalette(self.display_utils.create_image_with_palette().getpalette())
            
            center = size // 2
            radius = size // 4
            
            if weather_code in [0, 1]:  # Clear/Sunny
                # Draw sun (circle + rays)
                draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                           fill=self.display_utils.YELLOW, outline=self.display_utils.BLACK)
                
                # Draw sun rays
                ray_length = radius + 5
                for angle in range(0, 360, 45):
                    import math
                    rad = math.radians(angle)
                    x1 = center + radius * math.cos(rad)
                    y1 = center + radius * math.sin(rad)
                    x2 = center + ray_length * math.cos(rad)
                    y2 = center + ray_length * math.sin(rad)
                    draw.line([(x1, y1), (x2, y2)], fill=self.display_utils.YELLOW, width=2)
            
            elif weather_code in [2, 3]:  # Partly cloudy/Overcast
                # Draw cloud
                self._draw_cloud(draw, center, radius, self.display_utils.BLUE)
                
                if weather_code == 2:  # Partly cloudy - add sun
                    sun_radius = radius // 2
                    draw.ellipse([center-sun_radius-10, center-sun_radius-10, 
                                center+sun_radius-10, center+sun_radius-10], 
                               fill=self.display_utils.YELLOW, outline=self.display_utils.BLACK)
            
            elif weather_code in [45, 48]:  # Fog
                # Draw wavy fog lines
                for i in range(3):
                    y = center - 5 + i * 5
                    draw.line([(center-radius, y), (center+radius, y)], 
                            fill=self.display_utils.BLUE, width=2)
            
            elif weather_code in range(51, 68):  # Rain
                # Draw cloud + rain drops
                self._draw_cloud(draw, center, radius, self.display_utils.BLUE)
                self._draw_rain(draw, center, radius)
            
            elif weather_code in range(71, 78):  # Snow
                # Draw cloud + snow
                self._draw_cloud(draw, center, radius, self.display_utils.BLUE)
                self._draw_snow(draw, center, radius)
            
            elif weather_code in range(80, 87):  # Rain showers
                # Draw cloud + heavy rain
                self._draw_cloud(draw, center, radius, self.display_utils.BLUE)
                self._draw_rain(draw, center, radius, heavy=True)
            
            elif weather_code in range(95, 100):  # Thunderstorm
                # Draw cloud + lightning
                self._draw_cloud(draw, center, radius, self.display_utils.BLUE)
                self._draw_lightning(draw, center, radius)
            
            else:  # Unknown weather
                # Draw question mark
                font = self.display_utils.get_font('medium', size//2)
                draw.text((center-size//4, center-size//4), "?", font=font, fill=self.display_utils.BLACK)
            
            return icon
            
        except Exception as e:
            self.logger.error(f"Error creating weather icon: {e}")
            return None
    
    def _draw_cloud(self, draw: ImageDraw.Draw, center_x: int, radius: int, color: int):
        """Draw a cloud shape."""
        # Main cloud body
        draw.ellipse([center_x-radius, center_x-radius//2, center_x+radius, center_x+radius//2], 
                    fill=color, outline=self.display_utils.BLACK)
        
        # Cloud bumps
        bump_radius = radius // 2
        draw.ellipse([center_x-radius//2, center_x-radius, center_x+radius//2, center_x], 
                    fill=color, outline=self.display_utils.BLACK)
        draw.ellipse([center_x-radius//4, center_x-radius//2, center_x+radius//4, center_x+radius//4], 
                    fill=color, outline=self.display_utils.BLACK)
    
    def _draw_rain(self, draw: ImageDraw.Draw, center_x: int, radius: int, heavy: bool = False):
        """Draw rain drops."""
        drop_count = 8 if heavy else 5
        for i in range(drop_count):
            x = center_x - radius//2 + (i * radius//drop_count)
            y_start = center_x + radius//2
            y_end = y_start + radius//2
            draw.line([(x, y_start), (x, y_end)], fill=self.display_utils.BLUE, width=1)
    
    def _draw_snow(self, draw: ImageDraw.Draw, center_x: int, radius: int):
        """Draw snowflakes."""
        import math
        for i in range(6):
            x = center_x - radius//2 + (i * radius//6)
            y = center_x + radius//2 + 5
            
            # Simple snowflake (star shape)
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                x1 = x + 3 * math.cos(rad)
                y1 = y + 3 * math.sin(rad)
                draw.line([(x, y), (x1, y1)], fill=self.display_utils.WHITE, width=1)
    
    def _draw_lightning(self, draw: ImageDraw.Draw, center_x: int, radius: int):
        """Draw lightning bolt."""
        # Simple lightning bolt
        points = [
            (center_x, center_x + radius//2),
            (center_x - 3, center_x + radius//2 + 5),
            (center_x + 3, center_x + radius//2 + 5),
            (center_x, center_x + radius//2 + 10)
        ]
        draw.polygon(points, fill=self.display_utils.YELLOW, outline=self.display_utils.BLACK)
