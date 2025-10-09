"""
Tumblr Feed Mode
Displays images from a Tumblr blog feed using the Tumblr API.
"""

import time
import random
import logging
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image, ImageDraw
import io


class TumblrFeedMode:
    """Tumblr feed mode for displaying images from a Tumblr blog."""
    
    def __init__(self, inky_display, config: dict, display_utils, main_app=None):
        """Initialize Tumblr feed mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.main_app = main_app  # Reference to main app for mode switching
        self.logger = logging.getLogger(__name__)
        
        # Get Tumblr configuration
        self.tumblr_config = config.get('tumblr_feed', {})
        self.api_key = self.tumblr_config.get('api_key', '')
        self.blog_name = self.tumblr_config.get('blog_name', 'handsoffmydinosaur')
        self.display_time = self.tumblr_config.get('display_time', 15)
        self.max_posts = self.tumblr_config.get('max_posts', 20)
        self.update_interval = self.tumblr_config.get('update_interval', 3600)  # 1 hour
        self.background_color = self.tumblr_config.get('background_color', 'white')
        self.saturation = self.tumblr_config.get('saturation', 0.5)
        
        # Image cache and current state
        self.cached_images = []
        self.current_index = 0
        self.last_update = 0
        self.last_fetch = 0
        
        # Cache directory
        self.cache_dir = Path("data/cache/tumblr")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load initial images
        self._fetch_tumblr_images()
    
    def _fetch_tumblr_images(self):
        """Fetch images from Tumblr API."""
        if not self.api_key:
            self.logger.error("Tumblr API key not configured")
            return
        
        current_time = time.time()
        
        # Check if we need to fetch new images
        if current_time - self.last_fetch < self.update_interval and self.cached_images:
            self.logger.info("Using cached Tumblr images")
            return
        
        self.logger.info(f"Fetching images from Tumblr blog: {self.blog_name}")
        
        try:
            # Construct API URL
            api_url = f"https://api.tumblr.com/v2/blog/{self.blog_name}.tumblr.com/posts/photo"
            params = {
                'api_key': self.api_key,
                'limit': self.max_posts,
                'offset': 0
            }
            
            # Make API request
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'response' not in data or 'posts' not in data['response']:
                self.logger.error("Invalid Tumblr API response")
                return
            
            posts = data['response']['posts']
            self.logger.info(f"Retrieved {len(posts)} posts from Tumblr")
            
            # Extract image URLs from posts
            new_images = []
            for post in posts:
                if 'photos' in post:
                    for photo in post['photos']:
                        if 'original_size' in photo and 'url' in photo['original_size']:
                            image_url = photo['original_size']['url']
                            new_images.append({
                                'url': image_url,
                                'post_id': post.get('id', ''),
                                'timestamp': post.get('timestamp', 0)
                            })
            
            if new_images:
                self.cached_images = new_images
                self.current_index = 0
                self.last_fetch = current_time
                self.logger.info(f"Cached {len(self.cached_images)} images from Tumblr")
            else:
                self.logger.warning("No images found in Tumblr posts")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch Tumblr images: {e}")
        except Exception as e:
            self.logger.error(f"Error processing Tumblr API response: {e}")
    
    def _download_image(self, image_url: str) -> Optional[Image.Image]:
        """Download and process an image from URL."""
        try:
            # Check cache first
            cache_filename = f"{hash(image_url)}.jpg"
            cache_path = self.cache_dir / cache_filename
            
            if cache_path.exists():
                self.logger.debug(f"Loading cached image: {cache_filename}")
                return Image.open(cache_path)
            
            # Download image
            self.logger.debug(f"Downloading image: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Load image from bytes
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode == 'RGBA':
                # Create a white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Cache the image
            try:
                img.save(cache_path, 'JPEG', quality=85)
            except Exception as e:
                self.logger.warning(f"Failed to cache image: {e}")
            
            return img
            
        except Exception as e:
            self.logger.error(f"Failed to download image {image_url}: {e}")
            return None
    
    def _get_next_image(self) -> Optional[Dict[str, Any]]:
        """Get the next image in the sequence."""
        if not self.cached_images:
            return None
        
        image_data = self.cached_images[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.cached_images)
        return image_data
    
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
    
    def _show_no_images_message(self):
        """Show a message when no images are available."""
        img = self.display_utils.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        # Draw message
        font_large = self.display_utils.get_font('large', 24)
        font_medium = self.display_utils.get_font('medium', 16)
        
        self.display_utils.draw_text_centered(draw, "No Tumblr Images", 150, font_large, self.display_utils.BLACK)
        self.display_utils.draw_text_centered(draw, f"Blog: {self.blog_name}", 200, font_medium, self.display_utils.BLUE)
        self.display_utils.draw_text_centered(draw, "Check API key and connection", 230, font_medium, self.display_utils.BLUE)
        
        try:
            self.inky.set_image(img)
            self.inky.show()
        except Exception as e:
            self.logger.error(f"Failed to show no images message: {e}")
    
    def _show_loading_message(self):
        """Show a loading message while fetching images."""
        img = self.display_utils.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        # Draw message
        font_large = self.display_utils.get_font('large', 24)
        font_medium = self.display_utils.get_font('medium', 16)
        
        self.display_utils.draw_text_centered(draw, "Loading Tumblr Images", 150, font_large, self.display_utils.BLACK)
        self.display_utils.draw_text_centered(draw, f"From: {self.blog_name}", 200, font_medium, self.display_utils.BLUE)
        self.display_utils.draw_text_centered(draw, "Please wait...", 230, font_medium, self.display_utils.BLUE)
        
        try:
            self.inky.set_image(img)
            self.inky.show()
        except Exception as e:
            self.logger.error(f"Failed to show loading message: {e}")
    
    def update_display(self):
        """Update the display with the next image if it's time."""
        current_time = time.time()
        
        # Check if it's time to update the display
        if current_time - self.last_update < self.display_time:
            return
        
        self.last_update = current_time
        
        # Try to fetch new images if needed
        if not self.cached_images or current_time - self.last_fetch >= self.update_interval:
            self._show_loading_message()
            self._fetch_tumblr_images()
        
        if not self.cached_images:
            self._show_no_images_message()
            return
        
        try:
            # Get next image
            image_data = self._get_next_image()
            if not image_data:
                self.logger.warning("No images available")
                return
            
            self.logger.info(f"Displaying Tumblr image: {image_data['url']}")
            
            # Download and process the image
            img = self._download_image(image_data['url'])
            if img is None:
                self.logger.error(f"Failed to download image: {image_data['url']}")
                return
            
            # Resize to display resolution while maintaining aspect ratio
            img = self._resize_with_aspect_ratio(img, self.inky.resolution)
            
            # Set image directly with saturation
            try:
                self.inky.set_image(img, saturation=self.saturation)
            except TypeError:
                # Fallback for older inky versions
                self.inky.set_image(img)
            
            # Display the image
            try:
                self.inky.show()
            except Exception as e:
                self.logger.error(f"Failed to display image: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in Tumblr feed mode: {e}")
