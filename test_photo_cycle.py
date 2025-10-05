#!/usr/bin/env python3
"""
Test script for photo cycle mode
Run this to test the photo cycle functionality without hardware.
"""

import sys
import time
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from modules.photo_cycle import PhotoCycleMode
from modules.display_utils import DisplayUtils

# Mock display for testing
class MockInky:
    def __init__(self):
        self.resolution = (800, 480)
        self.BLACK = 0
        self.WHITE = 1
        self.GREEN = 2
        self.BLUE = 3
        self.RED = 4
        self.YELLOW = 5
    
    def set_image(self, img):
        print(f"Displaying image: {img.size}")
    
    def show(self):
        print("Updating display...")

def test_photo_cycle():
    """Test the photo cycle mode."""
    print("Testing Photo Cycle Mode")
    print("=" * 40)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create mock display
    mock_inky = MockInky()
    
    # Create test configuration
    config = {
        'photo_cycle': {
            'folder': './data/photos',
            'display_time': 3,  # 3 seconds for testing
            'random_order': False,
            'supported_formats': ['jpg', 'jpeg', 'png', 'webp']
        }
    }
    
    # Create display utils
    display_utils = DisplayUtils(mock_inky, config)
    
    # Create photo cycle mode
    photo_mode = PhotoCycleMode(mock_inky, config, display_utils)
    
    print(f"Photos found: {len(photo_mode.photos)}")
    for photo in photo_mode.photos[:5]:  # Show first 5 photos
        print(f"  - {photo.name}")
    
    if len(photo_mode.photos) > 5:
        print(f"  ... and {len(photo_mode.photos) - 5} more")
    
    if not photo_mode.photos:
        print("No photos found. Please add some photos to ./data/photos/")
        return
    
    print("\nStarting photo cycle (press Ctrl+C to stop)...")
    
    # Run photo cycle for a few iterations
    running = True
    try:
        photo_mode.run(running)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_photo_cycle()
