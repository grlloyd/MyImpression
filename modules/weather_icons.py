"""
Weather Icon Management System
Handles downloading, caching, and mapping weather codes to icons.
"""

import os
import requests
import logging
from pathlib import Path
from typing import Dict, Optional
from PIL import Image
import hashlib


class WeatherIconManager:
    """Manages weather icons with caching and mapping."""
    
    def __init__(self, cache_dir: str = "assets/icons/weather"):
        """Initialize the weather icon manager."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Weather code to icon mapping
        self.weather_icon_map = {
            # Clear sky
            0: "sun",
            
            # Mainly clear, partly cloudy, overcast
            1: "sun",
            2: "partly-cloudy", 
            3: "cloudy",
            
            # Fog
            45: "fog",
            48: "fog",
            
            # Drizzle
            51: "drizzle",
            53: "drizzle", 
            55: "drizzle",
            56: "drizzle",
            57: "drizzle",
            
            # Rain
            61: "rain",
            63: "rain",
            65: "rain",
            66: "rain",
            67: "rain",
            
            # Snow
            71: "snow",
            73: "snow",
            75: "snow",
            77: "snow",
            
            # Rain showers
            80: "rain",
            81: "rain",
            82: "rain",
            
            # Snow showers
            85: "snow",
            86: "snow",
            
            # Thunderstorm
            95: "thunderstorm",
            96: "thunderstorm",
            99: "thunderstorm"
        }
        
        # Icon URLs from Flaticon weather pack
        self.icon_urls = {
            "sun": "https://cdn-icons-png.flaticon.com/512/3222/3222807.png",
            "partly-cloudy": "https://cdn-icons-png.flaticon.com/512/3222/3222808.png", 
            "cloudy": "https://cdn-icons-png.flaticon.com/512/3222/3222809.png",
            "fog": "https://cdn-icons-png.flaticon.com/512/3222/3222810.png",
            "drizzle": "https://cdn-icons-png.flaticon.com/512/3222/3222811.png",
            "rain": "https://cdn-icons-png.flaticon.com/512/3222/3222812.png",
            "snow": "https://cdn-icons-png.flaticon.com/512/3222/3222813.png",
            "thunderstorm": "https://cdn-icons-png.flaticon.com/512/3222/3222814.png"
        }
        
        # Default icon (fallback)
        self.default_icon = "sun"
    
    def get_icon_for_weather_code(self, weather_code: int) -> str:
        """Get icon name for weather code."""
        return self.weather_icon_map.get(weather_code, self.default_icon)
    
    def _get_icon_path(self, icon_name: str) -> Path:
        """Get local path for cached icon."""
        return self.cache_dir / f"{icon_name}.png"
    
    def _download_icon(self, icon_name: str) -> bool:
        """Download icon from URL and cache it."""
        if icon_name not in self.icon_urls:
            self.logger.warning(f"No URL for icon: {icon_name}")
            return False
        
        icon_path = self._get_icon_path(icon_name)
        if icon_path.exists():
            return True  # Already cached
        
        try:
            self.logger.info(f"Downloading icon: {icon_name}")
            url = self.icon_urls[icon_name]
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Save the icon
            with open(icon_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Cached icon: {icon_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download icon {icon_name}: {e}")
            return False
    
    def get_icon_image(self, weather_code: int, size: tuple = (32, 32)) -> Optional[Image.Image]:
        """Get weather icon as PIL Image."""
        icon_name = self.get_icon_for_weather_code(weather_code)
        
        # Try to get cached icon
        icon_path = self._get_icon_path(icon_name)
        
        if not icon_path.exists():
            # Try to download it
            if not self._download_icon(icon_name):
                # Fallback to default
                icon_name = self.default_icon
                icon_path = self._get_icon_path(icon_name)
                
                if not icon_path.exists():
                    if not self._download_icon(icon_name):
                        return None
        
        try:
            # Load and resize the icon
            icon = Image.open(icon_path)
            icon = icon.convert('RGBA')
            icon = icon.resize(size, Image.Resampling.LANCZOS)
            return icon
        except Exception as e:
            self.logger.error(f"Failed to load icon {icon_path}: {e}")
            return None
    
    def preload_icons(self):
        """Preload all weather icons."""
        self.logger.info("Preloading weather icons...")
        for icon_name in self.icon_urls.keys():
            self._download_icon(icon_name)
        self.logger.info("Weather icons preloaded")
    
    def clear_cache(self):
        """Clear the icon cache."""
        try:
            for icon_file in self.cache_dir.glob("*.png"):
                icon_file.unlink()
            self.logger.info("Icon cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear icon cache: {e}")
    
    def get_cache_size(self) -> int:
        """Get the size of the icon cache in bytes."""
        total_size = 0
        for icon_file in self.cache_dir.glob("*.png"):
            total_size += icon_file.stat().st_size
        return total_size
