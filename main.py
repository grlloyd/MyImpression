#!/usr/bin/env python3
"""
MyImpression - 4-Mode Display System for 6-Color Inky Impression
Main application entry point with button handling and mode switching.
"""

import json
import time
import threading
import logging
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import gpiod
    import gpiodevice
    from gpiod.line import Bias, Direction, Edge
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: GPIO libraries not available. Running in simulation mode.")

from inky.auto import auto

# Import our modules
from modules.button_handler import ButtonHandler
from modules.photo_cycle import PhotoCycleMode
from modules.weather_dashboard import WeatherDashboardMode
from modules.solar_monitor import SolarMonitorMode
from modules.news_feed import NewsFeedMode
from modules.display_utils import DisplayUtils


class MyImpressionApp:
    """Main application class for the 4-mode display system."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the application with configuration."""
        self.config_path = Path(config_path)
        self.running = False
        
        # Setup logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration after logger is set up
        self.config = self._load_config()
        
        # Initialize display
        try:
            self.inky = auto(ask_user=False, verbose=True)
            print(f"Display initialized: {self.inky.resolution}")
        except Exception as e:
            print(f"Failed to initialize display: {e}")
            raise
        
        # Initialize display utilities
        self.display_utils = DisplayUtils(self.inky, self.config)
        
        # Initialize modes
        self.modes = {
            "photo_cycle": PhotoCycleMode(self.inky, self.config, self.display_utils),
            "weather": WeatherDashboardMode(self.inky, self.config, self.display_utils),
            "solar_monitor": SolarMonitorMode(self.inky, self.config, self.display_utils),
            "news_feed": NewsFeedMode(self.inky, self.config, self.display_utils)
        }
        
        # Initialize button handler
        if GPIO_AVAILABLE:
            self.button_handler = ButtonHandler(self.config, self._on_button_press)
        else:
            self.button_handler = None
            print("Running without button support - use keyboard input for testing")
        
        # Current mode
        self.current_mode = None
        self.mode_thread = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _create_default_config(self):
        """Create default configuration file."""
        default_config = self._get_default_config()
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        self.logger.info(f"Created default configuration at {self.config_path}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "display": {
                "resolution": [800, 480],
                "dpi": 127,
                "colors": 6,
                "refresh_rate": 30
            },
            "buttons": {
                "A": "photo_cycle",
                "B": "weather", 
                "C": "solar_monitor",
                "D": "news_feed"
            },
            "photo_cycle": {
                "folder": "./data/photos",
                "display_time": 10,
                "random_order": False,
                "supported_formats": ["jpg", "jpeg", "png", "webp"],
                "background_color": "white",
                "saturation": 0.5
            },
            "weather": {
                "latitude": 51.5085300,
                "longitude": -0.1257400,
                "location": "London, UK",
                "units": "metric",
                "update_interval": 1800
            },
            "solar_monitor": {
                "api_endpoint": "https://monitoringapi.solaredge.com",
                "site_id": "your_site_id",
                "api_key": "your_solaredge_key",
                "update_interval": 300
            },
            "news_feed": {
                "sources": ["arxiv"],
                "search_terms": ["machine learning", "renewable energy"],
                "max_articles": 5,
                "update_interval": 86400
            }
        }
    
    def _on_button_press(self, button: str):
        """Handle button press events."""
        mode_name = self.config["buttons"].get(button)
        if mode_name and mode_name in self.modes:
            self.logger.info(f"Button {button} pressed - switching to {mode_name}")
            self.switch_mode(mode_name)
        else:
            self.logger.warning(f"No mode configured for button {button}")
    
    def switch_mode(self, mode_name: str):
        """Switch to a different display mode."""
        if mode_name not in self.modes:
            self.logger.error(f"Unknown mode: {mode_name}")
            return
        
        # Stop current mode
        if self.current_mode and self.mode_thread:
            self.logger.info(f"Stopping current mode: {self.current_mode}")
            self.running = False
            if self.mode_thread.is_alive():
                self.mode_thread.join(timeout=5)
        
        # Start new mode
        self.current_mode = mode_name
        self.running = True
        self.mode_thread = threading.Thread(
            target=self._run_mode,
            args=(mode_name,),
            daemon=True
        )
        self.mode_thread.start()
        self.logger.info(f"Started mode: {mode_name}")
    
    def _run_mode(self, mode_name: str):
        """Run the specified mode in a separate thread."""
        try:
            mode = self.modes[mode_name]
            mode.run(self.running)
        except Exception as e:
            self.logger.error(f"Error in mode {mode_name}: {e}")
            # Show error display
            self.display_utils.show_error(f"Error in {mode_name}: {str(e)}")
    
    def start(self):
        """Start the application."""
        self.logger.info("Starting MyImpression application")
        
        # Create necessary directories
        Path("data/photos").mkdir(parents=True, exist_ok=True)
        Path("data/cache").mkdir(parents=True, exist_ok=True)
        Path("assets/fonts").mkdir(parents=True, exist_ok=True)
        Path("assets/icons").mkdir(parents=True, exist_ok=True)
        
        # Start button handler
        if self.button_handler:
            self.button_handler.start()
        
        # Start with photo cycle mode
        self.switch_mode("photo_cycle")
        
        try:
            # Main loop
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            self.stop()
    
    def stop(self):
        """Stop the application."""
        self.running = False
        if self.mode_thread and self.mode_thread.is_alive():
            self.mode_thread.join(timeout=5)
        if self.button_handler:
            self.button_handler.stop()
        self.logger.info("Application stopped")


def main():
    """Main entry point."""
    app = MyImpressionApp()
    app.start()


if __name__ == "__main__":
    main()
