#!/usr/bin/env python3
"""
Verify Cloudflare API token permissions
"""

import requests
import json
import os
import sys

# Configuration
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
if not CLOUDFLARE_API_TOKEN:
    print("Error: CLOUDFLARE_API_TOKEN environment variable not set")
    print("Set it with: export CLOUDFLARE_API_TOKEN='your-token'")
    sys.exit(1)

CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

def verify_token():
    """Verify the API token"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/user/tokens/verify",
        headers=headers
    )
    
    print("Token Verification:")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 200

def get_token_permissions():
    """Get current token permissions"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/user",
        headers=headers
    )
    
    print("\nUser Info:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()['result']
        print(f"Email: {user_data.get('email', 'N/A')}")
        print(f"ID: {user_data.get('id', 'N/A')}")

def test_zones_access():
    """Test access to zones"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/zones",
        headers=headers
    )
    
    print("\nZones Access:")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        zones = response.json()['result']
        print(f"Found {len(zones)} zone(s)")
        for zone in zones:
            print(f"  - {zone['name']} (ID: {zone['id']})")

def main():
    print("=== Cloudflare API Token Verification ===\n")
    
    # Verify token
    if verify_token():
        print("\n✅ Token is valid")
    else:
        print("\n❌ Token is invalid")
        return
    
    # Get permissions
    get_token_permissions()
    
    # Test zones access
    test_zones_access()
    
    print("\n=== Required Permissions for Access ===")
    print("Your token needs these permissions:")
    print("- Account:Cloudflare Access:Edit")
    print("- Zone:Zone:Read")
    print("\nTo create a proper token:")
    print("1. Go to https://dash.cloudflare.com/profile/api-tokens")
    print("2. Create a Custom Token with:")
    print("   - Account → Cloudflare Access → Edit")
    print("   - Zone → Zone → Read")
    print("   - Include → All accounts/zones or specific ones")

if __name__ == "__main__":
    main()