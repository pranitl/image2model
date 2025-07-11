#!/usr/bin/env python3
"""
Update Cloudflare Access application to protect entire domain
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
APP_ID = "df0cd752-7474-4db6-ab5e-f6ba67c4b45b"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

def update_application():
    """Update the application to protect entire domain"""
    
    # Updated configuration to protect entire domain
    app_config = {
        "name": "image2model-app",
        "domain": "image2model.pranitlab.com",  # Remove /upload to protect entire domain
        "type": "self_hosted",
        "session_duration": "24h",
        "auto_redirect_to_identity": False,
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
    
    print("Updating application to protect entire domain...")
    
    response = requests.put(
        f"{CLOUDFLARE_API_BASE}/accounts/{ACCOUNT_ID}/access/apps/{APP_ID}",
        headers=headers,
        json=app_config
    )
    
    if response.status_code == 200:
        result = response.json()['result']
        print("✅ Application updated successfully!")
        print(f"   Domain: {result.get('domain', 'N/A')}")
        print(f"   AUD: {result['aud']}")
        return result
    else:
        print(f"❌ Failed to update application: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return None

def create_bypass_policy():
    """Create a bypass policy for public endpoints"""
    
    bypass_policy = {
        "name": "Public Endpoints Bypass",
        "decision": "bypass",
        "precedence": 0,  # Lower precedence number = higher priority
        "include": [
            {
                "everyone": {}
            }
        ],
        "exclude": [],
        "require": []
    }
    
    print("\nCreating bypass policy for public endpoints...")
    
    # Note: Cloudflare doesn't support path-based policies in the same app
    # We'll need to handle this at the application level or create separate apps
    print("⚠️  Note: Path-based bypass requires separate applications or WAF rules")
    print("   Public endpoints will be handled by your backend authentication")

def main():
    print("=== Updating Cloudflare Access Application ===\n")
    
    # Update the application
    result = update_application()
    
    if result:
        print("\n=== Next Steps ===")
        print("1. Your application now protects the entire domain")
        print("2. The AUD tag remains the same - no need to update .env.production")
        print("3. Public endpoints (/health, etc.) are handled by your backend code")
        print("4. Deploy the updated backend to your server")
        
        print("\n=== Public Endpoints ===")
        print("These endpoints bypass Cloudflare auth in your backend:")
        print("- / (root)")
        print("- /api/v1/health")
        print("- /api/v1/health/*")
        print("- /api/v1/models/available")
        print("\nAll other endpoints require Cloudflare or API key authentication")

if __name__ == "__main__":
    main()