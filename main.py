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
from modules.news_feed import NewsFeedMode
from modules.tumblr_rss import TumblrRSSMode
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
            "photo_cycle": PhotoCycleMode(self.inky, self.config, self.display_utils, self),
            "tumblr_rss": TumblrRSSMode(self.inky, self.config, self.display_utils, self),
            "news_feed": NewsFeedMode(self.inky, self.config, self.display_utils, self)
        }
        
        
        # Initialize button handler
        if GPIO_AVAILABLE:
            self.button_handler = ButtonHandler(self.config, self._on_button_press)
        else:
            self.button_handler = None
            print("Running without button support - use keyboard input for testing")
        
        # Current mode tracking
        self.current_mode = None
        self.switch = None  # Button number for mode switch (A=0, B=1, C=2, D=3)
        self.last_button_press = 0  # Timestamp of last button press
    
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
                "B": "tumblr_rss", 
                "C": "news_feed",
                "D": "photo_cycle"
            },
            "photo_cycle": {
                "folder": "./data/photos",
                "display_time": 10,
                "random_order": False,
                "supported_formats": ["jpg", "jpeg", "png", "webp"],
                "background_color": "white",
                "saturation": 0.5
            },
            "tumblr_rss": {
                "rss_url": "https://handsoffmydinosaur.tumblr.com/rss",
                "display_time": 300,
                "max_posts": 300,
                "update_interval": 86400,
                "background_color": "auto",
                "saturation": 1.0
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
        import time
        
        # Debounce button presses (ignore if pressed within 500ms)
        current_time = time.time()
        if current_time - self.last_button_press < 0.5:
            return
        self.last_button_press = current_time
        
        # Map button to number (A=0, B=1, C=2, D=3)
        button_map = {"A": 0, "B": 1, "C": 2, "D": 3}
        button_num = button_map.get(button)
        
        if button_num is not None:
            # Only set switch if it's different from current target
            button_modes = ["photo_cycle", "tumblr_rss", "news_feed", "photo_cycle"]
            target_mode = button_modes[button_num]
            
            if self.current_mode != target_mode:
                self.switch = button_num
                self.logger.info(f"Button {button} pressed (button #{button_num}) - switching to {target_mode}")
            else:
                self.logger.info(f"Button {button} pressed (button #{button_num}) - already in {target_mode} mode")
            
            # Flash LED to indicate button press
            if self.button_handler and hasattr(self.button_handler, '_flash_led'):
                self.button_handler._flash_led(0.3)
        else:
            self.logger.warning(f"Unknown button: {button}")
    
    def switch_mode(self, mode_name: str):
        """Switch to a different display mode."""
        if mode_name not in self.modes:
            self.logger.error(f"Unknown mode: {mode_name}")
            return
        
        # If switching to the same mode, do nothing
        if self.current_mode == mode_name:
            self.logger.info(f"Already in {mode_name} mode")
            return
        
        # Update current mode
        self.current_mode = mode_name
        self.logger.info(f"Switched to mode: {mode_name}")
        
        # Flash LED to indicate mode change
        self._indicate_mode_change(mode_name)
    
    def _indicate_mode_change(self, mode_name: str):
        """Flash LED with different patterns for different modes."""
        if not self.button_handler or not hasattr(self.button_handler, '_flash_led'):
            return
        
        # Different LED patterns for different modes
        mode_patterns = {
            "photo_cycle": 1,    # 1 flash
            "tumblr_rss": 2,     # 2 flashes
            "news_feed": 3       # 3 flashes
        }
        
        flash_count = mode_patterns.get(mode_name, 1)
        
        # Flash the LED in a separate thread to avoid blocking
        def flash_pattern():
            for _ in range(flash_count):
                self.button_handler._flash_led(0.2)  # 200ms flash
                time.sleep(0.1)  # 100ms pause between flashes
        
        threading.Thread(target=flash_pattern, daemon=True).start()
    
    def check_and_switch_mode(self):
        """Check if mode switch is needed and execute it."""
        if self.switch is not None:
            # Map button number to mode name
            button_modes = ["photo_cycle", "tumblr_rss", "news_feed", "photo_cycle"]
            target_mode = button_modes[self.switch]
            
            # Switch to the target mode
            self.switch_mode(target_mode)
            
            # Reset switch flag
            self.switch = None
            return True
        return False
    
    def run_current_mode(self):
        """Run the current mode's display update."""
        if self.current_mode and self.current_mode in self.modes:
            try:
                mode = self.modes[self.current_mode]
                mode.update_display()
            except Exception as e:
                self.logger.error(f"Error in mode {self.current_mode}: {e}")
                # Show error display
                self.display_utils.show_error(f"Error in {self.current_mode}: {str(e)}")
    
    def start(self):
        """Start the application."""
        self.logger.info("Starting MyImpression application")
        
        # Set the application as running
        self.running = True
        
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
            while self.running:
                # Check for mode switches
                self.check_and_switch_mode()
                
                # Run current mode's display update
                self.run_current_mode()
                
                time.sleep(0.1)  # Check every 100ms
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            self.stop()
    
    def stop(self):
        """Stop the application."""
        self.running = False
        if self.button_handler:
            self.button_handler.stop()
        self.logger.info("Application stopped")


def main():
    """Main entry point."""
    app = MyImpressionApp()
    app.start()


if __name__ == "__main__":
    main()
