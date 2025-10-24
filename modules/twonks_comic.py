"""
Twonks Comic RSS Feed Mode
Displays comic images from the Twonks (@twonkcomics) RSS feed.
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


class TwonksComicMode:
    """Twonks comic RSS feed mode for displaying comic images from the Twonks feed."""
    
    def __init__(self, inky_display, config: dict, display_utils, main_app=None):
        """Initialize Twonks comic RSS feed mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.main_app = main_app  # Reference to main app for mode switching
        self.logger = logging.getLogger(__name__)
        
        # Get Twonks comic RSS configuration
        self.comic_config = config.get('twonks_comic', {})
        self.rss_url = self.comic_config.get('rss_url', 'https://fetchrss.com/feed/aPqdPwCxq2JyaPqdK5gClBE1.rss')
        self.display_time = self.comic_config.get('display_time', 20)  # Longer display time for comics
        self.max_posts = self.comic_config.get('max_posts', 10)
        self.update_interval = self.comic_config.get('update_interval', 3600)  # 1 hour
        self.background_color = self.comic_config.get('background_color', 'white')
        self.saturation = self.comic_config.get('saturation', 0.8)  # Higher saturation for comics
        self.fill_screen = self.comic_config.get('fill_screen', True)  # Fill screen for comics
        self.auto_rotate = self.comic_config.get('auto_rotate', False)
        
        # Image cache and current state
        self.cached_images = []
        self.current_index = 0
        self.last_update = 0
        self.last_fetch = 0
        
        # Cache directory
        self.cache_dir = Path("data/cache/twonks_comic")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load initial images
        self._fetch_rss_images()
    
    def _fetch_rss_images(self):
        """Fetch comic images from Twonks RSS feed."""
        current_time = time.time()
        
        # Check if we need to fetch new images
        if current_time - self.last_fetch < self.update_interval and self.cached_images:
            self.logger.info("Using cached Twonks comic images")
            return
        
        self.logger.info(f"Fetching comic images from RSS feed: {self.rss_url}")
        
        try:
            # Fetch RSS feed
            response = requests.get(self.rss_url, timeout=30)
            response.raise_for_status()
            
            # Parse RSS XML
            root = ET.fromstring(response.content)
            
            # Find all items (comic posts)
            items = root.findall('.//item')
            self.logger.info(f"Found {len(items)} comic posts in RSS feed")
            
            # Extract image URLs from posts
            new_images = []
            for item in items:
                # Look for media:content elements first (preferred method)
                media_content = item.find('.//{http://search.yahoo.com/mrss/}content')
                if media_content is not None:
                    img_url = media_content.get('url')
                    if img_url and self._is_valid_comic_url(img_url):
                        new_images.append({
                            'url': img_url,
                            'post_title': item.find('title').text if item.find('title') is not None else 'Untitled Comic',
                            'post_link': item.find('link').text if item.find('link') is not None else '',
                            'timestamp': self._parse_rss_date(item.find('pubDate').text) if item.find('pubDate') is not None else 0
                        })
                        self.logger.debug(f"Found comic from media:content: {item.find('title').text if item.find('title') is not None else 'Untitled Comic'}")
                        continue
                
                # Fallback: extract from description using regex
                description_elem = item.find('description')
                if description_elem is not None:
                    description = description_elem.text or ""
                    
                    # Extract image URLs using regex
                    img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
                    img_matches = re.findall(img_pattern, description, re.IGNORECASE)
                    
                    for img_url in img_matches:
                        if self._is_valid_comic_url(img_url):
                            new_images.append({
                                'url': img_url,
                                'post_title': item.find('title').text if item.find('title') is not None else 'Untitled Comic',
                                'post_link': item.find('link').text if item.find('link') is not None else '',
                                'timestamp': self._parse_rss_date(item.find('pubDate').text) if item.find('pubDate') is not None else 0
                            })
                            self.logger.debug(f"Found comic from description: {item.find('title').text if item.find('title') is not None else 'Untitled Comic'}")
                            break  # Use the first valid image
            
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
                self.logger.info(f"Cached {len(self.cached_images)} unique comic images from RSS feed")
            else:
                self.logger.warning("No comic images found in RSS feed")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch RSS feed: {e}")
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse RSS XML: {e}")
        except Exception as e:
            self.logger.error(f"Error processing RSS feed: {e}")
    
    def _is_valid_comic_url(self, url: str) -> bool:
        """Check if the comic image URL is valid."""
        # Skip very small images (likely thumbnails)
        if any(size in url for size in ['s75x75', 's100x200', 's250x400', '50x50', '100x100']):
            return False
        
        # Skip avatar images
        if 'avatar' in url.lower():
            return False
        
        # Skip error/placeholder images
        if any(error_indicator in url.lower() for error_indicator in [
            'error', 'placeholder', 'missing', 'default', 'noimage', 'broken'
        ]):
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
    
    def _download_image(self, image_url: str) -> Optional[tuple]:
        """Download and process a comic image from URL. Returns (image, background_color)."""
        try:
            # Check cache first
            cache_filename = f"{hash(image_url)}.jpg"
            cache_path = self.cache_dir / cache_filename
            
            if cache_path.exists():
                self.logger.debug(f"Loading cached comic image: {cache_filename}")
                img = Image.open(cache_path)
                # For cached images, detect background from the cached RGB image
                bg_color = self._get_image_background_color(img)
                return img, bg_color
            
            # Download image
            self.logger.debug(f"Downloading comic image from URL")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Load image from bytes
            original_img = Image.open(io.BytesIO(response.content))
            
            # Detect background color from original image before conversion
            bg_color = self._get_image_background_color(original_img)
            
            # Convert to RGB if necessary
            if original_img.mode == 'RGBA':
                # Use the detected background color instead of white
                background = Image.new('RGB', original_img.size, bg_color)
                background.paste(original_img, mask=original_img.split()[-1])  # Use alpha channel as mask
                img = background
            elif original_img.mode != 'RGB':
                img = original_img.convert('RGB')
            else:
                img = original_img
            
            # Cache the image
            try:
                img.save(cache_path, 'JPEG', quality=90)  # Higher quality for comics
            except Exception as e:
                self.logger.warning(f"Failed to cache comic image: {e}")
            
            return img, bg_color
            
        except Exception as e:
            self.logger.error(f"Failed to download comic image: {e}")
            return None
    
    def _get_next_image(self) -> Optional[Dict[str, Any]]:
        """Get the next comic image in the sequence."""
        if not self.cached_images:
            return None
        
        image_data = self.cached_images[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.cached_images)
        return image_data
    
    def _get_image_background_color(self, img: Image.Image) -> tuple:
        """Get background color by sampling corner pixels of the comic image."""
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
            self.logger.debug(f"Detected background color from comic image corners: {bg_color}")
            return bg_color
            
        except Exception as e:
            self.logger.warning(f"Failed to detect background color: {e}")
            return self._get_background_color()
    
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
        """Show a message when no comic images are available."""
        img = self.display_utils.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        # Draw message
        font_large = self.display_utils.get_font('large', 24)
        font_medium = self.display_utils.get_font('medium', 16)
        
        self.display_utils.draw_text_centered(draw, "No Comic Images", 150, font_large, self.display_utils.BLACK)
        self.display_utils.draw_text_centered(draw, "Twonks Comics", 200, font_medium, self.display_utils.BLUE)
        self.display_utils.draw_text_centered(draw, "Check RSS feed and connection", 230, font_medium, self.display_utils.BLUE)
        
        try:
            self.inky.set_image(img)
            self.inky.show()
        except Exception as e:
            self.logger.error(f"Failed to show no images message: {e}")
    
    def _show_loading_message(self):
        """Show a loading message while fetching comic images."""
        img = self.display_utils.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        # Draw message
        font_large = self.display_utils.get_font('large', 24)
        font_medium = self.display_utils.get_font('medium', 16)
        
        self.display_utils.draw_text_centered(draw, "Loading Comics", 150, font_large, self.display_utils.BLACK)
        self.display_utils.draw_text_centered(draw, "Twonks Comics", 200, font_medium, self.display_utils.BLUE)
        self.display_utils.draw_text_centered(draw, "Please wait...", 230, font_medium, self.display_utils.BLUE)
        
        try:
            self.inky.set_image(img)
            self.inky.show()
        except Exception as e:
            self.logger.error(f"Failed to show loading message: {e}")
    
    def update_display(self):
        """Update the display with the next comic image if it's time."""
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
            # Get next comic image
            image_data = self._get_next_image()
            if not image_data:
                self.logger.warning("No comic images available")
                return
            
            self.logger.info(f"Displaying comic: {image_data['post_title']}")
            
            # Download and process the comic image
            result = self._download_image(image_data['url'])
            if result is None:
                self.logger.error(f"Failed to download comic image: {image_data['post_title']}")
                return
            
            img, bg_color = result
            
            # Resize to display resolution while maintaining aspect ratio
            img = self.display_utils.resize_with_aspect_ratio(
                img, self.inky.resolution, 
                fill_screen=self.fill_screen, 
                auto_rotate=self.auto_rotate,
                bg_color=bg_color
            )
            
            # Set image directly with saturation
            try:
                self.inky.set_image(img, saturation=self.saturation)
            except TypeError:
                # Fallback for older inky versions
                self.inky.set_image(img)
            
            # Display the comic image
            try:
                self.inky.show()
            except Exception as e:
                self.logger.error(f"Failed to display comic image: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in Twonks comic mode: {e}")
