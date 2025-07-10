#!/usr/bin/env python3
"""
Get Cloudflare account info from zones
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

def main():
    # Get zone details to find account ID
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/zones",
        headers=headers,
        params={"name": "pranitlab.com"}
    )
    
    if response.status_code == 200:
        zones = response.json()['result']
        if zones:
            zone = zones[0]
            print(f"Zone: {zone['name']}")
            print(f"Zone ID: {zone['id']}")
            print(f"Account ID: {zone['account']['id']}")
            print(f"Account Name: {zone['account']['name']}")
            
            # Try to list Access applications
            account_id = zone['account']['id']
            print(f"\nTrying to access applications for account: {account_id}")
            
            apps_response = requests.get(
                f"{CLOUDFLARE_API_BASE}/accounts/{account_id}/access/applications",
                headers=headers
            )
            
            print(f"Access Applications Response: {apps_response.status_code}")
            if apps_response.status_code != 200:
                print(json.dumps(apps_response.json(), indent=2))
            else:
                apps = apps_response.json()['result']
                print(f"Found {len(apps)} Access application(s)")
                
    else:
        print(f"Failed to get zones: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    main()