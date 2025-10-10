#!/usr/bin/env python3
"""
Test script for username-based DeviantArt configuration
Tests the new username configuration system and URL construction.
"""

import sys
import os
import json
from pathlib import Path

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_url_construction():
    """Test the URL construction from usernames."""
    print("Testing DeviantArt URL Construction")
    print("=" * 50)
    
    # Test usernames
    test_usernames = [
        "WestOz64",
        "SomeArtist",
        "user123",
        "My-Art-Gallery",
        "artist_with_underscores"
    ]
    
    # Import the DeviantArt RSS module to test URL construction
    try:
        from deviantart_rss import DeviantArtRSSMode
        
        # Create a mock configuration
        config = {
            'deviantart_rss': {
                'username': 'test',
                'display_time': 15,
                'max_posts': 20,
                'update_interval': 3600,
                'background_color': 'auto',
                'saturation': 0.5
            }
        }
        
        # Create mock objects
        class MockInky:
            def __init__(self):
                self.resolution = (800, 480)
        
        class MockDisplayUtils:
            def create_image_with_palette(self):
                return None
            def get_font(self, size, height):
                return None
            def draw_text_centered(self, draw, text, y, font, color):
                pass
        
        # Create the mode instance
        mode = DeviantArtRSSMode(MockInky(), config, MockDisplayUtils())
        
        print("Testing URL construction for different usernames:")
        print("-" * 50)
        
        for username in test_usernames:
            constructed_url = mode._construct_rss_url(username)
            expected_url = f"https://backend.deviantart.com/rss.xml?q=gallery:{username}"
            
            if constructed_url == expected_url:
                print(f"✓ {username:20} → {constructed_url}")
            else:
                print(f"✗ {username:20} → {constructed_url}")
                print(f"  Expected: {expected_url}")
        
    except ImportError as e:
        print(f"✗ Failed to import DeviantArtRSSMode: {e}")
    except Exception as e:
        print(f"✗ Error testing URL construction: {e}")

def test_username_configurations():
    """Test different username configurations."""
    print(f"\n{'='*50}")
    print("Testing Username Configurations")
    print("=" * 50)
    
    # Test configurations
    test_configs = [
        {
            "name": "Default Configuration",
            "config": {
                "deviantart_rss": {
                    "username": "WestOz64",
                    "display_time": 15,
                    "max_posts": 20,
                    "update_interval": 3600,
                    "background_color": "auto",
                    "saturation": 0.5
                }
            }
        },
        {
            "name": "Custom Username",
            "config": {
                "deviantart_rss": {
                    "username": "MyFavoriteArtist",
                    "display_time": 30,
                    "max_posts": 50,
                    "update_interval": 7200,
                    "background_color": "white",
                    "saturation": 0.8
                }
            }
        },
        {
            "name": "Minimal Configuration",
            "config": {
                "deviantart_rss": {
                    "username": "AnotherArtist"
                }
            }
        }
    ]
    
    try:
        from deviantart_rss import DeviantArtRSSMode
        
        # Create mock objects
        class MockInky:
            def __init__(self):
                self.resolution = (800, 480)
        
        class MockDisplayUtils:
            def create_image_with_palette(self):
                return None
            def get_font(self, size, height):
                return None
            def draw_text_centered(self, draw, text, y, font, color):
                pass
        
        for test_config in test_configs:
            print(f"\n{test_config['name']}:")
            print("-" * 30)
            
            try:
                # Create the mode instance
                mode = DeviantArtRSSMode(MockInky(), test_config['config'], MockDisplayUtils())
                
                print(f"  Username: {mode.username}")
                print(f"  RSS URL: {mode.rss_url}")
                print(f"  Display Time: {mode.display_time}")
                print(f"  Max Posts: {mode.max_posts}")
                print(f"  Update Interval: {mode.update_interval}")
                print(f"  Background Color: {mode.background_color}")
                print(f"  Saturation: {mode.saturation}")
                
            except Exception as e:
                print(f"  ✗ Error creating mode: {e}")
        
    except ImportError as e:
        print(f"✗ Failed to import DeviantArtRSSMode: {e}")

