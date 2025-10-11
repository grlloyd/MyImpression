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
        
        try:
            if self.browser_available:
                return self._render_with_browser()
            else:
                return self._render_fallback()
        except Exception as e:
            self.logger.error(f"Error generating weather display: {e}")
            return self._render_fallback()
    
    def _render_with_browser(self) -> Optional[Image.Image]:
        """Render weather display using browser automation."""
        try:
            from playwright.sync_api import sync_playwright
            
            # Generate HTML content
            html_content = self._generate_html_content()
            
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
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
    
    def _render_fallback(self) -> Optional[Image.Image]:
        """Fallback rendering method without browser."""
        self.logger.info("Using fallback rendering method")
        
        # Create a simple image using PIL as fallback
        img = self.display_utils.create_image_with_palette()
        
        # This is a basic fallback - in a real implementation you might
        # want to create a more sophisticated PIL-based layout
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(img)
        
        # Draw basic weather info
        current = self.weather_data['current']
        
        # Title
        font_large = self.display_utils.get_font('large', 24)
        self.display_utils.draw_text_centered(draw, "HTML Weather (Fallback)", 30, font_large, self.display_utils.BLACK)
        
        # Current temperature
        temp_text = f"{current['temperature']}°C"
        font_medium = self.display_utils.get_font('medium', 36)
        self.display_utils.draw_text_centered(draw, temp_text, 100, font_medium, self.display_utils.BLUE)
        
        # Conditions
        conditions = self.weather_api.get_weather_description(current['weather_code'])
        font_small = self.display_utils.get_font('small', 16)
        self.display_utils.draw_text_centered(draw, conditions, 150, font_small, self.display_utils.BLACK)
        
        # 5-day forecast
        daily_forecast = self.weather_data['daily']
        y_start = 200
        for i, day in enumerate(daily_forecast[:5]):
            x = 50 + (i * 140)
            day_name = self.weather_api.get_day_name(day['time'])
            
            # Day name
            self.display_utils.draw_text_centered(draw, day_name, y_start, font_small, self.display_utils.BLACK)
            
            # High temp
            high_temp = f"{day['temp_max']}°"
            self.display_utils.draw_text_centered(draw, high_temp, y_start + 30, font_small, self.display_utils.RED)
            
            # Low temp
            low_temp = f"{day['temp_min']}°"
            self.display_utils.draw_text_centered(draw, low_temp, y_start + 50, font_small, self.display_utils.BLUE)
        
        return img
    
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
            return self._generate_basic_html()
    
    def _generate_basic_html(self) -> str:
        """Generate basic HTML as ultimate fallback."""
        current = self.weather_data['current']
        daily = self.weather_data['daily'][:5]
        hourly = self.weather_data['hourly'][:12]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Weather</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: white;
                    color: black;
                    width: 760px;
                    height: 440px;
                }}
                .current {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .temp {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #0066cc;
                }}
                .forecast {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                }}
                .day {{
                    text-align: center;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                .hourly {{
                    display: flex;
                    gap: 10px;
                    overflow-x: auto;
                }}
                .hour {{
                    text-align: center;
                    padding: 5px;
                    border: 1px solid #ddd;
                    border-radius: 3px;
                    min-width: 50px;
                }}
            </style>
        </head>
        <body>
            <div class="current">
                <div class="temp">{current['temperature']}°C</div>
                <div>{self.weather_api.get_weather_description(current['weather_code'])}</div>
            </div>
            
            <div class="forecast">
        """
        
        for day in daily:
            day_name = self.weather_api.get_day_name(day['time'])
            html += f"""
                <div class="day">
                    <div>{day_name}</div>
                    <div>{day['temp_max']}°/{day['temp_min']}°</div>
                </div>
            """
        
        html += """
            </div>
            
            <div class="hourly">
        """
        
        for hour in hourly:
            time_str = self.weather_api.format_hour(hour['time'])
            html += f"""
                <div class="hour">
                    <div>{time_str}</div>
                    <div>{hour['temperature']}°</div>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
