#!/usr/bin/env python3
"""
Test script to verify weather icon configuration options.
"""

import json
import tempfile
from pathlib import Path
from modules.weather_html import WeatherHTMLMode
from modules.display_utils import DisplayUtils

class MockDisplay:
    """Mock display for testing."""
    def __init__(self):
        self.resolution = (800, 480)
    
    def set_image(self, image):
        print(f"Mock display: Setting image {image.size}")
    
    def show(self):
        print("Mock display: Showing image")

class MockDisplayUtils:
    """Mock display utils for testing."""
    def __init__(self, display, config):
        self.display = display
        self.config = config

def test_icon_configurations():
    """Test different icon configuration options."""
    
    # Test configurations
    configs = [
        {
            "name": "Emoji Icons",
            "config": {
                "weather_html": {
                    "icon_source": "emoji",
                    "update_interval": 1800
                }
            }
        },
        {
            "name": "Font Awesome Icons", 
            "config": {
                "weather_html": {
                    "icon_source": "fontawesome",
                    "update_interval": 1800
                }
            }
        },
        {
            "name": "Custom Icons",
            "config": {
                "weather_html": {
                    "icon_source": "custom",
                    "custom_icon_path": "assets/icons/weather/",
                    "update_interval": 1800
                }
            }
        }
    ]
    
    mock_display = MockDisplay()
    mock_display_utils = MockDisplayUtils(mock_display, {})
    
    for test_config in configs:
        print(f"\n=== Testing {test_config['name']} ===")
        
        try:
            # Create weather mode with test configuration
            weather_mode = WeatherHTMLMode(
                mock_display, 
                test_config['config'], 
                mock_display_utils
            )
            
            # Check icon configuration
            icon_config = weather_mode.icon_config
            print(f"Icon sources: {icon_config.get('icon_sources', [])}")
            print(f"Custom icon path: {icon_config.get('custom_icon_path', 'N/A')}")
            
            # Test icon generation for a few weather codes
            test_codes = [0, 3, 61, 95]  # Clear, Overcast, Rain, Thunderstorm
            for code in test_codes:
                icon = weather_mode._get_icon_for_weather_code(code, 'large')
                print(f"Weather code {code}: {icon}")
            
            print(f"[OK] {test_config['name']} configuration successful")
            
        except Exception as e:
            print(f"[ERROR] {test_config['name']} configuration failed: {e}")

def test_config_file_loading():
    """Test loading configuration from file."""
    print("\n=== Testing Configuration File Loading ===")
    
    # Create a temporary config file
    config_data = {
        "weather_html": {
            "icon_source": "fontawesome",
            "custom_icon_path": "test/icons/",
            "update_interval": 900
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f, indent=2)
        config_path = f.name
    
    try:
        # Load the config file
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        print(f"Loaded config: {loaded_config}")
        
        # Test weather mode with loaded config
        mock_display = MockDisplay()
        mock_display_utils = MockDisplayUtils(mock_display, loaded_config)
        
        weather_mode = WeatherHTMLMode(mock_display, loaded_config, mock_display_utils)
        icon_config = weather_mode.icon_config
        
        print(f"Final icon sources: {icon_config.get('icon_sources', [])}")
        print(f"Final custom path: {icon_config.get('custom_icon_path', 'N/A')}")
        
        print("[OK] Configuration file loading successful")
        
    except Exception as e:
        print(f"[ERROR] Configuration file loading failed: {e}")
    finally:
        # Clean up temp file
        Path(config_path).unlink()

if __name__ == "__main__":
    print("Weather Icon Configuration Test")
    print("=" * 40)
    
    test_icon_configurations()
    test_config_file_loading()
    
    print("\n" + "=" * 40)
    print("Test completed!")
    print("\nTo use different icon sources in your app:")
    print("1. Edit your config.json file")
    print("2. Set 'icon_source' to 'emoji', 'fontawesome', or 'custom'")
    print("3. For custom icons, place PNG files in the specified directory")
    print("4. Restart your application")
