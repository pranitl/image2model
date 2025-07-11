#!/usr/bin/env python3
"""
Configure Cloudflare Access to allow API key authentication bypass.
This creates a bypass policy for requests with valid API keys.
"""

import os
import requests
import json

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

def create_bypass_policy(app_id: str):
    """Create a bypass policy for service tokens."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app_id}/policies"
    
    # First, check existing policies
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        policies = response.json()["result"]
        
        # Check if bypass policy already exists
        for policy in policies:
            if policy["name"] == "API Service Token Bypass":
                print("✅ Bypass policy already exists")
                return policy
    
    # Create bypass policy for service tokens
    bypass_policy = {
        "name": "API Service Token Bypass",
        "decision": "bypass",
        "include": [
            {
                "service_token": {}  # Any valid service token
            }
        ],
        "precedence": 1  # Higher precedence than other policies
    }
    
    response = requests.post(url, headers=headers, json=bypass_policy)
    
    if response.status_code in [200, 201]:
        print("✅ Created bypass policy for service tokens")
        return response.json()["result"]
    else:
        print(f"❌ Error creating bypass policy: {response.status_code}")
        print(response.text)
        return None

def create_user_allow_policy(app_id: str):
    """Create or update the main user allow policy."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps/{app_id}/policies"
    
    # Check existing policies
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        policies = response.json()["result"]
        
        # Find and update existing allow policy
        for policy in policies:
            if policy["decision"] == "allow" and policy["name"] != "API Service Token Bypass":
                print(f"📝 Updating existing policy: {policy['name']}")
                
                # Update the policy
                policy_update = {
                    "name": "Allowed Users",
                    "decision": "allow",
                    "include": [
                        {
                            "email": {"email": "pranit.lahoty1@gmail.com"}
                        },
                        {
                            "email_domain": {"domain": "gallagherdesign.com"}
                        }
                    ],
                    "precedence": 2  # Lower precedence than bypass
                }
                
                update_response = requests.put(
                    f"{url}/{policy['id']}", 
                    headers=headers, 
                    json=policy_update
                )
                
                if update_response.status_code == 200:
                    print("✅ Updated user allow policy")
                    return update_response.json()["result"]
                else:
                    print(f"❌ Error updating policy: {update_response.status_code}")
                    return None
    
    # Create new allow policy if none exists
    allow_policy = {
        "name": "Allowed Users",
        "decision": "allow",
        "include": [
            {
                "email": {"email": "pranit.lahoty1@gmail.com"}
            },
            {
                "email_domain": {"domain": "gallagherdesign.com"}
            }
        ],
        "precedence": 2
    }
    
    response = requests.post(url, headers=headers, json=allow_policy)
    
    if response.status_code in [200, 201]:
        print("✅ Created user allow policy")
        return response.json()["result"]
    else:
        print(f"❌ Error creating allow policy: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🔍 Setting up API bypass for Cloudflare Access...")
    
    # Find Image2Model app
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
    
    # Create policies
    print("\n📝 Setting up policies...")
    
    # 1. Create bypass policy for service tokens
    bypass_policy = create_bypass_policy(image2model_app["id"])
    
    # 2. Create/update user allow policy
    allow_policy = create_user_allow_policy(image2model_app["id"])
    
    if bypass_policy and allow_policy:
        print("\n✅ Configuration complete!")
        print("\n📋 Access methods:")
        print("1. Browser users: Login with approved email")
        print("2. API clients: Use service token headers")
        print("3. Backend: API key authentication still works after Cloudflare auth")
        
        print("\n🧪 Next steps:")
        print("1. Run create-service-token.py to generate API credentials")
        print("2. Test API access with the service token")
        print("3. Public health endpoints will still require Cloudflare auth")

if __name__ == "__main__":
    main()