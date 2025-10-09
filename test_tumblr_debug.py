#!/usr/bin/env python3
"""
Debug script for Tumblr API connection
Run this to test your Tumblr API key and blog access
"""

import requests
import json
import sys

def test_tumblr_api(api_key, blog_name="handsoffmydinosaur"):
    """Test Tumblr API connection and blog access"""
    
    print(f"Testing Tumblr API with blog: {blog_name}")
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key provided")
    print("-" * 50)
    
    # Test 1: Try with .tumblr.com suffix
    print("Test 1: Trying with .tumblr.com suffix")
    try:
        url1 = f"https://api.tumblr.com/v2/blog/{blog_name}.tumblr.com/posts/photo"
        params = {'api_key': api_key, 'limit': 5}
        
        print(f"URL: {url1}")
        response = requests.get(url1, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('response', {}).get('posts', [])
            print(f"✅ Success! Found {len(posts)} posts")
            
            # Count images
            image_count = 0
            for post in posts:
                if 'photos' in post:
                    image_count += len(post['photos'])
                    print(f"  Post {post.get('id', 'unknown')}: {len(post['photos'])} images")
            
            print(f"Total images found: {image_count}")
            
            if image_count > 0:
                # Show first image URL
                for post in posts:
                    if 'photos' in post and post['photos']:
                        first_image = post['photos'][0]['original_size']['url']
                        print(f"First image URL: {first_image}")
                        break
                        
            return True
            
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Try without .tumblr.com suffix
    print("\nTest 2: Trying without .tumblr.com suffix")
    try:
        url2 = f"https://api.tumblr.com/v2/blog/{blog_name}/posts/photo"
        params = {'api_key': api_key, 'limit': 5}
        
        print(f"URL: {url2}")
        response = requests.get(url2, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('response', {}).get('posts', [])
            print(f"✅ Success! Found {len(posts)} posts")
            
            # Count images
            image_count = 0
            for post in posts:
                if 'photos' in post:
                    image_count += len(post['photos'])
                    print(f"  Post {post.get('id', 'unknown')}: {len(post['photos'])} images")
            
            print(f"Total images found: {image_count}")
            return True
            
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Try getting all posts (not just photos)
    print("\nTest 3: Trying to get all posts (not just photos)")
    try:
        url3 = f"https://api.tumblr.com/v2/blog/{blog_name}.tumblr.com/posts"
        params = {'api_key': api_key, 'limit': 10}
        
        print(f"URL: {url3}")
        response = requests.get(url3, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('response', {}).get('posts', [])
            print(f"✅ Success! Found {len(posts)} total posts")
            
            # Check post types
            post_types = {}
            for post in posts:
                post_type = post.get('type', 'unknown')
                post_types[post_type] = post_types.get(post_type, 0) + 1
            
            print("Post types found:")
            for post_type, count in post_types.items():
                print(f"  {post_type}: {count}")
            
            return True
            
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    # Get API key from command line or config
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        # Try to read from config.json
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('tumblr_feed', {}).get('api_key', '')
        except:
            api_key = input("Enter your Tumblr API key: ")
    
    if not api_key or api_key == "your_tumblr_api_key":
        print("❌ No valid API key provided!")
        print("Please provide your Tumblr API key as an argument or update config.json")
        sys.exit(1)
    
    success = test_tumblr_api(api_key)
    
    if success:
        print("\n✅ Tumblr API test completed successfully!")
        print("Your API key and blog access are working correctly.")
    else:
        print("\n❌ Tumblr API test failed!")
        print("Please check your API key and blog name.")
