"""
Display Utilities Module
Common utilities for display management and layout.
"""

import logging
from typing import Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont
import os


class DisplayUtils:
    """Utilities for display management and common operations."""
    
    def __init__(self, inky_display, config: dict):
        """Initialize display utilities."""
        self.inky = inky_display
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Color constants for 6-color display
        self.BLACK = self.inky.BLACK
        self.WHITE = self.inky.WHITE
        self.GREEN = getattr(self.inky, 'GREEN', 2)
        self.BLUE = getattr(self.inky, 'BLUE', 3)
        self.RED = getattr(self.inky, 'RED', 4)
        self.YELLOW = getattr(self.inky, 'YELLOW', 5)
        
        # Available colors
        self.colors = [self.BLACK, self.WHITE, self.GREEN, self.BLUE, self.RED, self.YELLOW]
        
        # Font paths
        self.font_paths = {
            'small': self._find_font('small'),
            'medium': self._find_font('medium'),
            'large': self._find_font('large')
        }
    
    def _find_font(self, size: str) -> str:
        """Find appropriate font file for given size."""
        font_files = {
            'small': ['arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf'],
            'medium': ['arial.ttf', 'DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf'],
            'large': ['arial.ttf', 'DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf']
        }
        
        # Check assets/fonts directory first
        assets_fonts = Path("assets/fonts")
        if assets_fonts.exists():
            for font_file in font_files.get(size, font_files['medium']):
                font_path = assets_fonts / font_file
                if font_path.exists():
                    return str(font_path)
        
        # Fallback to system fonts
        for font_file in font_files.get(size, font_files['medium']):
            try:
                # Try to load the font to see if it exists
                font = ImageFont.truetype(font_file, 12)
                return font_file
            except:
                continue
        
        # Ultimate fallback
        return None
    
    def get_font(self, size: str, font_size: int = None) -> ImageFont.ImageFont:
        """Get font with specified size."""
        if font_size is None:
            font_sizes = {'small': 12, 'medium': 16, 'large': 24}
            font_size = font_sizes.get(size, 16)
        
        font_path = self.font_paths.get(size)
        if font_path:
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                pass
        
        # Fallback to default font
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def create_blank_image(self, color: int = None) -> Image.Image:
        """Create a blank image with specified background color."""
        if color is None:
            color = self.WHITE
        
        return Image.new("P", self.inky.resolution, color)
    
    def create_image_with_palette(self) -> Image.Image:
        """Create image with proper color palette for the display."""
        img = Image.new("P", self.inky.resolution)
        
        # Set up the palette for 6-color display
        palette = []
        for color in self.colors:
            if color == self.BLACK:
                palette.extend([0, 0, 0])  # Black
            elif color == self.WHITE:
                palette.extend([255, 255, 255])  # White
            elif color == self.GREEN:
                palette.extend([0, 255, 0])  # Green
            elif color == self.BLUE:
                palette.extend([0, 0, 255])  # Blue
            elif color == self.RED:
                palette.extend([255, 0, 0])  # Red
            elif color == self.YELLOW:
                palette.extend([255, 255, 0])  # Yellow
            else:
                palette.extend([128, 128, 128])  # Gray fallback
        
        img.putpalette(palette)
        return img
    
    def draw_text_centered(self, draw: ImageDraw.Draw, text: str, y: int, 
                          font: ImageFont.ImageFont, color: int = None) -> None:
        """Draw centered text on the image."""
        if color is None:
            color = self.BLACK
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate centered position
        x = (self.inky.width - text_width) // 2
        y = y - text_height // 2
        
        draw.text((x, y), text, font=font, fill=color)
    
    def draw_text_multiline(self, draw: ImageDraw.Draw, text: str, 
                           start_y: int, font: ImageFont.ImageFont, 
                           color: int = None, line_spacing: int = 5) -> int:
        """Draw multiline text and return the final Y position."""
        if color is None:
            color = self.BLACK
        
        lines = text.split('\n')
        current_y = start_y
        
        for line in lines:
            if line.strip():  # Skip empty lines
                self.draw_text_centered(draw, line.strip(), current_y, font, color)
                current_y += font.size + line_spacing
        
        return current_y
    
    def draw_progress_bar(self, draw: ImageDraw.Draw, x: int, y: int, 
                         width: int, height: int, progress: float, 
                         bg_color: int = None, fg_color: int = None) -> None:
        """Draw a progress bar."""
        if bg_color is None:
            bg_color = self.WHITE
        if fg_color is None:
            fg_color = self.BLUE
        
        # Draw background
        draw.rectangle([x, y, x + width, y + height], fill=bg_color, outline=self.BLACK)
        
        # Draw progress
        if progress > 0:
            progress_width = int(width * progress)
            draw.rectangle([x, y, x + progress_width, y + height], fill=fg_color)
    
    def draw_icon(self, img: Image.Image, icon_path: str, x: int, y: int, 
                  size: Tuple[int, int] = None) -> bool:
        """Draw an icon on the image."""
        try:
            if not os.path.exists(icon_path):
                return False
            
            icon = Image.open(icon_path)
            if size:
                icon = icon.resize(size, Image.Resampling.LANCZOS)
            
            # Convert icon to palette mode if needed
            if icon.mode != 'P':
                icon = icon.convert('P')
            
            # Paste the icon
            img.paste(icon, (x, y))
            return True
            
        except Exception as e:
            self.logger.error(f"Error drawing icon {icon_path}: {e}")
            return False
    
    def show_error(self, error_message: str):
        """Display an error message on the screen."""
        img = self.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        # Draw error message
        font = self.get_font('medium', 20)
        self.draw_text_centered(draw, "ERROR", 100, font, self.RED)
        
        # Draw error details
        font_small = self.get_font('small', 14)
        self.draw_text_multiline(draw, error_message, 150, font_small, self.BLACK)
        
        # Show on display
        try:
            self.inky.set_image(img)
            self.inky.show()
        except Exception as e:
            self.logger.error(f"Failed to show error display: {e}")
    
    def show_loading(self, message: str = "Loading..."):
        """Display a loading message."""
        img = self.create_image_with_palette()
        draw = ImageDraw.Draw(img)
        
        font = self.get_font('large', 24)
        self.draw_text_centered(draw, message, self.inky.height // 2, font, self.BLUE)
        
        try:
            self.inky.set_image(img)
            self.inky.show()
        except Exception as e:
            self.logger.error(f"Failed to show loading display: {e}")
    
    def optimize_for_display(self, img: Image.Image) -> Image.Image:
        """Optimize image for the 6-color display."""
        # Resize to display resolution
        img = img.resize(self.inky.resolution, Image.Resampling.LANCZOS)
        
        # Convert to palette mode with our color palette
        if img.mode != 'P':
            # Convert to RGB first, then to palette
            img = img.convert('RGB')
        
        # Create palette image
        palette_img = self.create_image_with_palette()
        
        # Copy the resized image to the palette image
        # This is a simple approach - in practice you might want more sophisticated dithering
        palette_img.paste(img)
        
        return palette_img
