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
            return None
        
        try:
            return self._render_with_browser()
        except Exception as e:
            self.logger.error(f"Error generating weather display: {e}")
            return None
    
    def _render_with_browser(self) -> Optional[Image.Image]:
        """Render weather display using browser automation."""
        try:
            from playwright.sync_api import sync_playwright
            
            # Generate HTML content
            html_content = self._generate_html_content()
            
            with sync_playwright() as p:
                # Launch browser using system Chromium
                browser = p.chromium.launch(
                    headless=True,
                    executable_path='/usr/bin/chromium-browser',
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-extensions',
                        '--disable-plugins'
                    ]
                )
                
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
    
