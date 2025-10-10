#!/usr/bin/env python3
"""
Test script for DeviantArt RSS functionality
Tests the RSS feed parsing and image extraction without requiring the full display setup.
"""

import sys
import os
import requests
import xml.etree.ElementTree as ET
import re
from pathlib import Path

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_deviantart_rss_feed():
    """Test fetching and parsing the DeviantArt RSS feed."""
    rss_url = "https://backend.deviantart.com/rss.xml?q=gallery:WestOz64"
    
    print(f"Testing DeviantArt RSS feed: {rss_url}")
    print("=" * 60)
    
    try:
        # Fetch RSS feed
        print("Fetching RSS feed...")
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        print(f"✓ Successfully fetched RSS feed (status: {response.status_code})")
        
        # Parse RSS XML
        print("Parsing RSS XML...")
        root = ET.fromstring(response.content)
        print("✓ Successfully parsed RSS XML")
        
        # Find all items (posts)
        items = root.findall('.//item')
        print(f"✓ Found {len(items)} posts in RSS feed")
        
        # Extract image URLs from posts
        print("\nExtracting images from posts...")
        new_images = []
        
        for i, item in enumerate(items[:5]):  # Only check first 5 items for testing
            print(f"\nPost {i+1}:")
            
            # Get post title
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else 'Untitled'
            print(f"  Title: {title}")
            
            # Get post description/content
            description_elem = item.find('description')
            if description_elem is not None:
                description = description_elem.text or ""
                
                # Extract image URLs using regex
                img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
                img_matches = re.findall(img_pattern, description, re.IGNORECASE)
                
                print(f"  Found {len(img_matches)} image URLs in description")
                
                for j, img_url in enumerate(img_matches):
                    # Check if it's a valid image URL
                    is_valid = _is_valid_image_url(img_url)
                    status = "✓ VALID" if is_valid else "✗ INVALID (thumbnail/small)"
                    print(f"    {j+1}. {status}: {img_url}")
                    
                    if is_valid:
                        new_images.append({
                            'url': img_url,
                            'post_title': title,
                            'post_link': item.find('link').text if item.find('link') is not None else '',
                        })
            else:
                print("  No description found")
        
        print(f"\n" + "=" * 60)
        print(f"SUMMARY:")
        print(f"Total posts checked: {min(5, len(items))}")
        print(f"Valid images found: {len(new_images)}")
        
        if new_images:
            print(f"\nValid image URLs:")
            for i, img in enumerate(new_images):
                print(f"  {i+1}. {img['url']}")
                print(f"     From: {img['post_title']}")
        else:
            print("No valid images found in the first 5 posts.")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to fetch RSS feed: {e}")
    except ET.ParseError as e:
        print(f"✗ Failed to parse RSS XML: {e}")
    except Exception as e:
        print(f"✗ Error processing RSS feed: {e}")

def _is_valid_image_url(url: str) -> bool:
    """Check if the image URL is valid and not a thumbnail."""
    # Skip very small images (likely thumbnails)
    if any(size in url for size in ['s75x75', 's100x200', 's250x400', '150px', '200h', '350t', '400t']):
        return False
    
    # Skip avatar images
    if 'avatar' in url.lower():
        return False
    
    # Skip very small DeviantArt thumbnails
    if any(size in url for size in ['50x50', '100x100', '150x150']):
        return False
    
    # Must be a valid image URL
    if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
        return False
    
    return True

def test_deviantart_rss_mode():
    """Test the DeviantArtRSSMode class directly."""
    print("\n" + "=" * 60)
    print("TESTING DeviantArtRSSMode CLASS")
    print("=" * 60)
    
    try:
        # Import the module
        from deviantart_rss import DeviantArtRSSMode
        
        # Create a mock configuration
        config = {
            'deviantart_rss': {
                'rss_url': 'https://backend.deviantart.com/rss.xml?q=gallery:WestOz64',
                'display_time': 15,
                'max_posts': 20,
                'update_interval': 3600,
                'background_color': 'auto',
                'saturation': 0.5
            }
        }
        
        # Create mock objects (we won't actually use them for display)
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
        print("Creating DeviantArtRSSMode instance...")
        mode = DeviantArtRSSMode(MockInky(), config, MockDisplayUtils())
        print("✓ Successfully created DeviantArtRSSMode instance")
        
        # Test RSS fetching
        print("Testing RSS image fetching...")
        mode._fetch_rss_images()
        
        if mode.cached_images:
            print(f"✓ Successfully cached {len(mode.cached_images)} images")
            print("Sample cached images:")
            for i, img in enumerate(mode.cached_images[:3]):
                print(f"  {i+1}. {img['url']}")
                print(f"     Title: {img['post_title']}")
        else:
            print("✗ No images were cached")
            
    except ImportError as e:
        print(f"✗ Failed to import DeviantArtRSSMode: {e}")
    except Exception as e:
        print(f"✗ Error testing DeviantArtRSSMode: {e}")

if __name__ == "__main__":
    print("DeviantArt RSS Integration Test")
    print("=" * 60)
    
    # Test 1: Direct RSS feed parsing
    test_deviantart_rss_feed()
    
    # Test 2: DeviantArtRSSMode class
    test_deviantart_rss_mode()
    
    print("\n" + "=" * 60)
    print("Test completed!")

