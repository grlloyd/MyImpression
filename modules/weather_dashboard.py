"""
Weather Dashboard Mode - Placeholder
Will be implemented later.
"""

import logging
from typing import Any


class WeatherDashboardMode:
    """Weather dashboard mode - placeholder for future implementation."""
    
    def __init__(self, inky_display, config: dict, display_utils):
        """Initialize weather dashboard mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.logger = logging.getLogger(__name__)
    
    def run(self, running_flag):
        """Run weather dashboard mode."""
        self.logger.info("Weather dashboard mode - not implemented yet")
        self.display_utils.show_error("Weather Dashboard\nNot implemented yet")
        
        # Keep showing message until mode changes
        while running_flag:
            import time
            time.sleep(1)
