"""
HTML Weather Mode
Displays weather using HTML templates and browser screen capture for modern graphics.
"""

import time
import logging
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
from jinja2 import Template, Environment, FileSystemLoader

from .weather_api import WeatherAPIClient


class WeatherHTMLMode:
    """HTML-based weather display mode for the e-ink display."""
    
    def __init__(self, inky_display, config: dict, display_utils, main_app=None):
        """Initialize HTML weather mode."""
        self.inky = inky_display
        self.config = config
        self.display_utils = display_utils
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Get weather configuration
        self.weather_config = config.get('weather', {})
        self.display_time = self.weather_config.get('display_time', 300)  # 5 minutes
        
        # Initialize weather API client
        self.weather_api = WeatherAPIClient(config)
        
        # Weather data cache
        self.weather_data = None
        self.last_update = 0
        
        # Setup Jinja2 template environment
        self.template_dir = Path("templates")
        self.template_dir.mkdir(exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
        # Browser automation setup
        self._setup_browser()
    
    def _setup_browser(self):
        """Setup browser automation for screen capture."""
        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright
            self.browser_available = True
            self.logger.info("Playwright browser automation available")
        except ImportError:
            self.logger.warning("Playwright not available, falling back to basic HTML generation")
            self.browser_available = False
    
    def update_display(self):
        """Update the weather display using HTML rendering."""
        current_time = time.time()
        
        # Check if we need to update the display
        if current_time - self.last_update < self.display_time:
            return
        
        try:
            # Get fresh weather data
            self.weather_data = self.weather_api.get_weather_data()
            
            if self.weather_data:
                # Generate and show weather display
                weather_img = self._generate_weather_display()
                if weather_img:
                    # Optimize for display
                    optimized_img = self.display_utils.optimize_for_display(weather_img)
                    
                    # Show on display
                    self.inky.set_image(optimized_img)
                    self.inky.show()
                    
                    self.last_update = current_time
                    self.logger.info("HTML weather display updated successfully")
            else:
                self.logger.warning("No weather data available")
                self.display_utils.show_error("Weather data unavailable")
                
        except Exception as e:
            self.logger.error(f"HTML weather display error: {e}")
            self.display_utils.show_error(f"Weather Error: {str(e)}")
    
    def _generate_weather_display(self) -> Optional[Image.Image]:
        """Generate the weather display image using HTML rendering."""
        if not self.weather_data:
            return None
        
        if not self.browser_available:
            self.logger.error("Browser automation not available. Playwright installation required.")
            return self._generate_fallback_display()
        
        try:
            return self._render_with_browser()
        except Exception as e:
            self.logger.error(f"Error generating weather display: {e}")
            self.logger.info("Falling back to simple text display")
            return self._generate_fallback_display()
    
    def _render_with_browser(self) -> Optional[Image.Image]:
        """Render weather display using browser automation."""
        try:
            from playwright.sync_api import sync_playwright
            import shutil
            
            # Generate HTML content
            html_content = self._generate_html_content()
            
            with sync_playwright() as p:
                # Find available browser executable
                browser_executable = self._find_browser_executable()
                
                # Launch browser with appropriate settings
                launch_options = {
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                }
                
                # Add executable path if found
                if browser_executable:
                    launch_options['executable_path'] = browser_executable
                    self.logger.info(f"Using browser executable: {browser_executable}")
                else:
                    self.logger.info("Using default browser executable")
                
                browser = p.chromium.launch(**launch_options)
                
                # Create page with exact display dimensions
                page = browser.new_page(viewport={
                    'width': self.inky.width,
                    'height': self.inky.height,
                    'deviceScaleFactor': 1
                })
                
                # Set content and wait for fonts to load
                page.set_content(html_content, wait_until='networkidle')
                
                # Wait a bit for any animations or fonts to settle
                page.wait_for_timeout(1000)
                
                # Take screenshot
                screenshot_bytes = page.screenshot(
                    type='png',
                    full_page=False,
                    clip={
                        'x': 0,
                        'y': 0,
                        'width': self.inky.width,
                        'height': self.inky.height
                    }
                )
                
                browser.close()
                
                # Convert to PIL Image
                from io import BytesIO
                img = Image.open(BytesIO(screenshot_bytes))
                return img
                
        except Exception as e:
            self.logger.error(f"Browser rendering failed: {e}")
            return None
    
    def _find_browser_executable(self) -> Optional[str]:
        """Find the best available browser executable for the system."""
        import shutil
        import os
        
        # Common browser executable paths on Raspberry Pi/Linux systems
        # Prioritize chromium-headless-shell for better performance in headless mode
        browser_paths = [
            '/usr/bin/chromium-headless-shell',  # Best for headless automation
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/snap/bin/chromium',
            '/usr/local/bin/chromium-browser',
            '/opt/google/chrome/chrome'
        ]
        
        # Check which browser is available
        for path in browser_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.logger.info(f"Found browser executable: {path}")
                return path
        
        # Try to find chromium in PATH (prioritize headless-shell)
        chromium_path = shutil.which('chromium-headless-shell')
        if chromium_path:
            self.logger.info(f"Found chromium-headless-shell in PATH: {chromium_path}")
            return chromium_path
            
        chromium_path = shutil.which('chromium-browser')
        if chromium_path:
            self.logger.info(f"Found chromium-browser in PATH: {chromium_path}")
            return chromium_path
            
        chromium_path = shutil.which('chromium')
        if chromium_path:
            self.logger.info(f"Found chromium in PATH: {chromium_path}")
            return chromium_path
            
        # Try to find chrome in PATH
        chrome_path = shutil.which('google-chrome')
        if chrome_path:
            self.logger.info(f"Found google-chrome in PATH: {chrome_path}")
            return chrome_path
        
        self.logger.warning("No browser executable found, will use default")
        return None
    
    def _generate_fallback_display(self) -> Optional[Image.Image]:
        """Generate a simple fallback weather display without browser rendering."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a new image with the display dimensions
            img = Image.new('RGB', (self.inky.width, self.inky.height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a system font, fallback to default
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                try:
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                except:
                    font_large = font_medium = font_small = None
            
            # Get weather data
            current = self.weather_data.get('current', {})
            location = self.weather_data.get('location', {})
            
            # Draw weather information
            y_pos = 10
            
            # Location
            if location.get('name'):
                location_text = f"{location['name']}, {location.get('region', '')}"
                if font_medium:
                    draw.text((10, y_pos), location_text, fill='black', font=font_medium)
                else:
                    draw.text((10, y_pos), location_text, fill='black')
                y_pos += 25
            
            # Temperature
            if current.get('temp_c'):
                temp_text = f"{current['temp_c']:.1f}°C"
                if font_large:
                    draw.text((10, y_pos), temp_text, fill='black', font=font_large)
                else:
                    draw.text((10, y_pos), temp_text, fill='black')
                y_pos += 35
            
            # Weather condition
            if current.get('condition', {}).get('text'):
                condition_text = current['condition']['text']
                if font_medium:
                    draw.text((10, y_pos), condition_text, fill='black', font=font_medium)
                else:
                    draw.text((10, y_pos), condition_text, fill='black')
                y_pos += 25
            
            # Additional details
            details = []
            if current.get('humidity'):
                details.append(f"Humidity: {current['humidity']}%")
            if current.get('wind_kph'):
                details.append(f"Wind: {current['wind_kph']} km/h")
            if current.get('feelslike_c'):
                details.append(f"Feels like: {current['feelslike_c']:.1f}°C")
            
            for detail in details:
                if font_small:
                    draw.text((10, y_pos), detail, fill='black', font=font_small)
                else:
                    draw.text((10, y_pos), detail, fill='black')
                y_pos += 20
            
            return img
            
        except Exception as e:
            self.logger.error(f"Error generating fallback display: {e}")
            return None
    
    def _generate_html_content(self) -> str:
        """Generate HTML content with weather data."""
        try:
            # Load the template
            template = self.jinja_env.get_template('weather.html')
            
            # Prepare data for template
            template_data = {
                'weather_data': json.dumps(self.weather_data, indent=2)
            }
            
            # Render template
            html_content = template.render(**template_data)
            
            # Inline CSS to avoid external dependencies
            css_path = self.template_dir / 'weather.css'
            if css_path.exists():
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                # Replace CSS link with inline styles
                html_content = html_content.replace(
                    '<link rel="stylesheet" href="weather.css">',
                    f'<style>{css_content}</style>'
                )
            
            # Replace external font links with inline styles for better reliability
            font_css = """
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            """
            html_content = html_content.replace(
                '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">',
                f'<style>{font_css}</style>'
            )
            
            # Replace Font Awesome with a simpler icon solution
            icon_css = """
            /* Simple icon replacements for Font Awesome */
            .fas.fa-sun:before { content: "☀️"; }
            .fas.fa-cloud:before { content: "☁️"; }
            .fas.fa-cloud-sun:before { content: "⛅"; }
            .fas.fa-cloud-rain:before { content: "🌧️"; }
            .fas.fa-cloud-showers-heavy:before { content: "🌧️"; }
            .fas.fa-snowflake:before { content: "❄️"; }
            .fas.fa-cloud-snow:before { content: "🌨️"; }
            .fas.fa-bolt:before { content: "⚡"; }
            .fas.fa-smog:before { content: "🌫️"; }
            .fas.fa-cloud-drizzle:before { content: "🌦️"; }
            .fas.fa-eye:before { content: "👁️"; }
            .fas.fa-wind:before { content: "💨"; }
            .fas.fa-tint:before { content: "💧"; }
            .fas.fa-question:before { content: "❓"; }
            """
            
            html_content = html_content.replace(
                '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
                f'<style>{icon_css}</style>'
            )
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"Error generating HTML content: {e}")
            return None
    
