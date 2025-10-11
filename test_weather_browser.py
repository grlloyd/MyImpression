#!/usr/bin/env python3
"""
Browser Test for HTML Weather Mode
Generates HTML weather display and opens it in a browser for testing.
"""

import json
import webbrowser
import tempfile
from pathlib import Path
from modules.weather_api import WeatherAPIClient
from jinja2 import Environment, FileSystemLoader

def generate_test_html():
    """Generate HTML weather display for browser testing."""
    
    # Create test configuration
    config = {
        "weather": {
            "latitude": 51.5074,  # London
            "longitude": -0.1278,
            "display_time": 300,
            "update_interval": 1800,
            "cache_duration": 3600
        }
    }
    
    # Initialize weather API client
    weather_api = WeatherAPIClient(config)
    
    # Get weather data
    print("Fetching weather data...")
    weather_data = weather_api.get_weather_data()
    
    if not weather_data:
        print("Failed to fetch weather data. Using mock data for testing.")
        # Create mock weather data for testing
        weather_data = {
            "current": {
                "temperature": 22,
                "weather_code": 0,  # Clear sky
                "time": "2024-01-15T14:00"
            },
            "daily": [
                {"time": "2024-01-15", "weather_code": 0, "temp_max": 25, "temp_min": 15},
                {"time": "2024-01-16", "weather_code": 2, "temp_max": 23, "temp_min": 12},
                {"time": "2024-01-17", "weather_code": 61, "temp_max": 18, "temp_min": 8},
                {"time": "2024-01-18", "weather_code": 0, "temp_max": 20, "temp_min": 10},
                {"time": "2024-01-19", "weather_code": 1, "temp_max": 24, "temp_min": 14}
            ],
            "hourly": [
                {"time": "2024-01-15T12:00", "weather_code": 0, "temperature": 22},
                {"time": "2024-01-15T15:00", "weather_code": 2, "temperature": 20},
                {"time": "2024-01-15T18:00", "weather_code": 61, "temperature": 18},
                {"time": "2024-01-15T21:00", "weather_code": 61, "temperature": 16},
                {"time": "2024-01-16T00:00", "weather_code": 61, "temperature": 14},
                {"time": "2024-01-16T03:00", "weather_code": 0, "temperature": 12},
                {"time": "2024-01-16T06:00", "weather_code": 0, "temperature": 15},
                {"time": "2024-01-16T09:00", "weather_code": 0, "temperature": 18},
                {"time": "2024-01-16T12:00", "weather_code": 2, "temperature": 20},
                {"time": "2024-01-16T15:00", "weather_code": 2, "temperature": 22},
                {"time": "2024-01-16T18:00", "weather_code": 61, "temperature": 19},
                {"time": "2024-01-16T21:00", "weather_code": 61, "temperature": 17}
            ]
        }
    
    # Setup Jinja2 template environment
    template_dir = Path("templates")
    jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    # Load the template
    template = jinja_env.get_template('weather.html')
    
    # Prepare data for template
    template_data = {
        'weather_data': json.dumps(weather_data, indent=2)
    }
    
    # Render template
    html_content = template.render(**template_data)
    
    # Inline CSS to avoid external dependencies
    css_path = template_dir / 'weather.css'
    if css_path.exists():
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Replace CSS link with inline styles
        html_content = html_content.replace(
            '<link rel="stylesheet" href="weather.css">',
            f'<style>{css_content}</style>'
        )
    
    # Replace external font links with inline styles
    font_css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    """
    html_content = html_content.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">',
        f'<style>{font_css}</style>'
    )
    
    # Replace Font Awesome with emoji icons for browser testing
    icon_css = """
    /* Emoji icon replacements for browser testing */
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
    
    return html_content, weather_data

def main():
    """Generate HTML and open in browser."""
    print("Generating HTML weather display for browser testing...")
    
    try:
        # Generate HTML content
        html_content, weather_data = generate_test_html()
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        
        print(f"HTML file created: {temp_file}")
        
        # Also save a permanent copy for reference
        output_file = "weather_test.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Permanent copy saved: {output_file}")
        
        # Open in browser
        print("Opening in browser...")
        webbrowser.open(f'file://{temp_file}')
        
        print("\n" + "="*60)
        print("BROWSER TEST INSTRUCTIONS:")
        print("="*60)
        print("1. The weather display should open in your browser")
        print("2. Check that the layout looks good at 800x480 resolution")
        print("3. Try resizing the browser window to test responsiveness")
        print("4. Verify that weather icons and data are displayed correctly")
        print("5. Check that colors and typography look professional")
        print("\nTo test at exact display size:")
        print("- Press F12 to open developer tools")
        print("- Click the device toolbar icon (mobile/tablet icon)")
        print("- Set custom dimensions to 800x480")
        print("- Refresh the page")
        print("\nWeather data used:")
        print(f"- Current: {weather_data['current']['temperature']}°C, Code {weather_data['current']['weather_code']}")
        print(f"- 5-day forecast: {len(weather_data['daily'])} days")
        print(f"- Hourly forecast: {len(weather_data['hourly'])} hours")
        print("="*60)
        
    except Exception as e:
        print(f"Error generating HTML: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
