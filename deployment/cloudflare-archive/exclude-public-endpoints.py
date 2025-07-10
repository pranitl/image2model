#!/usr/bin/env python3
"""
Update Cloudflare Access application to exclude public endpoints.
Based on the security endpoints document, these paths should be publicly accessible.
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

# Public endpoints that should be excluded from authentication
PUBLIC_PATHS = [
    "/",
    "/health",
    "/api/v1/health/",
    "/api/v1/health/detailed",
    "/api/v1/health/metrics", 
    "/api/v1/health/liveness",
    "/api/v1/health/readiness",
    "/api/v1/models/available"
]

def get_access_apps():
    """Get all Access applications."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(f"Error getting apps: {response.status_code}")
        print(response.text)
        return []

def update_app_with_exclusions(app_id: str, app_data: Dict[str, Any]):
    """Update Access app to exclude public paths."""
    
    # Add path exclusions
    app_data["path_cookie_attribute"] = "SameSite=None; Secure"
    
    # Create exclude rules for public paths
    exclude_rules = []
    for path in PUBLIC_PATHS:
        exclude_rules.append({
            "path": path
        })
    
    # Update the app configuration
    updated_config = {
        "name": app_data["name"],
        "domain": app_data["domain"],
        "type": app_data["type"],
        "session_duration": app_data.get("session_duration", "24h"),
        "auto_redirect_to_identity": app_data.get("auto_redirect_to_identity", True),
        "allowed_idps": app_data.get("allowed_idps", []),
        "custom_deny_message": app_data.get("custom_deny_message", ""),
        "custom_deny_url": app_data.get("custom_deny_url", ""),
        "http_only_cookie_attribute": app_data.get("http_only_cookie_attribute", True),
        "same_site_cookie_attribute": app_data.get("same_site_cookie_attribute", "none"),
        "cors_headers": app_data.get("cors_headers", {
            "allowed_methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
            "allowed_origins": ["https://image2model.pranitlab.com"],
            "allow_all_origins": False,
            "allow_credentials": True
        }),
        # Add exclude configuration
        "self_hosted_domains": exclude_rules
    }
    
    # If app already has a path, keep it
    if "path" in app_data:
        updated_config["path"] = app_data["path"]
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app_id}"
    response = requests.put(url, headers=headers, json=updated_config)
    
    if response.status_code == 200:
        print(f"✅ Successfully updated app to exclude public endpoints")
        return response.json()["result"]
    else:
        print(f"❌ Error updating app: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🔍 Finding Image2Model Access application...")
    
    apps = get_access_apps()
    image2model_app = None
    
    for app in apps:
        if app["domain"] == "image2model.pranitlab.com":
            image2model_app = app
            break
    
    if not image2model_app:
        print("❌ No Image2Model app found!")
        return
    
    print(f"✅ Found app: {image2model_app['name']} (ID: {image2model_app['id']})")
    
    # Create a policy if needed
    policy_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/policies"
    
    # Check if we already have a policy for this app
    policies_response = requests.get(
        f"{policy_url}?app_id={image2model_app['id']}", 
        headers=headers
    )
    
    if policies_response.status_code == 200:
        policies = policies_response.json()["result"]
        
        if not policies:
            print("📝 Creating access policy...")
            # Create a new policy
            policy_data = {
                "name": "Image2Model Allowed Users",
                "decision": "allow",
                "include": [
                    {
                        "email": {"email": "pranit.lahoty1@gmail.com"}
                    },
                    {
                        "email_domain": {"domain": "gallagherdesign.com"}
                    }
                ],
                "exclude": [],
                "require": [],
                "precedence": 1
            }
            
            create_response = requests.post(
                f"{policy_url}?app_id={image2model_app['id']}",
                headers=headers,
                json=policy_data
            )
            
            if create_response.status_code in [200, 201]:
                print("✅ Policy created successfully")
            else:
                print(f"❌ Error creating policy: {create_response.status_code}")
                print(create_response.text)
    
    # Now update the app with exclusions
    print("\n🔄 Updating app to exclude public endpoints...")
    print(f"   Excluding paths: {', '.join(PUBLIC_PATHS)}")
    
    updated_app = update_app_with_exclusions(image2model_app["id"], image2model_app)
    
    if updated_app:
        print("\n✅ Configuration complete!")
        print("\n📋 Public endpoints (no auth required):")
        for path in PUBLIC_PATHS:
            print(f"   - https://image2model.pranitlab.com{path}")
        print("\n🔒 All other endpoints require authentication")
        print("\n🧪 Test commands:")
        print("   # Public endpoint (should work):")
        print("   curl https://image2model.pranitlab.com/api/v1/health/")
        print("\n   # Protected endpoint (should redirect to login):")
        print("   curl https://image2model.pranitlab.com/api/v1/models/generate")

if __name__ == "__main__":
    main()