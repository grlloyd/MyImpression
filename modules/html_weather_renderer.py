"""
HTML Weather Dashboard Renderer
Generates HTML weather dashboard and captures it as PNG for display.
"""

import os
import json
import time
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HTMLWeatherRenderer:
    """Renders weather data as HTML and captures as PNG."""
    
    def __init__(self, template_path: str = "templates/weather_dashboard.html"):
        """Initialize the HTML weather renderer."""
        self.template_path = Path(template_path)
        self.logger = logging.getLogger(__name__)
        
        # Setup Chrome options for headless rendering
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=800,480")
        self.chrome_options.add_argument("--force-device-scale-factor=1")
        
        # Initialize webdriver
        self.driver = None
        self._init_driver()
    
    def _init_driver(self):
        """Initialize the Chrome webdriver."""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.logger.info("Chrome webdriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome webdriver: {e}")
            self.driver = None
    
    def _create_html_file(self, weather_data: Dict[str, Any]) -> str:
        """Create HTML file with weather data."""
        if not self.template_path.exists():
            self.logger.error(f"Template file not found: {self.template_path}")
            return None
        
        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create temporary HTML file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
        temp_file.write(html_content)
        temp_file.close()
        
        return temp_file.name
    
    def _inject_weather_data(self, html_file: str, weather_data: Dict[str, Any]):
        """Inject weather data into HTML file using JavaScript."""
        if not self.driver:
            self.logger.error("WebDriver not initialized")
            return False
        
        try:
            # Load the HTML file
            file_url = f"file://{os.path.abspath(html_file)}"
            self.driver.get(file_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "location"))
            )
            
            # Inject weather data using JavaScript
            weather_json = json.dumps(weather_data)
            script = f"""
                if (window.updateWeather) {{
                    window.updateWeather({weather_json});
                }}
            """
            
            self.driver.execute_script(script)
            
            # Wait a moment for the display to update
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to inject weather data: {e}")
            return False
    
    def _capture_screenshot(self, output_path: str) -> bool:
        """Capture screenshot of the weather dashboard."""
        if not self.driver:
            self.logger.error("WebDriver not initialized")
            return False
        
        try:
            # Take screenshot
            self.driver.save_screenshot(output_path)
            self.logger.info(f"Screenshot saved to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return False
    
    def render_weather_dashboard(self, weather_data: Dict[str, Any], output_path: str) -> bool:
        """Render weather dashboard as PNG image."""
        if not self.driver:
            self.logger.error("WebDriver not initialized")
            return False
        
        html_file = None
        try:
            # Create HTML file
            html_file = self._create_html_file(weather_data)
            if not html_file:
                return False
            
            # Inject weather data
            if not self._inject_weather_data(html_file, weather_data):
                return False
            
            # Capture screenshot
            if not self._capture_screenshot(output_path):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to render weather dashboard: {e}")
            return False
        
        finally:
            # Clean up temporary HTML file
            if html_file and os.path.exists(html_file):
                try:
                    os.unlink(html_file)
                except Exception as e:
                    self.logger.warning(f"Failed to delete temporary HTML file: {e}")
    
    def close(self):
        """Close the webdriver."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def __del__(self):
        """Destructor to ensure webdriver is closed."""
        self.close()


class FallbackHTMLWeatherRenderer:
    """Fallback renderer that creates a simple HTML file without browser automation."""
    
    def __init__(self, template_path: str = "templates/weather_dashboard.html"):
        """Initialize the fallback renderer."""
        self.template_path = Path(template_path)
        self.logger = logging.getLogger(__name__)
    
    def render_weather_dashboard(self, weather_data: Dict[str, Any], output_path: str) -> bool:
        """Create HTML file with weather data (no PNG capture)."""
        try:
            # Read template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write HTML file
            with open(output_path.replace('.png', '.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML weather dashboard created: {output_path.replace('.png', '.html')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create HTML weather dashboard: {e}")
            return False
    
    def close(self):
        """No cleanup needed for fallback renderer."""
        pass
