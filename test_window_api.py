#!/usr/bin/env python3
"""
Test script for the window control API endpoints.
Run this after starting the GUI application to test window visibility control.
"""

import requests
import time
import json

API_BASE = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, description):
    """Test an API endpoint and print the result."""
    print(f"\n🧪 Testing: {description}")
    print(f"   {method} {API_BASE}{endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{API_BASE}{endpoint}")
        elif method == "DELETE":
            response = requests.delete(f"{API_BASE}{endpoint}")
        
        print(f"   Status: {response.status_code}")
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
        else:
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed - make sure the GUI application is running!")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Test all window control endpoints."""
    print("🎯 Interview Corvus Window Control API Test")
    print("=" * 50)
    
    # Test health check first
    test_endpoint("GET", "/health", "Health check")
    
    print("\n" + "=" * 50)
    print("🪟 Testing Window Control APIs")
    print("=" * 50)
    
    # Test window controls
    test_endpoint("POST", "/window/hide", "Hide window")
    time.sleep(2)  # Wait 2 seconds
    
    test_endpoint("POST", "/window/show", "Show window")
    time.sleep(2)  # Wait 2 seconds
    
    test_endpoint("POST", "/window/toggle", "Toggle window visibility")
    time.sleep(2)  # Wait 2 seconds
    
    test_endpoint("POST", "/window/toggle", "Toggle window visibility again")
    
    print("\n" + "=" * 50)
    print("✅ Window control API tests completed!")
    print("💡 You can also test these endpoints manually:")
    print(f"   curl -X POST {API_BASE}/window/hide")
    print(f"   curl -X POST {API_BASE}/window/show")
    print(f"   curl -X POST {API_BASE}/window/toggle")

if __name__ == "__main__":
    main()
