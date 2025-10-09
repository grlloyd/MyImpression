#!/usr/bin/env python3
"""
Debug script for Tumblr RSS feed
Run this to test RSS feed parsing and image extraction
"""

import requests
import xml.etree.ElementTree as ET
import re

def test_rss_feed(rss_url="https://handsoffmydinosaur.tumblr.com/rss"):
    """Test RSS feed parsing and image extraction"""
    
    print(f"Testing RSS feed: {rss_url}")
    print("-" * 50)
    
    try:
        # Fetch RSS feed
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        print(f"✅ RSS feed fetched successfully (status: {response.status_code})")
        
        # Parse RSS XML
        root = ET.fromstring(response.content)
        print("✅ RSS XML parsed successfully")
        
        # Find all items (posts)
        items = root.findall('.//item')
        print(f"✅ Found {len(items)} posts in RSS feed")
        
        # Extract image URLs from posts
        all_images = []
        for i, item in enumerate(items[:5]):  # Check first 5 posts
            # Get post title
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else f"Post {i+1}"
            
            # Get post description/content
            description_elem = item.find('description')
            if description_elem is not None:
                description = description_elem.text or ""
                
                # Extract image URLs using regex
                img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
                img_matches = re.findall(img_pattern, description, re.IGNORECASE)
                
                print(f"\nPost: {title}")
                print(f"  Found {len(img_matches)} image(s)")
                
                for j, img_url in enumerate(img_matches):
                    # Filter out small images
                    is_valid = not any(size in img_url for size in ['s75x75', 's100x200', 's250x400'])
                    status = "✅ Valid" if is_valid else "❌ Too small"
                    print(f"    {j+1}. {status}: {img_url}")
                    
                    if is_valid:
                        all_images.append(img_url)
        
        print(f"\n📊 Summary:")
        print(f"  Total posts checked: {min(5, len(items))}")
        print(f"  Valid images found: {len(all_images)}")
        
        if all_images:
            print(f"\n🖼️  Sample valid image URLs:")
            for i, url in enumerate(all_images[:3]):
                print(f"  {i+1}. {url}")
        
        return len(all_images) > 0
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch RSS feed: {e}")
        return False
    except ET.ParseError as e:
        print(f"❌ Failed to parse RSS XML: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_rss_feed()
    
    if success:
        print("\n✅ RSS feed test completed successfully!")
        print("The RSS feed contains images and should work with the display system.")
    else:
        print("\n❌ RSS feed test failed!")
        print("Please check the RSS feed URL and network connection.")
