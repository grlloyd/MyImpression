#!/usr/bin/env python3
"""
Test script for the new button configuration system
Tests the flexible button-to-mode mapping configuration.
"""

import json
import sys
import os
from pathlib import Path

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_config_parsing():
    """Test parsing different button configurations."""
    print("Testing Button Configuration System")
    print("=" * 50)
    
    # Test configurations
    test_configs = [
        {
            "name": "Default Configuration",
            "config": {
                "buttons": {
                    "button_1": "photo_cycle",
                    "button_2": "tumblr_rss", 
                    "button_3": "deviantart_rss",
                    "button_4": "news_feed"
                }
            }
        },
        {
            "name": "Custom Configuration - DeviantArt on Button 1",
            "config": {
                "buttons": {
                    "button_1": "deviantart_rss",
                    "button_2": "photo_cycle",
                    "button_3": "tumblr_rss", 
                    "button_4": "news_feed"
                }
            }
        },
        {
            "name": "Custom Configuration - Only 2 Buttons",
            "config": {
                "buttons": {
                    "button_1": "deviantart_rss",
                    "button_3": "photo_cycle"
                }
            }
        },
        {
            "name": "Invalid Configuration - Unknown Mode",
            "config": {
                "buttons": {
                    "button_1": "invalid_mode",
                    "button_2": "deviantart_rss"
                }
            }
        }
    ]
    
    # Available modes
    available_modes = ["photo_cycle", "tumblr_rss", "deviantart_rss", "news_feed"]
    
    for test_config in test_configs:
        print(f"\n{test_config['name']}:")
        print("-" * 30)
        
        config = test_config['config']
        buttons = config.get('buttons', {})
        
        # Test each button configuration
        for button_key, mode_name in buttons.items():
            # Extract button number
            try:
                button_num = int(button_key.split('_')[1]) - 1  # Convert button_1 to 0, etc.
                button_letter = chr(ord('A') + button_num)  # Convert 0 to A, 1 to B, etc.
            except (ValueError, IndexError):
                print(f"  ✗ Invalid button key: {button_key}")
                continue
            
            # Check if mode exists
            if mode_name in available_modes:
                print(f"  ✓ {button_key} ({button_letter}) → {mode_name}")
            else:
                print(f"  ✗ {button_key} ({button_letter}) → {mode_name} (INVALID MODE)")
        
        # Show unmapped buttons
        mapped_buttons = set(buttons.keys())
        all_buttons = {"button_1", "button_2", "button_3", "button_4"}
        unmapped = all_buttons - mapped_buttons
        
        if unmapped:
            print(f"  Unmapped buttons: {', '.join(sorted(unmapped))}")

def test_button_mapping_logic():
    """Test the button mapping logic used in the application."""
    print(f"\n{'='*50}")
    print("Testing Button Mapping Logic")
    print("=" * 50)
    
    # Simulate the button mapping logic from the application
    def simulate_button_press(button_letter, config):
        """Simulate a button press with the given configuration."""
        # Map button letter to button number (A=0, B=1, C=2, D=3)
        button_map = {"A": 0, "B": 1, "C": 2, "D": 3}
        button_num = button_map.get(button_letter)
        
        if button_num is not None:
            # Get the target mode from configuration
            button_config_key = f"button_{button_num + 1}"  # button_1, button_2, etc.
            target_mode = config.get("buttons", {}).get(button_config_key)
            
            if target_mode is None:
                return f"No mode configured for {button_config_key}"
            
            available_modes = ["photo_cycle", "tumblr_rss", "deviantart_rss", "news_feed"]
            if target_mode not in available_modes:
                return f"Unknown mode '{target_mode}' configured for {button_config_key}"
            
            return f"Button {button_letter} → {target_mode}"
        else:
            return f"Unknown button: {button_letter}"
    
    # Test configurations
    test_configs = [
        {
            "name": "Default Config",
            "config": {
                "buttons": {
                    "button_1": "photo_cycle",
                    "button_2": "tumblr_rss", 
                    "button_3": "deviantart_rss",
                    "button_4": "news_feed"
                }
            }
        },
        {
            "name": "Custom Config - DeviantArt First",
            "config": {
                "buttons": {
                    "button_1": "deviantart_rss",
                    "button_2": "photo_cycle",
                    "button_3": "tumblr_rss", 
                    "button_4": "news_feed"
                }
            }
        }
    ]
    
    for test_config in test_configs:
        print(f"\n{test_config['name']}:")
        print("-" * 20)
        
        config = test_config['config']
        
        # Test all buttons A-D
        for button in ['A', 'B', 'C', 'D']:
            result = simulate_button_press(button, config)
            print(f"  {result}")

