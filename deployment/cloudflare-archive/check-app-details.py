#!/usr/bin/env python3
"""
Check Cloudflare Access application details
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
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "97bf59a94fce66eee3db3b118c9bb4f1")

# Headers for API requests
headers = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

def get_app_details(app_id):
    """Get detailed information about an app"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps/{app_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['result']
    return None

def get_app_policies(app_id):
    """Get policies for an app"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps/{app_id}/policies",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['result']
    return []

def main():
    # First list all apps
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps",
        headers=headers
    )
    
    if response.status_code == 200:
        apps = response.json()['result']
        
        # Find image2model-app
        for app in apps:
            if app['name'] == 'image2model-app':
                print(f"=== Application: {app['name']} ===")
                print(f"ID: {app['id']}")
                print(f"AUD: {app['aud']}")
                print(f"Domain: {app.get('domain', 'N/A')}")
                print(f"Path: {app.get('path', 'N/A')}")
                print(f"Type: {app.get('type', 'N/A')}")
                print(f"Session Duration: {app.get('session_duration', 'N/A')}")
                
                # Get detailed info
                details = get_app_details(app['id'])
                if details:
                    print(f"\nDetailed Configuration:")
                    print(json.dumps(details, indent=2))
                
                # Get policies
                policies = get_app_policies(app['id'])
                print(f"\nPolicies ({len(policies)}):")
                for policy in policies:
                    print(f"\n  Policy: {policy['name']}")
                    print(f"  Decision: {policy['decision']}")
                    print(f"  Include Rules:")
                    for rule in policy.get('include', []):
                        print(f"    - {json.dumps(rule)}")
                    print(f"  Exclude Rules:")
                    for rule in policy.get('exclude', []):
                        print(f"    - {json.dumps(rule)}")

if __name__ == "__main__":
    main()