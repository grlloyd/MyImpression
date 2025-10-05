#!/usr/bin/env python3
"""
Setup script for MyImpression
Creates necessary directories and initial configuration.
"""

import json
import os
from pathlib import Path


def create_directories():
    """Create necessary directories."""
    directories = [
        "data/photos",
        "data/cache", 
        "assets/fonts",
        "assets/icons"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")


def create_default_config():
    """Create default configuration file."""
    config = {
        "display": {
            "resolution": [800, 480],
            "dpi": 127,
            "colors": 6,
            "refresh_rate": 30
        },
        "buttons": {
            "A": "photo_cycle",
            "B": "weather",
            "C": "solar_monitor", 
            "D": "news_feed"
        },
        "photo_cycle": {
            "folder": "./data/photos",
            "display_time": 10,
            "random_order": False,
            "supported_formats": ["jpg", "jpeg", "png", "webp"],
            "background_color": "white"
        },
        "weather": {
            "api_key": "your_openweathermap_key",
            "location": "London, UK",
            "units": "metric",
            "update_interval": 1800
        },
        "solar_monitor": {
            "api_endpoint": "https://monitoringapi.solaredge.com",
            "site_id": "your_site_id",
            "api_key": "your_solaredge_key",
            "update_interval": 300
        },
        "news_feed": {
            "sources": ["arxiv"],
            "search_terms": ["machine learning", "renewable energy"],
            "max_articles": 5,
            "update_interval": 86400
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("Created default configuration: config.json")


def create_sample_photos_info():
    """Create a README file for the photos directory."""
    photos_readme = """# Photos Directory

Place your photos here for the photo cycle mode.

## Supported Formats
- JPG/JPEG
- PNG  
- WebP

## Recommendations
- Use high-quality images for best display results
- Images will be automatically resized to 800x480
- Aspect ratio will be preserved
- White background will be used for transparent images

## File Organization
You can organize photos in subdirectories - the system will find them recursively.
"""
    
    with open("data/photos/README.md", "w") as f:
        f.write(photos_readme)
    
    print("Created photos directory info: data/photos/README.md")


def main():
    """Main setup function."""
    print("MyImpression Setup")
    print("=" * 20)
    
    # Create directories
    print("\nCreating directories...")
    create_directories()
    
    # Create configuration
    print("\nCreating configuration...")
    create_default_config()
    
    # Create sample photos info
    print("\nSetting up photos directory...")
    create_sample_photos_info()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Add some photos to the data/photos/ directory")
    print("2. Edit config.json to customize settings")
    print("3. Run: python main.py")


if __name__ == "__main__":
    main()