def test_config_file_creation():
    """Test creating a configuration file with the new format."""
    print(f"\n{'='*50}")
    print("Testing Configuration File Creation")
    print("=" * 50)
    
    # Create a sample configuration
    sample_config = {
        "display": {
            "resolution": [800, 480],
            "dpi": 127,
            "colors": 6,
            "refresh_rate": 30
        },
        "buttons": {
            "button_1": "deviantart_rss",
            "button_2": "photo_cycle",
            "button_3": "tumblr_rss", 
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
            "rss_url": "https://backend.deviantart.com/rss.xml?q=gallery:WestOz64",
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
    
    # Save to a test file
    test_config_path = Path("test_config.json")
    try:
        with open(test_config_path, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"✓ Created test configuration file: {test_config_path}")
        
        # Read it back and verify
        with open(test_config_path, 'r') as f:
            loaded_config = json.load(f)
        
        print("✓ Successfully loaded configuration file")
        print("Button mappings:")
        for button_key, mode in loaded_config.get('buttons', {}).items():
            print(f"  {button_key}: {mode}")
            
    except Exception as e:
        print(f"✗ Error creating/loading config file: {e}")
    finally:
        # Clean up test file
        if test_config_path.exists():
            test_config_path.unlink()
            print("✓ Cleaned up test configuration file")

def show_configuration_examples():
    """Show examples of different configuration setups."""
    print(f"\n{'='*50}")
    print("Configuration Examples")
    print("=" * 50)
    
    examples = [
        {
            "name": "DeviantArt Focused Setup",
            "description": "Put DeviantArt RSS on multiple buttons for easy access",
            "config": {
                "button_1": "deviantart_rss",
                "button_2": "deviantart_rss", 
                "button_3": "photo_cycle",
                "button_4": "tumblr_rss"
            }
        },
        {
            "name": "Photo Gallery Setup",
            "description": "Focus on photo cycling with RSS feeds as secondary",
            "config": {
                "button_1": "photo_cycle",
                "button_2": "photo_cycle", 
                "button_3": "deviantart_rss",
                "button_4": "tumblr_rss"
            }
        },
        {
            "name": "RSS Feed Setup",
            "description": "All buttons for different RSS feeds",
            "config": {
                "button_1": "tumblr_rss",
                "button_2": "deviantart_rss", 
                "button_3": "news_feed",
                "button_4": "photo_cycle"
            }
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}:")
        print(f"  {example['description']}")
        print("  Button mappings:")
        for button_key, mode in example['config'].items():
            button_num = int(button_key.split('_')[1])
            button_letter = chr(ord('A') + button_num - 1)
            print(f"    Button {button_letter} ({button_key}): {mode}")

if __name__ == "__main__":
    print("Button Configuration System Test")
    print("=" * 50)
    
    # Run all tests
    test_config_parsing()
    test_button_mapping_logic()
    test_config_file_creation()
    show_configuration_examples()
    
    print(f"\n{'='*50}")
    print("Test completed!")
    print("\nTo use the new configuration system:")
    print("1. Edit your config.json file")
    print("2. Set button mappings like: 'button_1': 'deviantart_rss'")
    print("3. Available modes: photo_cycle, tumblr_rss, deviantart_rss, news_feed")
    print("4. Button mapping: A=button_1, B=button_2, C=button_3, D=button_4")

