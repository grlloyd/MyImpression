#!/usr/bin/env python3
"""
Test script for Twonks Comic mode
Tests the comic RSS feed functionality without requiring the full display setup.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the inky display for testing
class MockInky:
    def __init__(self):
        self.resolution = (800, 480)
    
    def set_image(self, img, saturation=None):
        print(f"Mock: Setting image with saturation={saturation}")
    
    def show(self):
        print("Mock: Displaying image")

# Mock display utils
class MockDisplayUtils:
    def __init__(self):
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
    
    def create_image_with_palette(self):
        from PIL import Image
        return Image.new('RGB', (800, 480), (255, 255, 255))
    
    def get_font(self, size, font_size):
        return None
    
    def draw_text_centered(self, draw, text, y, font, color):
        print(f"Mock: Drawing text '{text}' at y={y}")
    
    def resize_with_aspect_ratio(self, img, resolution, fill_screen=False, auto_rotate=False, bg_color=(255, 255, 255)):
        print(f"Mock: Resizing image to {resolution}, fill_screen={fill_screen}")
        return img

def test_twonks_comic():
    """Test the Twonks comic mode."""
    print("Testing Twonks Comic Mode...")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create mock objects
    mock_inky = MockInky()
    mock_display_utils = MockDisplayUtils()
    
    # Test configuration
    config = {
        'twonks_comic': {
            'rss_url': 'https://fetchrss.com/feed/aPqdPwCxq2JyaPqdK5gClBE1.rss',
            'display_time': 5,  # Short display time for testing
            'max_posts': 5,
            'update_interval': 60,  # Short update interval for testing
            'background_color': 'white',
            'saturation': 0.8,
            'fill_screen': True,
            'auto_rotate': False
        }
    }
    
    try:
        # Import and test the comic mode
        from modules.twonks_comic import TwonksComicMode
        
        # Initialize the comic mode
        comic_mode = TwonksComicMode(mock_inky, config, mock_display_utils)
        
        print(f"✓ Comic mode initialized successfully")
        print(f"✓ RSS URL: {comic_mode.rss_url}")
        print(f"✓ Display time: {comic_mode.display_time} seconds")
        print(f"✓ Max posts: {comic_mode.max_posts}")
        
        # Test fetching images
        print("\nTesting RSS feed fetching...")
        comic_mode._fetch_rss_images()
        
        if comic_mode.cached_images:
            print(f"✓ Successfully fetched {len(comic_mode.cached_images)} comic images")
            
            # Test getting next image
            image_data = comic_mode._get_next_image()
            if image_data:
                print(f"✓ Next image: {image_data['post_title']}")
                print(f"✓ Image URL: {image_data['url']}")
            else:
                print("✗ No image data available")
        else:
            print("✗ No images found in RSS feed")
        
        # Test display update
        print("\nTesting display update...")
        comic_mode.update_display()
        print("✓ Display update completed")
        
        print("\n🎉 Twonks Comic mode test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error testing comic mode: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_twonks_comic()
