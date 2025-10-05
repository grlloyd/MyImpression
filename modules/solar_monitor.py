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
    
    def update_display(self):
        """Update solar monitor display."""
        self.logger.info("Solar monitor mode - not implemented yet")
        self.display_utils.show_error("Solar Monitor\nNot implemented yet")
