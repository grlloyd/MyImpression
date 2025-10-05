"""
Solar Monitor Mode - Placeholder
Will be implemented later.
"""

import logging
from typing import Any


class SolarMonitorMode:
    """Solar monitor mode - placeholder for future implementation."""
    
    def __init__(self, inky_display, config: dict, display_utils, main_app=None):
        """Initialize solar monitor mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.main_app = main_app  # Reference to main app for mode switching
        self.logger = logging.getLogger(__name__)
    
    def run(self, running_flag):
        """Run solar monitor mode."""
        self.logger.info("Solar monitor mode - not implemented yet")
        self.display_utils.show_error("Solar Monitor\nNot implemented yet")
        
        # Keep running until mode switch or app stops
        while running_flag():
            # Check for mode switch
            if self.main_app and self.main_app.switch is not None:
                self.logger.info("Mode switch requested, exiting solar monitor")
                return
            time.sleep(1)
