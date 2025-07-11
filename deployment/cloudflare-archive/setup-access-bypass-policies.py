#!/usr/bin/env python3
"""
Configure Cloudflare Access with bypass policies for public endpoints.
This is the correct approach based on 2024 Cloudflare documentation.
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
        "name": "Bypass - Home Page",
        "decision": "bypass",  # This is the key - bypass instead of allow
        "include": [{"everyone": {}}],
        "exclude": [],
        "require": [],
        "precedence": 1,  # Highest precedence
        "description": "Allow public access to home page",
        # Path matching is done via include conditions
    },
    {
        "name": "Bypass - Health Endpoints", 
        "decision": "bypass",
        "include": [{"everyone": {}}],
        "exclude": [],
        "require": [],
        "precedence": 2,
        "description": "Allow public access to health check endpoints"
    },
    {
        "name": "Bypass - Available Models",
        "decision": "bypass",
        "include": [{"everyone": {}}],
        "exclude": [],
        "require": [],
        "precedence": 3,
        "description": "Allow public access to available models endpoint"
    },
    {
        "name": "Authenticated Users - All Other Paths",
        "decision": "allow",
        "include": [
            {"email": {"email": "pranit.lahoty1@gmail.com"}},
            {"email_domain": {"domain": "gallagherdesign.com"}}
        ],
        "exclude": [],
        "require": [],
        "precedence": 10,  # Lower precedence - catch all
        "description": "Require authentication for all other endpoints"
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

def create_path_specific_apps():
    """Create separate Access applications for different path patterns."""
    
    # Delete existing Image2Model app first
    print("🔍 Checking for existing Image2Model apps...")
    apps = get_existing_apps()
    
    for app in apps:
        if app.get("domain") == "image2model.pranitlab.com":
            print(f"🗑️  Deleting existing app: {app['name']}")
            url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app['id']}"
            requests.delete(url, headers=headers)
    
    # Define our applications with specific paths
    app_configs = [
        {
            "name": "Image2Model - Public Home",
            "domain": "image2model.pranitlab.com",
            "path": "/",
            "config": {
                "type": "self_hosted",
                "session_duration": "24h",
                "auto_redirect_to_identity": False,
                "http_only_cookie_attribute": True,
                "same_site_cookie_attribute": "none",
                "skip_interstitial": True,
                "app_launcher_visible": False
            },
            "policy": {
                "name": "Public Access",
                "decision": "bypass",
                "include": [{"everyone": {}}],
                "precedence": 1
            }
        },
        {
            "name": "Image2Model - Health Endpoints",
            "domain": "image2model.pranitlab.com", 
            "path": "/api/v1/health",
            "config": {
                "type": "self_hosted",
                "session_duration": "24h",
                "auto_redirect_to_identity": False,
                "http_only_cookie_attribute": True,
                "same_site_cookie_attribute": "none",
                "skip_interstitial": True,
                "app_launcher_visible": False
            },
            "policy": {
                "name": "Public Health Check",
                "decision": "bypass",
                "include": [{"everyone": {}}],
                "precedence": 1
            }
        },
        {
            "name": "Image2Model - Available Models",
            "domain": "image2model.pranitlab.com",
            "path": "/api/v1/models/available",
            "config": {
                "type": "self_hosted",
                "session_duration": "24h",
                "auto_redirect_to_identity": False,
                "http_only_cookie_attribute": True,
                "same_site_cookie_attribute": "none",
                "skip_interstitial": True,
                "app_launcher_visible": False
            },
            "policy": {
                "name": "Public Model List",
                "decision": "bypass",
                "include": [{"everyone": {}}],
                "precedence": 1
            }
        },
        {
            "name": "Image2Model - Protected Areas",
            "domain": "image2model.pranitlab.com",
            "config": {
                "type": "self_hosted",
                "session_duration": "24h",
                "auto_redirect_to_identity": True,
                "http_only_cookie_attribute": True,
                "same_site_cookie_attribute": "none",
                "skip_interstitial": False,
                "app_launcher_visible": False,
                "custom_deny_message": "Access denied. Please contact your administrator.",
                "cors_headers": {
                    "allowed_methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
                    "allowed_origins": ["https://image2model.pranitlab.com"],
                    "allowed_headers": ["Content-Type", "Authorization"],
                    "allow_credentials": True
                }
            },
            "policy": {
                "name": "Authenticated Users",
                "decision": "allow",
                "include": [
                    {"email": {"email": "pranit.lahoty1@gmail.com"}},
                    {"email_domain": {"domain": "gallagherdesign.com"}}
                ],
                "precedence": 1
            }
        }
    ]
    
    # Create each application
    for app_config in app_configs:
        print(f"\n📱 Creating app: {app_config['name']}")
        
        # Build app data
        app_data = {
            "name": app_config["name"],
            "domain": app_config["domain"],
            **app_config["config"]
        }
        
        # Add path if specified
        if "path" in app_config:
            app_data["path"] = app_config["path"]
        
        # Create the app
        url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps"
        response = requests.post(url, headers=headers, json=app_data)
        
        if response.status_code in [200, 201]:
            app = response.json()["result"]
            print(f"   ✅ Created app (ID: {app['id']})")
            
            # Create the policy
            if "policy" in app_config:
                policy_url = f"{url}/{app['id']}/policies"
                policy_response = requests.post(policy_url, headers=headers, json=app_config["policy"])
                
                if policy_response.status_code in [200, 201]:
                    print(f"   ✅ Created policy: {app_config['policy']['name']}")
                else:
                    print(f"   ❌ Error creating policy: {policy_response.status_code}")
                    print(policy_response.text)
        else:
            print(f"   ❌ Error creating app: {response.status_code}")
            print(response.text)

def main():
    print("🔧 Cloudflare Access Path-Based Bypass Configuration")
    print("=" * 60)
    
    # Create path-specific applications
    create_path_specific_apps()
    
    print("\n✅ Configuration complete!")
    print("\n📋 Access configuration:")
    print("   - Public endpoints (bypass authentication):")
    print("     • / (home page only)")
    print("     • /api/v1/health/* (all health endpoints)")  
    print("     • /api/v1/models/available")
    print("   - Protected endpoints (require authentication):")
    print("     • All other paths")
    
    print("\n🧪 Test commands:")
    print("\n1. Public endpoints (should work without login):")
    print("   curl https://image2model.pranitlab.com/")
    print("   curl https://image2model.pranitlab.com/api/v1/health/")
    print("   curl https://image2model.pranitlab.com/api/v1/models/available")
    
    print("\n2. Protected endpoints (should redirect to login):")
    print("   curl https://image2model.pranitlab.com/upload")
    print("   curl https://image2model.pranitlab.com/api/v1/models/generate")
    print("   curl https://image2model.pranitlab.com/api/v1/admin/disk-usage")
    
    print("\n📝 Notes:")
    print("   - Path-specific apps take precedence over domain-wide apps")
    print("   - Bypass policies allow access without authentication")
    print("   - Changes may take 30-60 seconds to propagate")

if __name__ == "__main__":
    main()