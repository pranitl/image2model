#!/usr/bin/env python3
"""
Configure Cloudflare Access with different protection levels for different paths.
Based on security requirements in SECURITY_ENDPOINTS.md
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

# Define our access tiers
ACCESS_TIERS = {
    "public": {
        "name": "Image2Model Public Endpoints",
        "domain": "image2model.pranitlab.com",
        "path": "/api/v1/health",  # Using a single path that covers health endpoints
        "description": "Public health check endpoints - no authentication required",
        "policy": {
            "name": "Allow All - Public Access",
            "decision": "allow",
            "include": [{"everyone": {}}],  # Allow everyone
            "precedence": 1
        }
    },
    "api": {
        "name": "Image2Model API Endpoints",
        "domain": "image2model.pranitlab.com", 
        "path": "/api",  # Covers all API endpoints except health
        "description": "Protected API endpoints requiring authentication",
        "policy": {
            "name": "Allowed Users and Service Tokens",
            "decision": "allow",
            "include": [
                {"email": {"email": "pranit.lahoty1@gmail.com"}},
                {"email_domain": {"domain": "gallagherdesign.com"}}
            ],
            "precedence": 2
        }
    },
    "ui": {
        "name": "Image2Model Web UI",
        "domain": "image2model.pranitlab.com",
        "path": "/upload",  # Upload UI page
        "description": "Web UI requiring user authentication",
        "policy": {
            "name": "Allowed UI Users",
            "decision": "allow",
            "include": [
                {"email": {"email": "pranit.lahoty1@gmail.com"}},
                {"email_domain": {"domain": "gallagherdesign.com"}}
            ],
            "precedence": 3
        }
    },
    "admin": {
        "name": "Image2Model Admin",
        "domain": "image2model.pranitlab.com",
        "path": "/api/v1/admin",  # Admin endpoints
        "description": "Admin endpoints requiring elevated permissions",
        "policy": {
            "name": "Admin Users Only",
            "decision": "allow",
            "include": [
                {"email": {"email": "pranit.lahoty1@gmail.com"}}
            ],
            "require": [],  # Could add MFA requirement here
            "precedence": 4
        }
    }
}

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

def delete_existing_image2model_apps():
    """Delete existing Image2Model apps to start fresh."""
    apps = get_existing_apps()
    
    for app in apps:
        if "image2model" in app.get("name", "").lower() or app.get("domain") == "image2model.pranitlab.com":
            print(f"🗑️  Deleting existing app: {app['name']} (ID: {app['id']})")
            url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app['id']}"
            response = requests.delete(url, headers=headers)
            
            if response.status_code in [200, 204]:
                print(f"   ✅ Deleted successfully")
            else:
                print(f"   ❌ Error deleting: {response.status_code}")

def create_access_app(tier_name: str, config: Dict[str, Any]):
    """Create an Access application for a specific tier."""
    print(f"\n📱 Creating {tier_name} application...")
    
    # Create the application
    app_data = {
        "name": config["name"],
        "domain": config["domain"],
        "type": "self_hosted",
        "session_duration": "24h",
        "auto_redirect_to_identity": False,  # Don't auto-redirect for API endpoints
        "http_only_cookie_attribute": True,
        "same_site_cookie_attribute": "none",
        "logo_url": "",
        "skip_interstitial": True,
        "app_launcher_visible": False,
        "service_auth_401_redirect": False,
        "custom_deny_message": "Access denied. Please contact your administrator.",
        "cors_headers": {
            "allowed_methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "allowed_origins": ["https://image2model.pranitlab.com"],
            "allow_all_origins": False,
            "allow_credentials": True
        }
    }
    
    # Add path if specified
    if "path" in config:
        app_data["path"] = config["path"]
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps"
    response = requests.post(url, headers=headers, json=app_data)
    
    if response.status_code in [200, 201]:
        app = response.json()["result"]
        print(f"   ✅ Created app: {app['name']} (ID: {app['id']})")
        
        # Create the policy for this app
        if "policy" in config:
            create_policy(app["id"], config["policy"])
        
        return app
    else:
        print(f"   ❌ Error creating app: {response.status_code}")
        print(response.text)
        return None

def create_policy(app_id: str, policy_config: Dict[str, Any]):
    """Create a policy for an Access application."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app_id}/policies"
    
    response = requests.post(url, headers=headers, json=policy_config)
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Created policy: {policy_config['name']}")
        return response.json()["result"]
    else:
        print(f"   ❌ Error creating policy: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🔧 Cloudflare Access Path-Based Configuration")
    print("=" * 60)
    
    # Ask user if they want to delete existing apps
    print("\n⚠️  WARNING: This will reconfigure all Image2Model Access apps")
    print("   Existing configurations will be replaced.")
    
    # Check for existing apps
    existing_apps = get_existing_apps()
    image2model_apps = [app for app in existing_apps if "image2model" in app.get("name", "").lower() or app.get("domain") == "image2model.pranitlab.com"]
    
    if image2model_apps:
        print(f"\n📋 Found {len(image2model_apps)} existing Image2Model app(s):")
        for app in image2model_apps:
            print(f"   - {app['name']} (Path: {app.get('path', '/')})")
        
        # Auto-confirm for MCP usage
        print("\n   Auto-confirming deletion for MCP usage...")
        print("   (Use --no-delete flag to keep existing apps)")
        
        # Delete existing apps
        delete_existing_image2model_apps()
    
    # Create new applications for each tier
    print("\n🚀 Creating new Access applications...")
    
    # First create the main domain app (catch-all)
    main_app_data = {
        "name": "Image2Model Main",
        "domain": "image2model.pranitlab.com",
        "description": "Main application - home page public access",
        "policy": {
            "name": "Public Home Page",
            "decision": "allow", 
            "include": [{"everyone": {}}],
            "precedence": 10  # Lowest precedence
        }
    }
    
    main_app = create_access_app("main", main_app_data)
    
    # Create path-specific apps (these will take precedence)
    for tier_name, config in ACCESS_TIERS.items():
        if tier_name != "public":  # Skip public as it's handled by main
            create_access_app(tier_name, config)
    
    print("\n✅ Configuration complete!")
    print("\n📋 Access configuration summary:")
    print("   - Home page (/): Public access")
    print("   - Health endpoints (/api/v1/health/*): Public access") 
    print("   - Upload UI (/upload): Requires authentication")
    print("   - API endpoints (/api/*): Requires authentication")
    print("   - Admin endpoints (/api/v1/admin/*): Requires admin authentication")
    
    print("\n🧪 Test with these commands:")
    print("   # Public home page (should work):")
    print("   curl https://image2model.pranitlab.com/")
    print("\n   # Public health endpoint (should work):")
    print("   curl https://image2model.pranitlab.com/api/v1/health/")
    print("\n   # Protected API endpoint (should redirect to login):")
    print("   curl https://image2model.pranitlab.com/api/v1/models/generate")
    print("\n   # Upload UI (should redirect to login):")
    print("   curl https://image2model.pranitlab.com/upload")
    
    print("\n📝 Next steps:")
    print("1. Test the endpoints to verify access control")
    print("2. Create service tokens for API access if needed")
    print("3. Configure rate limiting in Cloudflare WAF")

if __name__ == "__main__":
    main()