#!/usr/bin/env python3
"""
Cloudflare Access Application Setup Script
Creates Access applications programmatically for Image2Model
"""

import requests
import json
import sys
import os

# Configuration
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
if not CLOUDFLARE_API_TOKEN:
    print("Error: CLOUDFLARE_API_TOKEN environment variable not set")
    print("Set it with: export CLOUDFLARE_API_TOKEN='your-token'")
    sys.exit(1)

CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"

# Your Cloudflare account ID - we'll fetch this
ACCOUNT_ID = None

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
    
    print(f"Failed to get account ID: {response.status_code}")
    print(response.json())
    sys.exit(1)

def get_zone_id(domain):
    """Get zone ID for the domain"""
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/zones",
        headers=headers,
        params={"name": "pranitlab.com"}
    )
    
    if response.status_code == 200:
        zones = response.json()['result']
        if zones:
            return zones[0]['id']
    
    print(f"Failed to get zone ID: {response.status_code}")
    print(response.json())
    return None

def create_access_application(app_config):
    """Create an Access application"""
    print(f"\nCreating application: {app_config['name']}")
    
    response = requests.post(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/applications",
        headers=headers,
        json=app_config
    )
    
    if response.status_code in [200, 201]:
        result = response.json()['result']
        print(f"✅ Created: {result['name']} (ID: {result['id']})")
        print(f"   AUD: {result['aud']}")
        return result
    else:
        print(f"❌ Failed to create {app_config['name']}: {response.status_code}")
        print(response.json())
        return None

def create_access_policy(app_id, policy_config):
    """Create an Access policy for an application"""
    print(f"  Creating policy: {policy_config['name']}")
    
    response = requests.post(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/applications/{app_id}/policies",
        headers=headers,
        json=policy_config
    )
    
    if response.status_code in [200, 201]:
        print(f"  ✅ Policy created")
        return response.json()['result']
    else:
        print(f"  ❌ Failed to create policy: {response.status_code}")
        print(response.json())
        return None

def main():
    global ACCOUNT_ID
    
    print("=== Cloudflare Access Setup for Image2Model ===\n")
    
    # Get account ID
    ACCOUNT_ID = get_account_id()
    print(f"Account ID: {ACCOUNT_ID}")
    
    # Get zone ID
    zone_id = get_zone_id("pranitlab.com")
    print(f"Zone ID: {zone_id}")
    
    # Application 1: Main Application (Users)
    app1_config = {
        "name": "image2model-app",
        "domain": "image2model.pranitlab.com",
        "type": "self_hosted",
        "session_duration": "24h",
        "auto_redirect_to_identity": False,
        "enable_binding_cookie": True,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "lax",
        "cors_headers": {
            "allowed_methods": ["GET", "POST", "OPTIONS"],
            "allowed_origins": ["https://image2model.pranitlab.com"],
            "allow_credentials": True,
            "max_age": 300
        },
        "allowed_idps": [],  # Allow all configured IdPs
        "custom_deny_message": "Access denied. Please contact pranit.lahoty1@gmail.com for access.",
        "custom_deny_url": ""
    }
    
    app1 = create_access_application(app1_config)
    
    if app1:
        # Create policy for main app
        policy1_config = {
            "name": "Alpha Users",
            "decision": "allow",
            "include": [
                {
                    "email": {"email": "pranit.lahoty1@gmail.com"}
                },
                {
                    "email_domain": {"domain": "gallagherdesign.com"}
                }
            ],
            "require": [],
            "exclude": []
        }
        create_access_policy(app1['id'], policy1_config)
    
    # Application 2: Admin Endpoints
    app2_config = {
        "name": "image2model-admin",
        "domain": "image2model.pranitlab.com",
        "path": "/api/v1/admin",
        "type": "self_hosted",
        "session_duration": "12h",
        "auto_redirect_to_identity": True,
        "enable_binding_cookie": True,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "lax"
    }
    
    app2 = create_access_application(app2_config)
    
    if app2:
        # Create policy for admin app
        policy2_config = {
            "name": "Admin Only",
            "decision": "allow",
            "include": [
                {
                    "email": {"email": "pranit.lahoty1@gmail.com"}
                }
            ],
            "require": [],
            "exclude": []
        }
        create_access_policy(app2['id'], policy2_config)
    
    # Application 3: Flower Monitoring
    app3_config = {
        "name": "image2model-flower",
        "domain": "image2model.pranitlab.com",
        "path": "/flower",
        "type": "self_hosted",
        "session_duration": "12h",
        "auto_redirect_to_identity": True,
        "enable_binding_cookie": True,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "lax"
    }
    
    app3 = create_access_application(app3_config)
    
    if app3:
        # Create policy for monitoring app
        policy3_config = {
            "name": "Monitoring Admin",
            "decision": "allow",
            "include": [
                {
                    "email": {"email": "pranit.lahoty1@gmail.com"}
                }
            ],
            "require": [],
            "exclude": []
        }
        create_access_policy(app3['id'], policy3_config)
    
    print("\n=== Setup Complete ===\n")
    
    if app1:
        print(f"IMPORTANT: Add this to your .env.production file:")
        print(f"CLOUDFLARE_AUD_TAG={app1['aud']}")
        print("\nThen run the deployment script to update your containers.")
    
    print("\n=== Public Endpoints Configuration ===")
    print("The following paths are NOT protected by these applications:")
    print("- /")
    print("- /api/v1/health")
    print("- /api/v1/health/*")
    print("- /api/v1/models/available")
    print("\nAll other endpoints require authentication.")

if __name__ == "__main__":
    main()