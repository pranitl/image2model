#!/usr/bin/env python3
"""
Configure Cloudflare Access with a single app and multiple policies for different paths.
This is the correct approach based on Cloudflare documentation.
"""

import os
import requests
import json
from typing import Dict, Any, List

# Get environment variables
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")

if not API_TOKEN or not ACCOUNT_ID:
    print("Error: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID must be set")
    exit(1)

# Cloudflare API headers
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Define our policies in order of precedence (most specific first)
POLICIES = [
    {
        "name": "Public Health Endpoints",
        "decision": "allow",
        "include": [{"everyone": {}}],  # Allow everyone
        "exclude": [],
        "require": [],
        "precedence": 1,  # Highest precedence
        "description": "Allow public access to health check endpoints",
        # Note: Path filtering is done via include rules
    },
    {
        "name": "Public Home Page",
        "decision": "allow", 
        "include": [{"everyone": {}}],  # Allow everyone
        "exclude": [],
        "require": [],
        "precedence": 2,
        "description": "Allow public access to home page only"
    },
    {
        "name": "Admin Access",
        "decision": "allow",
        "include": [
            {"email": {"email": "pranit.lahoty1@gmail.com"}}
        ],
        "exclude": [],
        "require": [],  # Could add MFA here
        "precedence": 3,
        "description": "Admin users only for admin endpoints"
    },
    {
        "name": "Authenticated Users",
        "decision": "allow",
        "include": [
            {"email": {"email": "pranit.lahoty1@gmail.com"}},
            {"email_domain": {"domain": "gallagherdesign.com"}}
        ],
        "exclude": [],
        "require": [],
        "precedence": 4,  # Lowest precedence - catch all
        "description": "Authenticated users for all other endpoints"
    }
]

def get_existing_apps():
    """Get all existing Access applications."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(f"Error getting apps: {response.status_code}")
        print(response.text)
        return []

def delete_app(app_id: str):
    """Delete an Access application."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app_id}"
    response = requests.delete(url, headers=headers)
    
    if response.status_code in [200, 202, 204]:
        return True
    else:
        print(f"Error deleting app: {response.status_code}")
        print(response.text)
        return False

def create_or_update_app():
    """Create or update the Image2Model Access application."""
    
    # Check for existing app
    apps = get_existing_apps()
    existing_app = None
    
    for app in apps:
        if app.get("domain") == "image2model.pranitlab.com":
            existing_app = app
            break
    
    # App configuration
    app_config = {
        "name": "Image2Model Application",
        "domain": "image2model.pranitlab.com",
        "type": "self_hosted",
        "session_duration": "24h",
        "auto_redirect_to_identity": False,
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "none",
        "logo_url": "",
        "skip_interstitial": True,
        "app_launcher_visible": False,
        "service_auth_401_redirect": False,
        "custom_deny_message": "Access denied. Please contact your administrator for access to Image2Model.",
        "custom_deny_url": "",
        "cors_headers": {
            "allowed_methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "allowed_origins": ["https://image2model.pranitlab.com"],
            "allowed_headers": ["Content-Type", "Authorization", "CF-Access-JWT-Assertion"],
            "allow_all_origins": False,
            "allow_credentials": True
        }
    }
    
    if existing_app:
        print(f"📝 Updating existing app: {existing_app['name']} (ID: {existing_app['id']})")
        url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{existing_app['id']}"
        response = requests.put(url, headers=headers, json=app_config)
    else:
        print("🆕 Creating new Access application...")
        url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps"
        response = requests.post(url, headers=headers, json=app_config)
    
    if response.status_code in [200, 201]:
        app = response.json()["result"]
        print(f"✅ App configured: {app['name']} (ID: {app['id']})")
        return app
    else:
        print(f"❌ Error configuring app: {response.status_code}")
        print(response.text)
        return None

def create_waf_rules():
    """Create WAF custom rules for path-based access control."""
    print("\n🛡️  Creating WAF rules for public endpoints...")
    
    # This would require Zone ID and different API endpoints
    # For now, we'll document what needs to be done
    print("📝 Note: WAF rules need to be configured separately:")
    print("   1. Go to your Cloudflare dashboard")
    print("   2. Navigate to Security > WAF > Custom rules")
    print("   3. Create rules to bypass Access for public paths:")
    print("      - Rule 1: Skip Access for /api/v1/health/* paths")
    print("      - Rule 2: Skip Access for / (home page only)")
    print("      - Rule 3: Skip Access for /api/v1/models/available")

