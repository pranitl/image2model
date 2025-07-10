#!/usr/bin/env python3
"""
Cloudflare Access Application Setup Script V2
Creates Access applications programmatically for Image2Model
"""

import requests
import json
import sys
import os

# Configuration from environment
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
if not CLOUDFLARE_API_TOKEN:
    print("Error: CLOUDFLARE_API_TOKEN environment variable not set")
    sys.exit(1)

CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "97bf59a94fce66eee3db3b118c9bb4f1")

# Headers for API requests
headers = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

def list_existing_applications():
    """List existing Access applications"""
    print("Checking existing applications...")
    
    response = requests.get(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps",
        headers=headers
    )
    
    if response.status_code == 200:
        apps = response.json()['result']
        if apps:
            print(f"\nFound {len(apps)} existing application(s):")
            for app in apps:
                print(f"  - {app['name']} ({app.get('domain', 'N/A')})")
                if 'aud' in app:
                    print(f"    AUD: {app['aud']}")
        return apps
    else:
        print(f"Failed to list applications: {response.status_code}")
        print(response.json())
        return []

def create_access_application(app_config):
    """Create an Access application"""
    print(f"\nCreating application: {app_config['name']}")
    
    response = requests.post(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps",
        headers=headers,
        json=app_config
    )
    
    if response.status_code in [200, 201]:
        result = response.json()['result']
        print(f"✅ Created: {result['name']}")
        print(f"   ID: {result['id']}")
        print(f"   AUD: {result['aud']}")
        return result
    else:
        print(f"❌ Failed to create {app_config['name']}: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return None

def create_access_policy(app_id, policy_config):
    """Create an Access policy for an application"""
    print(f"  Creating policy: {policy_config['name']}")
    
    response = requests.post(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps/{app_id}/policies",
        headers=headers,
        json=policy_config
    )
    
    if response.status_code in [200, 201]:
        print(f"  ✅ Policy created")
        return response.json()['result']
    else:
        print(f"  ❌ Failed to create policy: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return None

def delete_application(app_id, app_name):
    """Delete an existing application"""
    print(f"Deleting application: {app_name}")
    
    response = requests.delete(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps/{app_id}",
        headers=headers
    )
    
    if response.status_code in [200, 204]:
        print(f"✅ Deleted: {app_name}")
        return True
    else:
        print(f"❌ Failed to delete {app_name}: {response.status_code}")
        return False

def main():
    print("=== Cloudflare Access Setup for Image2Model ===\n")
    
    # Check existing applications
    existing_apps = list_existing_applications()
    
    # Check if we need to clean up
    image2model_apps = []
    if existing_apps:
        for app in existing_apps:
            if app['name'] in ['image2model-app', 'image2model-admin', 'image2model-flower']:
                image2model_apps.append(app)
                print(f"\n⚠️  Application '{app['name']}' already exists.")
                print(f"   AUD: {app.get('aud', 'N/A')}")
                
    # Return the existing AUD if the main app exists
    for app in image2model_apps:
        if app['name'] == 'image2model-app':
            print(f"\n=== Existing Configuration ===")
            print(f"The main application already exists with AUD: {app['aud']}")
            print(f"\nAdd this to your .env.production file:")
            print(f"CLOUDFLARE_AUD_TAG={app['aud']}")
            print("\nTo recreate applications, first delete them in the Cloudflare dashboard.")
            return
    
    print("\n=== Creating New Applications ===")
    
    # Application 1: Main Application (Users)
    app1_config = {
        "name": "image2model-app",
        "domain": "image2model.pranitlab.com",
        "type": "self_hosted",
        "session_duration": "24h",
        "auto_redirect_to_identity": False,
        "allow_authenticate_via_warp": False,
        "app_launcher_visible": True,
        "enable_binding_cookie": True,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "lax",
        "skip_interstitial": True,
        "cors_headers": {
            "allowed_methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "allowed_origins": ["https://image2model.pranitlab.com"],
            "allow_credentials": True,
            "max_age": 300
        },
        "custom_deny_message": "Access denied. Please contact pranit.lahoty1@gmail.com for access.",
        "service_auth_401_redirect": False
    }
    
    app1 = create_access_application(app1_config)
    
    if app1:
        # Create policy for main app
        policy1_config = {
            "name": "Alpha Users",
            "decision": "allow",
            "precedence": 1,
            "include": [
                {
                    "email": {"email": "pranit.lahoty1@gmail.com"}
                },
                {
                    "email_domain": {"domain": "gallagherdesign.com"}
                }
            ],
            "exclude": [],
            "require": []
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
        "allow_authenticate_via_warp": False,
        "app_launcher_visible": False,
        "enable_binding_cookie": True,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "strict",
        "skip_interstitial": True,
        "custom_deny_message": "Admin access only.",
        "service_auth_401_redirect": False
    }
    
    app2 = create_access_application(app2_config)
    
    if app2:
        # Create policy for admin app
        policy2_config = {
            "name": "Admin Only",
            "decision": "allow",
            "precedence": 1,
            "include": [
                {
                    "email": {"email": "pranit.lahoty1@gmail.com"}
                }
            ],
            "exclude": [],
            "require": []
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
        "allow_authenticate_via_warp": False,
        "app_launcher_visible": True,
        "enable_binding_cookie": True,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "strict",
        "skip_interstitial": True,
        "custom_deny_message": "Monitoring access restricted.",
        "service_auth_401_redirect": False
    }
    
    app3 = create_access_application(app3_config)
    
    if app3:
        # Create policy for monitoring app
        policy3_config = {
            "name": "Monitoring Admin",
            "decision": "allow",
            "precedence": 1,
            "include": [
                {
                    "email": {"email": "pranit.lahoty1@gmail.com"}
                }
            ],
            "exclude": [],
            "require": []
        }
        create_access_policy(app3['id'], policy3_config)
    
    print("\n=== Setup Complete ===\n")
    
    if app1:
        print(f"IMPORTANT: Add this to your .env.production file:")
        print(f"CLOUDFLARE_AUD_TAG={app1['aud']}")
        print("\nThen run the deployment script to update your containers.")
    
    print("\n=== Public Endpoints Configuration ===")
    print("The following paths will remain public:")
    print("- /")
    print("- /api/v1/health")
    print("- /api/v1/health/*")
    print("- /api/v1/models/available")
    print("\nAll other endpoints require authentication.")
    
    print("\n=== Next Steps ===")
    print("1. Copy the AUD tag to your .env.production file")
    print("2. SSH into your server: ssh root@66.228.60.251")
    print("3. Update .env.production with the AUD tag")
    print("4. Run: ./deploy-cloudflare-auth.sh")
    print("5. Test authentication with: ./test-cloudflare-auth.sh")

if __name__ == "__main__":
    main()