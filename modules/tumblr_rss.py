"""
Tumblr RSS Feed Mode
Displays images from a Tumblr blog RSS feed (no API key required).
"""

import time
import random
import logging
import requests
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image, ImageDraw
import io
import xml.etree.ElementTree as ET


class TumblrRSSMode:
    """Tumblr RSS feed mode for displaying images from a Tumblr blog RSS feed."""
    
    def __init__(self, inky_display, config: dict, display_utils, main_app=None):
        """Initialize Tumblr RSS feed mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.main_app = main_app  # Reference to main app for mode switching
        self.logger = logging.getLogger(__name__)
        
        # Get Tumblr RSS configuration
        self.tumblr_config = config.get('tumblr_rss', {})
        self.rss_url = self.tumblr_config.get('rss_url', 'https://handsoffmydinosaur.tumblr.com/rss')
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
        self.cache_dir = Path("data/cache/tumblr_rss")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load initial images
        self._fetch_rss_images()
    
    def _fetch_rss_images(self):
        """Fetch images from Tumblr RSS feed."""
        current_time = time.time()
        
        # Check if we need to fetch new images
        if current_time - self.last_fetch < self.update_interval and self.cached_images:
            self.logger.info("Using cached RSS images")
            return
        
        self.logger.info(f"Fetching images from RSS feed: {self.rss_url}")
        
        try:
            # Fetch RSS feed
            response = requests.get(self.rss_url, timeout=30)
            response.raise_for_status()
            
            # Parse RSS XML
            root = ET.fromstring(response.content)
            
            # Find all items (posts)
            items = root.findall('.//item')
            self.logger.info(f"Found {len(items)} posts in RSS feed")
            
            # Extract image URLs from posts
            new_images = []
            for item in items:
                # Get post description/content
                description_elem = item.find('description')
                if description_elem is not None:
                    description = description_elem.text or ""
                    
                    # Extract image URLs using regex
                    # Look for img src attributes
                    img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
                    img_matches = re.findall(img_pattern, description, re.IGNORECASE)
                    
                    for img_url in img_matches:
                        # Filter out small images (thumbnails, avatars, etc.)
                        if self._is_valid_image_url(img_url):
                            new_images.append({
                                'url': img_url,
                                'post_title': item.find('title').text if item.find('title') is not None else 'Untitled',
                                'post_link': item.find('link').text if item.find('link') is not None else '',
                                'timestamp': self._parse_rss_date(item.find('pubDate').text) if item.find('pubDate') is not None else 0
                            })
                            self.logger.debug(f"Found image URL: {img_url}")
            
            if new_images:
                # Remove duplicates while preserving order
                seen_urls = set()
                unique_images = []
                for img in new_images:
                    if img['url'] not in seen_urls:
                        seen_urls.add(img['url'])
                        unique_images.append(img)
                
                self.cached_images = unique_images[:self.max_posts]
                self.current_index = 0
                self.last_fetch = current_time
                self.logger.info(f"Cached {len(self.cached_images)} unique images from RSS feed")
            else:
                self.logger.warning("No images found in RSS feed")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch RSS feed: {e}")
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse RSS XML: {e}")
        except Exception as e:
            self.logger.error(f"Error processing RSS feed: {e}")
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if the image URL is valid and not a thumbnail."""
        # Skip very small images (likely thumbnails)
        if any(size in url for size in ['s75x75', 's100x200', 's250x400']):
            return False
        
        # Skip avatar images
        if 'avatar' in url.lower():
            return False
        
        # Must be a valid image URL
        if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            return False
        
        return True
    
    def _parse_rss_date(self, date_str: str) -> int:
        """Parse RSS date string to timestamp."""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return int(dt.timestamp())
        except:
            return 0
    
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
    
    def _get_image_background_color(self, img: Image.Image) -> tuple:
        """Get background color by sampling corner pixels of the image."""
        try:
            width, height = img.size
            
            # Sample pixels from all four corners
            corner_pixels = [
                img.getpixel((0, 0)),                    # Top-left
                img.getpixel((width-1, 0)),             # Top-right
                img.getpixel((0, height-1)),            # Bottom-left
                img.getpixel((width-1, height-1))       # Bottom-right
            ]
            
            # Convert all corner pixels to RGB format
            rgb_pixels = []
            for pixel in corner_pixels:
                if img.mode == 'RGBA':
                    # For RGBA, use RGB values and ignore alpha
                    rgb_pixels.append(pixel[:3])
                elif img.mode == 'RGB':
                    rgb_pixels.append(pixel)
                elif img.mode == 'L':
                    # For grayscale, convert to RGB
                    rgb_pixels.append((pixel, pixel, pixel))
                else:
                    # Fallback to white
                    rgb_pixels.append((255, 255, 255))
            
            # Calculate average color from corner pixels
            avg_r = sum(pixel[0] for pixel in rgb_pixels) // len(rgb_pixels)
            avg_g = sum(pixel[1] for pixel in rgb_pixels) // len(rgb_pixels)
            avg_b = sum(pixel[2] for pixel in rgb_pixels) // len(rgb_pixels)
            
            bg_color = (avg_r, avg_g, avg_b)
            self.logger.debug(f"Detected background color from image corners: {bg_color}")
            return bg_color
            
        except Exception as e:
            self.logger.warning(f"Failed to detect background color: {e}")
            return self._get_background_color()
    
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
        
        # Get background color - either from image or configured color
        if self.background_color == "auto":
            bg_color = self._get_image_background_color(img)
        else:
            bg_color = self._get_background_color()
        
        # Create a new image with target size and paste the resized image in the center
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
        
        self.display_utils.draw_text_centered(draw, "No RSS Images", 150, font_large, self.display_utils.BLACK)
        self.display_utils.draw_text_centered(draw, f"Feed: {self.rss_url}", 200, font_medium, self.display_utils.BLUE)
        self.display_utils.draw_text_centered(draw, "Check RSS feed and connection", 230, font_medium, self.display_utils.BLUE)
        
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
        
        self.display_utils.draw_text_centered(draw, "Loading RSS Images", 150, font_large, self.display_utils.BLACK)
        self.display_utils.draw_text_centered(draw, "From Tumblr RSS Feed", 200, font_medium, self.display_utils.BLUE)
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
            self._fetch_rss_images()
        
        if not self.cached_images:
            self._show_no_images_message()
            return
        
        try:
            # Get next image
            image_data = self._get_next_image()
            if not image_data:
                self.logger.warning("No images available")
                return
            
            self.logger.info(f"Displaying RSS image: {image_data['url']}")
            
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
            self.logger.error(f"Error in Tumblr RSS mode: {e}")
