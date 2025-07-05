#!/usr/bin/env python3
"""Test authentication implementation for image2model API"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(name, method, url, headers=None, data=None, files=None):
    """Test an endpoint and print the results"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Method: {method} {url}")
    if headers:
        print(f"Headers: {headers}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=data, files=files)
        else:
            print(f"Unsupported method: {method}")
            return
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code in [401, 403]:
            print(f"Auth Error Response: {response.text}")
        elif response.status_code == 422:
            print(f"Validation Error: {response.text}")
        else:
            try:
                print(f"Response Body: {response.json()}")
            except:
                print(f"Response Text: {response.text[:200]}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("Testing Image2Model Authentication System")
    print("=" * 80)
    
    # Test 1: Upload endpoint without auth
    print("\n1. Testing upload endpoint without authentication:")
    test_endpoint(
        "Upload without auth",
        "POST",
        f"{BASE_URL}/upload/image",
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
    )
    
    # Test 2: Upload endpoint with invalid Bearer token
    print("\n2. Testing upload endpoint with invalid Bearer token:")
    test_endpoint(
        "Upload with invalid auth",
        "POST", 
        f"{BASE_URL}/upload/image",
        headers={"Authorization": "Bearer invalid-token"},
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
    )
    
    # Test 3: Upload endpoint with Bearer token but no prefix
    print("\n3. Testing upload endpoint with token but no Bearer prefix:")
    test_endpoint(
        "Upload with malformed auth",
        "POST",
        f"{BASE_URL}/upload/image", 
        headers={"Authorization": "invalid-token"},
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
    )
    
    # Test 4: Admin endpoint without auth
    print("\n4. Testing admin endpoint without authentication:")
    test_endpoint(
        "Admin disk-usage without auth",
        "GET",
        f"{BASE_URL}/admin/disk-usage"
    )
    
    # Test 5: Admin endpoint with regular API key (if it were set)
    print("\n5. Testing admin endpoint with regular API key:")
    test_endpoint(
        "Admin disk-usage with regular key",
        "GET",
        f"{BASE_URL}/admin/disk-usage",
        headers={"Authorization": "Bearer regular-api-key"}
    )
    
    # Test 6: Download endpoint (should work without auth)
    print("\n6. Testing download endpoint without authentication:")
    test_endpoint(
        "Download without auth",
        "GET",
        f"{BASE_URL}/download/test-job-id/all"
    )
    
    # Test 7: Download endpoint with auth
    print("\n7. Testing download endpoint with authentication:")
    test_endpoint(
        "Download with auth",
        "GET",
        f"{BASE_URL}/download/test-job-id/all",
        headers={"Authorization": "Bearer some-api-key"}
    )
    
    # Test 8: Batch upload endpoint without auth
    print("\n8. Testing batch upload endpoint without authentication:")
    test_endpoint(
        "Batch upload without auth",
        "POST",
        f"{BASE_URL}/upload/",
        files=[("files", ("test1.jpg", b"fake image 1", "image/jpeg")),
               ("files", ("test2.jpg", b"fake image 2", "image/jpeg"))]
    )
    
    # Test 9: Get upload status (no auth required based on code)
    print("\n9. Testing get upload status endpoint:")
    test_endpoint(
        "Get upload status",
        "GET",
        f"{BASE_URL}/upload/status/test-file-id"
    )

if __name__ == "__main__":
    main()