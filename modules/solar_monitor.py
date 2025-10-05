"""
Solar Monitor Mode - Placeholder
Will be implemented later.
"""

import logging
from typing import Any


class SolarMonitorMode:
    """Solar monitor mode - placeholder for future implementation."""
    
    def __init__(self, inky_display, config: dict, display_utils):
        """Initialize solar monitor mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.logger = logging.getLogger(__name__)
    
    def run(self, running_flag):
        """Run solar monitor mode."""
        self.logger.info("Solar monitor mode - not implemented yet")
        self.display_utils.show_error("Solar Monitor\nNot implemented yet")
        
        # Keep showing message until mode changes
        while running_flag:
            import time
            time.sleep(1)