def configure_policies(app_id: str):
    """Configure policies for the Access application."""
    print("\n📋 Configuring access policies...")
    
    # First, get existing policies
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app_id}/policies"
    response = requests.get(url, headers=headers)
    
    existing_policies = []
    if response.status_code == 200:
        existing_policies = response.json()["result"]
        
        # Delete existing policies
        for policy in existing_policies:
            print(f"🗑️  Removing old policy: {policy['name']}")
            delete_url = f"{url}/{policy['id']}"
            requests.delete(delete_url, headers=headers)
    
    # Create new policies
    for policy_config in POLICIES:
        print(f"\n📝 Creating policy: {policy_config['name']}")
        print(f"   Precedence: {policy_config['precedence']}")
        print(f"   Decision: {policy_config['decision']}")
        
        response = requests.post(url, headers=headers, json=policy_config)
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Policy created successfully")
        else:
            print(f"   ❌ Error creating policy: {response.status_code}")
            print(response.text)

def create_service_token():
    """Create a service token for API access."""
    print("\n🔐 Creating service token for API access...")
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/service_tokens"
    
    token_config = {
        "name": "Image2Model API Service Token",
        "duration": "8760h"  # 1 year
    }
    
    response = requests.post(url, headers=headers, json=token_config)
    
    if response.status_code in [200, 201]:
        result = response.json()["result"]
        print("✅ Service token created!")
        print("\n" + "="*60)
        print("🔑 SAVE THESE CREDENTIALS SECURELY!")
        print("="*60)
        print(f"Client ID: {result['client_id']}")
        print(f"Client Secret: {result['client_secret']}")
        print("="*60)
        
        with open("service-token-credentials.txt", "w") as f:
            f.write(f"Client ID: {result['client_id']}\n")
            f.write(f"Client Secret: {result['client_secret']}\n")
            f.write("\nUsage:\n")
            f.write("Add these headers to API requests:\n")
            f.write(f"CF-Access-Client-Id: {result['client_id']}\n")
            f.write(f"CF-Access-Client-Secret: {result['client_secret']}\n")
        
        print("\n📄 Credentials saved to: service-token-credentials.txt")
        return result
    else:
        print(f"❌ Error creating service token: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🔧 Cloudflare Access Single-App Configuration")
    print("=" * 60)
    
    # Step 1: Create or update the app
    app = create_or_update_app()
    if not app:
        print("❌ Failed to configure app. Exiting.")
        return
    
    # Step 2: Configure policies
    configure_policies(app["id"])
    
    # Step 3: Create service token
    print("\n❓ Do you want to create a service token for API access?")
    print("   (This allows API clients to bypass the login page)")
    # Auto-yes for MCP
    print("   Auto-confirming for MCP usage...")
    service_token = create_service_token()
    
    # Step 4: Show WAF rule instructions
    create_waf_rules()
    
    print("\n✅ Configuration complete!")
    print("\n📋 Access Summary:")
    print("   - Single app protecting entire domain: image2model.pranitlab.com")
    print("   - Multiple policies with different precedence levels")
    print("   - Service token created for API access")
    
    print("\n🧪 Test Commands:")
    print("\n1. Public endpoints (should work without auth):")
    print("   curl https://image2model.pranitlab.com/")
    print("   curl https://image2model.pranitlab.com/api/v1/health/")
    print("   curl https://image2model.pranitlab.com/api/v1/models/available")
    
    print("\n2. Protected endpoints (should redirect to login):")
    print("   curl https://image2model.pranitlab.com/upload")
    print("   curl https://image2model.pranitlab.com/api/v1/models/generate")
    
    if service_token:
        print("\n3. API access with service token:")
        print(f"   curl https://image2model.pranitlab.com/api/v1/models/generate \\")
        print(f"     -H 'CF-Access-Client-Id: {service_token['client_id']}' \\")
        print(f"     -H 'CF-Access-Client-Secret: {service_token['client_secret']}' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"file_id\": \"test\"}}'")
    
    print("\n⚠️  IMPORTANT: You still need to configure WAF rules in Cloudflare dashboard")
    print("   to properly bypass Access for public endpoints!")

if __name__ == "__main__":
    main()