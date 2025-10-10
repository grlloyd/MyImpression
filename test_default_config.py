#!/usr/bin/env python3
"""
Test script to verify the default configuration includes all modes
"""

import json
import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_default_config():
    """Test that the default configuration includes all available modes."""
    print("Testing Default Configuration Completeness")
    print("=" * 50)
    
    # Import the main app to get the default config
    try:
        # Import just the config method without initializing the full app
        sys.path.append(os.path.dirname(__file__))
        from main import MyImpressionApp
        
        # Create an instance to get the default config
        app = MyImpressionApp.__new__(MyImpressionApp)  # Create without __init__
        default_config = app._get_default_config()
        
        print("Default configuration generated:")
        print(json.dumps(default_config, indent=2))
        
        # Check what modes are available
        available_modes = ["photo_cycle", "tumblr_rss", "deviantart_rss", "news_feed"]
        
        print(f"\nChecking for all available modes:")
        print("-" * 30)
        
        missing_modes = []
        for mode in available_modes:
            if mode in default_config:
                print(f"✓ {mode}: Found")
            else:
                print(f"✗ {mode}: Missing")
                missing_modes.append(mode)
        
        # Check button mappings
        print(f"\nChecking button mappings:")
        print("-" * 30)
        
        buttons = default_config.get('buttons', {})
        for i in range(1, 5):  # button_1 to button_4
            button_key = f"button_{i}"
            if button_key in buttons:
                mode = buttons[button_key]
                if mode in available_modes:
                    print(f"✓ {button_key}: {mode}")
                else:
                    print(f"✗ {button_key}: {mode} (invalid mode)")
            else:
                print(f"✗ {button_key}: Not mapped")
        
        # Summary
        print(f"\nSummary:")
        print("-" * 30)
        if missing_modes:
            print(f"Missing modes: {', '.join(missing_modes)}")
        else:
            print("✓ All modes are included in default configuration")
        
        return len(missing_modes) == 0
        
    except Exception as e:
        print(f"✗ Error testing default configuration: {e}")
        return False

def show_expected_config():
    """Show what the complete default configuration should look like."""
    print(f"\n{'='*50}")
    print("Expected Complete Default Configuration")
    print("=" * 50)
    
    expected_config = {
        "display": {
            "resolution": [800, 480],
            "dpi": 127,
            "colors": 6,
            "refresh_rate": 30
        },
        "buttons": {
            "button_1": "photo_cycle",
            "button_2": "tumblr_rss", 
            "button_3": "deviantart_rss",
            "button_4": "news_feed"
        },
        "photo_cycle": {
            "folder": "./data/photos",
            "display_time": 10,
            "random_order": False,
            "supported_formats": ["jpg", "jpeg", "png", "webp"],
            "background_color": "white",
            "saturation": 0.5
        },
        "tumblr_rss": {
            "rss_url": "https://handsoffmydinosaur.tumblr.com/rss",
            "display_time": 300,
            "max_posts": 300,
            "update_interval": 86400,
            "background_color": "auto",
            "saturation": 1.0
        },
        "deviantart_rss": {
            "username": "WestOz64",
            "display_time": 15,
            "max_posts": 20,
            "update_interval": 3600,
            "background_color": "auto",
            "saturation": 0.5
        },
        "news_feed": {
            "sources": ["arxiv"],
            "search_terms": ["machine learning", "renewable energy"],
            "max_articles": 5,
            "update_interval": 86400
        }
    }
    
    print("Complete default configuration should include:")
    print(json.dumps(expected_config, indent=2))
    
    print(f"\nAll modes included:")
    for mode in ["photo_cycle", "tumblr_rss", "deviantart_rss", "news_feed"]:
        print(f"  ✓ {mode}")

if __name__ == "__main__":
    print("Default Configuration Test")
    print("=" * 50)
    
    # Test the current default config
    success = test_default_config()
    
    # Show expected config
    show_expected_config()
    
    print(f"\n{'='*50}")
    if success:
        print("✓ Default configuration is complete!")
    else:
        print("✗ Default configuration is missing some modes")
        print("The configuration should include all available modes even if not used")