def test_config_file_examples():
    """Show examples of configuration files with usernames."""
    print(f"\n{'='*50}")
    print("Configuration File Examples")
    print("=" * 50)
    
    examples = [
        {
            "name": "Basic Username Configuration",
            "description": "Simple configuration with just a username",
            "config": {
                "deviantart_rss": {
                    "username": "YourUsername"
                }
            }
        },
        {
            "name": "Full Custom Configuration",
            "description": "Complete configuration with all options",
            "config": {
                "deviantart_rss": {
                    "username": "YourUsername",
                    "display_time": 20,
                    "max_posts": 30,
                    "update_interval": 1800,
                    "background_color": "auto",
                    "saturation": 0.7
                }
            }
        },
        {
            "name": "Multiple DeviantArt Users",
            "description": "Example of how to set up multiple DeviantArt users",
            "config": {
                "buttons": {
                    "button_1": "deviantart_rss",
                    "button_2": "deviantart_rss_2",
                    "button_3": "photo_cycle",
                    "button_4": "tumblr_rss"
                },
                "deviantart_rss": {
                    "username": "Artist1"
                },
                "deviantart_rss_2": {
                    "username": "Artist2",
                    "display_time": 25
                }
            }
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}:")
        print(f"  {example['description']}")
        print("  Configuration:")
        print(json.dumps(example['config'], indent=4))

def test_username_validation():
    """Test username validation and edge cases."""
    print(f"\n{'='*50}")
    print("Testing Username Validation")
    print("=" * 50)
    
    # Test various username formats
    test_usernames = [
        ("Valid usernames:", [
            "WestOz64",
            "SomeArtist",
            "user123",
            "My-Art-Gallery",
            "artist_with_underscores",
            "CAPS_USER",
            "mixedCase123"
        ]),
        ("Edge cases:", [
            "",  # Empty username
            "a",  # Single character
            "very_long_username_that_might_be_too_long_for_some_systems",
            "user@with#special$chars",
            "user with spaces"
        ])
    ]
    
    try:
        from deviantart_rss import DeviantArtRSSMode
        
        # Create mock objects
        class MockInky:
            def __init__(self):
                self.resolution = (800, 480)
        
        class MockDisplayUtils:
            def create_image_with_palette(self):
                return None
            def get_font(self, size, height):
                return None
            def draw_text_centered(self, draw, text, y, font, color):
                pass
        
        for category, usernames in test_usernames:
            print(f"\n{category}")
            print("-" * 20)
            
            for username in usernames:
                try:
                    config = {
                        'deviantart_rss': {
                            'username': username
                        }
                    }
                    
                    mode = DeviantArtRSSMode(MockInky(), config, MockDisplayUtils())
                    constructed_url = mode._construct_rss_url(username)
                    
                    print(f"  ✓ '{username}' → {constructed_url}")
                    
                except Exception as e:
                    print(f"  ✗ '{username}' → Error: {e}")
        
    except ImportError as e:
        print(f"✗ Failed to import DeviantArtRSSMode: {e}")

def show_migration_guide():
    """Show how to migrate from old URL-based config to new username-based config."""
    print(f"\n{'='*50}")
    print("Migration Guide")
    print("=" * 50)
    
    print("""
OLD CONFIGURATION (URL-based):
{
  "deviantart_rss": {
    "rss_url": "https://backend.deviantart.com/rss.xml?q=gallery:WestOz64",
    "display_time": 15,
    "max_posts": 20,
    "update_interval": 3600,
    "background_color": "auto",
    "saturation": 0.5
  }
}

NEW CONFIGURATION (username-based):
{
  "deviantart_rss": {
    "username": "WestOz64",
    "display_time": 15,
    "max_posts": 20,
    "update_interval": 3600,
    "background_color": "auto",
    "saturation": 0.5
  }
}

MIGRATION STEPS:
1. Remove the "rss_url" field from your config
2. Add a "username" field with the DeviantArt username
3. The URL will be automatically constructed as:
   https://backend.deviantart.com/rss.xml?q=gallery:{username}

BENEFITS:
- Easier to configure (just username instead of full URL)
- Less error-prone (no need to construct URLs manually)
- More user-friendly
- Consistent URL format
""")

if __name__ == "__main__":
    print("DeviantArt Username Configuration Test")
    print("=" * 50)
    
    # Run all tests
    test_url_construction()
    test_username_configurations()
    test_config_file_examples()
    test_username_validation()
    show_migration_guide()
    
    print(f"\n{'='*50}")
    print("Test completed!")
    print("\nTo use the new username-based configuration:")
    print("1. Edit your config.json file")
    print("2. Replace 'rss_url' with 'username' in deviantart_rss section")
    print("3. Set the username to the DeviantArt username you want to follow")
    print("4. The RSS URL will be automatically constructed")
