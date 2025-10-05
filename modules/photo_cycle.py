"""
Photo Cycle Mode
Displays a slideshow of photos from a configured folder.
"""

import os
import time
import random
import logging
from pathlib import Path
from typing import List, Optional
from PIL import Image


class PhotoCycleMode:
    """Photo slideshow mode for the display."""
    
    def __init__(self, inky_display, config: dict, display_utils):
        """Initialize photo cycle mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.logger = logging.getLogger(__name__)
        
        # Get photo cycle configuration
        self.photo_config = config.get('photo_cycle', {})
        self.folder = Path(self.photo_config.get('folder', './data/photos'))
        self.display_time = self.photo_config.get('display_time', 10)
        self.random_order = self.photo_config.get('random_order', False)
        self.supported_formats = self.photo_config.get('supported_formats', ['jpg', 'jpeg', 'png', 'webp'])
        self.background_color = self.photo_config.get('background_color', 'white')
        
        # Photo list and current index
        self.photos = []
        self.current_index = 0
        self.last_update = 0
        
        # Load photos
        self._load_photos()
    
    def _load_photos(self):
        """Load all supported photos from the configured folder."""
        self.photos = []
        
        if not self.folder.exists():
            self.logger.warning(f"Photo folder does not exist: {self.folder}")
            return
        
        # Find all supported image files
        for ext in self.supported_formats:
            pattern = f"*.{ext}"
            self.photos.extend(self.folder.glob(pattern))
            # Also check for uppercase extensions
            pattern = f"*.{ext.upper()}"
            self.photos.extend(self.folder.glob(pattern))
        
        # Remove duplicates and sort
        self.photos = list(set(self.photos))
        self.photos.sort()
        
        if self.random_order:
            random.shuffle(self.photos)
        
        self.logger.info(f"Loaded {len(self.photos)} photos from {self.folder}")
        
        if not self.photos:
            self.logger.warning("No photos found in the specified folder")
    
    def _get_next_photo(self) -> Optional[Path]:
        """Get the next photo in the sequence."""
        if not self.photos:
            return None
        
        if self.random_order:
            return random.choice(self.photos)
        else:
            photo = self.photos[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.photos)
            return photo
    
    def _load_and_process_image(self, photo_path: Path) -> Optional[Image.Image]:
        """Load and process an image for display."""
        try:
            # Load the image
            img = Image.open(photo_path)
            
            # Convert to RGB if necessary
            if img.mode == 'RGBA':
                # Create a white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to display resolution while maintaining aspect ratio
            img = self._resize_with_aspect_ratio(img, self.inky.resolution)
            
            # Optimize for the display
            img = self.display_utils.optimize_for_display(img)
            
            return img
            
        except Exception as e:
            self.logger.error(f"Error processing image {photo_path}: {e}")
            return None
    
    def _resize_with_aspect_ratio(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """Resize image while maintaining aspect ratio."""
        target_width, target_height = target_size
        img_width, img_height = img.size
        
        # Calculate scaling factor to fit within target size
        scale_w = target_width / img_width
        scale_h = target_height / img_height
        scale = min(scale_w, scale_h)
        
        # Calculate new size
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Resize the image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new image with target size and paste the resized image in the center
        bg_color = self._get_background_color()
        new_img = Image.new('RGB', target_size, bg_color)
        
        # Calculate position to center the image
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        
        new_img.paste(img, (x, y))
        
        return new_img
    
    def _get_background_color(self) -> tuple:
        """Get background color as RGB tuple."""
        color_map = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128),
            'light_gray': (192, 192, 192),
            'dark_gray': (64, 64, 64)
        }
        
        # Handle RGB tuple format: [255, 255, 255]
        if isinstance(self.background_color, list) and len(self.background_color) == 3:
            return tuple(self.background_color)
        
        # Handle named colors
        return color_map.get(self.background_color.lower(), (255, 255, 255))
    
    def _show_no_photos_message(self):
        """Show a message when no photos are available."""
        img = self.display_utils.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        # Draw message
        font_large = self.display_utils.get_font('large', 24)
        font_medium = self.display_utils.get_font('medium', 16)
        
        self.display_utils.draw_text_centered(draw, "No Photos Found", 150, font_large, self.display_utils.BLACK)
        self.display_utils.draw_text_centered(draw, f"Folder: {self.folder}", 200, font_medium, self.display_utils.BLUE)
        self.display_utils.draw_text_centered(draw, f"Formats: {', '.join(self.supported_formats)}", 230, font_medium, self.display_utils.BLUE)
        
        try:
            self.inky.set_image(img)
            self.inky.show()
        except Exception as e:
            self.logger.error(f"Failed to show no photos message: {e}")
    
    def _show_loading_message(self):
        """Show loading message while processing image."""
        self.display_utils.show_loading("Loading Photo...")
    
    def run(self, running_flag):
        """Run the photo cycle mode."""
        self.logger.info("Starting photo cycle mode")
        
        if not self.photos:
            self._show_no_photos_message()
            # Keep showing the message until mode changes
            while running_flag:
                time.sleep(1)
            return
        
        while running_flag:
            try:
                # Get next photo
                photo_path = self._get_next_photo()
                if not photo_path:
                    self.logger.warning("No photos available")
                    time.sleep(5)
                    continue
                
                self.logger.info(f"Displaying photo: {photo_path.name}")
                
                # Show loading message
                self._show_loading_message()
                
                # Load and process the image
                img = self._load_and_process_image(photo_path)
                if img is None:
                    self.logger.error(f"Failed to process image: {photo_path}")
                    time.sleep(5)
                    continue
                
                # Display the image
                try:
                    self.inky.set_image(img)
                    self.inky.show()
                except Exception as e:
                    self.logger.error(f"Failed to display image: {e}")
                    continue
                
                # Wait for the specified display time
                start_time = time.time()
                while running_flag and (time.time() - start_time) < self.display_time:
                    time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in photo cycle mode: {e}")
                time.sleep(5)
        
        self.logger.info("Photo cycle mode stopped")
