#!/usr/bin/env python3
"""
Check existing Cloudflare Access applications
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

def get_account_id():
    """Get the account ID from Cloudflare"""
    response = requests.get(f"{CLOUDFLARE_API_BASE}/accounts", headers=headers)
    
    if response.status_code == 200:
        accounts = response.json()['result']
        if accounts:
            return accounts[0]['id']
    return None

def list_access_applications(account_id):
    """List all Access applications"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{account_id}/access/applications",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['result']
    else:
        print(f"Failed to list applications: {response.status_code}")
        print(response.json())
        return []

def get_application_policies(account_id, app_id):
    """Get policies for an application"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{account_id}/access/applications/{app_id}/policies",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()['result']
    return []

def main():
    print("=== Cloudflare Access Applications Check ===\n")
    
    # Get account ID
    account_id = get_account_id()
    if not account_id:
        print("Failed to get account ID")
        return
    
    print(f"Account ID: {account_id}\n")
    
    # List applications
    apps = list_access_applications(account_id)
    
    if not apps:
        print("No Access applications found.")
        return
    
    print(f"Found {len(apps)} application(s):\n")
    
    image2model_app = None
    
    for app in apps:
        print(f"Application: {app['name']}")
        print(f"  ID: {app['id']}")
        print(f"  AUD: {app['aud']}")
        print(f"  Domain: {app.get('domain', 'N/A')}")
        print(f"  Path: {app.get('path', '/')}")
        print(f"  Type: {app['type']}")
        print(f"  Session Duration: {app.get('session_duration', 'N/A')}")
        
        # Get policies
        policies = get_application_policies(account_id, app['id'])
        if policies:
            print(f"  Policies:")
            for policy in policies:
                print(f"    - {policy['name']} ({policy['decision']})")
        
        print()
        
        # Check if this is our main app
        if app['name'] == 'image2model-app':
            image2model_app = app
    
    if image2model_app:
        print("\n=== Configuration for .env.production ===")
        print(f"CLOUDFLARE_AUD_TAG={image2model_app['aud']}")

if __name__ == "__main__":
    main()