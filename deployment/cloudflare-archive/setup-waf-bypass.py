#!/usr/bin/env python3
"""
Configure Cloudflare WAF rules to bypass Access for public endpoints.
This is the correct approach for path-based access control.
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

# We need the Zone ID for WAF rules
# First, let's get it
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def get_zone_id():
    """Get the Zone ID for image2model.pranitlab.com"""
    url = "https://api.cloudflare.com/client/v4/zones"
    params = {"name": "pranitlab.com"}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        zones = response.json()["result"]
        if zones:
            zone_id = zones[0]["id"]
            print(f"✅ Found zone: pranitlab.com (ID: {zone_id})")
            return zone_id
    
    print("❌ Could not find zone ID")
    return None

def create_waf_bypass_rules(zone_id: str):
    """Create WAF custom rules to bypass Access for public endpoints."""
    
    # Define our bypass rules
    bypass_rules = [
        {
            "description": "Bypass Access for home page",
            "expression": '(http.request.uri.path eq "/" and http.host eq "image2model.pranitlab.com")',
            "action": "skip",
            "action_parameters": {
                "products": ["accessRules"]
            },
            "enabled": True
        },
        {
            "description": "Bypass Access for health endpoints",
            "expression": '(http.request.uri.path matches "^/api/v1/health" and http.host eq "image2model.pranitlab.com")',
            "action": "skip",
            "action_parameters": {
                "products": ["accessRules"]
            },
            "enabled": True
        },
        {
            "description": "Bypass Access for available models endpoint",
            "expression": '(http.request.uri.path eq "/api/v1/models/available" and http.host eq "image2model.pranitlab.com")',
            "action": "skip",
            "action_parameters": {
                "products": ["accessRules"]
            },
            "enabled": True
        },
        {
            "description": "Bypass Access for static assets",
            "expression": '(http.request.uri.path matches "\\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$" and http.host eq "image2model.pranitlab.com")',
            "action": "skip",
            "action_parameters": {
                "products": ["accessRules"]
            },
            "enabled": True
        }
    ]
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    
    # First, get existing rulesets
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        rulesets = response.json()["result"]
        
        # Find the custom ruleset
        custom_ruleset = None
        for ruleset in rulesets:
            if ruleset["phase"] == "http_request_firewall_custom":
                custom_ruleset = ruleset
                break
        
        if custom_ruleset:
            print(f"📝 Found existing custom ruleset: {custom_ruleset['id']}")
            
            # Update the ruleset with our rules
            update_url = f"{url}/{custom_ruleset['id']}"
            
            # Get existing rules
            existing_rules = custom_ruleset.get("rules", [])
            
            # Filter out any existing Image2Model bypass rules
            existing_rules = [rule for rule in existing_rules 
                            if "image2model" not in rule.get("description", "").lower()]
            
            # Add our new rules
            all_rules = existing_rules + bypass_rules
            
            update_data = {
                "rules": all_rules
            }
            
            response = requests.put(update_url, headers=headers, json=update_data)
            
            if response.status_code == 200:
                print("✅ Successfully created WAF bypass rules!")
                return True
            else:
                print(f"❌ Error updating ruleset: {response.status_code}")
                print(response.text)
                return False
        else:
            # Create new custom ruleset
            print("🆕 Creating new custom ruleset...")
            
            create_data = {
                "name": "Custom firewall rules",
                "description": "Custom rules including Access bypass",
                "kind": "zone",
                "phase": "http_request_firewall_custom",
                "rules": bypass_rules
            }
            
            response = requests.post(url, headers=headers, json=create_data)
            
            if response.status_code in [200, 201]:
                print("✅ Successfully created custom ruleset with bypass rules!")
                return True
            else:
                print(f"❌ Error creating ruleset: {response.status_code}")
                print(response.text)
                return False

def update_access_app():
    """Update the Access app to remove the 'everyone' policies."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/apps"
    
    # Get existing apps
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        apps = response.json()["result"]
        
        for app in apps:
            if app.get("domain") == "image2model.pranitlab.com":
                app_id = app["id"]
                print(f"\n📝 Found Access app: {app['name']} (ID: {app_id})")
                
                # Get policies
                policy_url = f"{url}/{app_id}/policies"
                policy_response = requests.get(policy_url, headers=headers)
                
                if policy_response.status_code == 200:
                    policies = policy_response.json()["result"]
                    
                    # Remove 'everyone' policies
                    for policy in policies:
                        if any("everyone" in str(rule) for rule in policy.get("include", [])):
                            print(f"🗑️  Removing public policy: {policy['name']}")
                            delete_url = f"{policy_url}/{policy['id']}"
                            requests.delete(delete_url, headers=headers)
                    
                    # Create a single authenticated users policy
                    auth_policy = {
                        "name": "Authenticated Users Only",
                        "decision": "allow",
                        "include": [
                            {"email": {"email": "pranit.lahoty1@gmail.com"}},
                            {"email_domain": {"domain": "gallagherdesign.com"}}
                        ],
                        "exclude": [],
                        "require": [],
                        "precedence": 1
                    }
                    
                    print("📝 Creating authenticated users policy...")
                    response = requests.post(policy_url, headers=headers, json=auth_policy)
                    
                    if response.status_code in [200, 201]:
                        print("✅ Policy created successfully")
                    else:
                        print(f"❌ Error creating policy: {response.status_code}")

def main():
    print("🔧 Cloudflare WAF Bypass Configuration")
    print("=" * 60)
    
    # Step 1: Get Zone ID
    zone_id = get_zone_id()
    if not zone_id:
        print("❌ Cannot proceed without Zone ID")
        return
    
    # Step 2: Create WAF bypass rules
    print("\n🛡️  Creating WAF bypass rules for public endpoints...")
    success = create_waf_bypass_rules(zone_id)
    
    if success:
        # Step 3: Update Access app to remove public policies
        update_access_app()
        
        print("\n✅ Configuration complete!")
        print("\n📋 Access configuration:")
        print("   - Access app protects entire domain")
        print("   - WAF rules bypass Access for public endpoints:")
        print("     • / (home page)")
        print("     • /api/v1/health/*")
        print("     • /api/v1/models/available")
        print("     • Static assets (js, css, images)")
        
        print("\n🧪 Test commands:")
        print("\n1. Public endpoints (should work without login):")
        print("   curl https://image2model.pranitlab.com/")
        print("   curl https://image2model.pranitlab.com/api/v1/health/")
        print("   curl https://image2model.pranitlab.com/api/v1/models/available")
        
        print("\n2. Protected endpoints (should redirect to login):")
        print("   curl https://image2model.pranitlab.com/upload")
        print("   curl https://image2model.pranitlab.com/api/v1/models/generate")
        
        print("\n📝 Note: WAF rules may take 30-60 seconds to propagate globally")
    else:
        print("\n❌ Failed to create WAF bypass rules")
        print("   You may need additional permissions or a paid plan")

if __name__ == "__main__":
    main()