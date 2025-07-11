#!/usr/bin/env python3
"""
Create a Cloudflare Access Service Token for API access.
This allows API clients to authenticate without going through the login flow.
"""

import os
import requests
import json
from datetime import datetime, timedelta

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

def create_service_token():
    """Create a service token for API access."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/service_tokens"
    
    # Token expires in 1 year
    expires_at = (datetime.utcnow() + timedelta(days=365)).isoformat() + "Z"
    
    token_data = {
        "name": "Image2Model API Token",
        "duration": "8760h"  # 1 year in hours
    }
    
    response = requests.post(url, headers=headers, json=token_data)
    
    if response.status_code in [200, 201]:
        result = response.json()["result"]
        print("✅ Service token created successfully!")
        print("\n🔐 IMPORTANT: Save these credentials securely!")
        print("="*60)
        print(f"Client ID: {result['client_id']}")
        print(f"Client Secret: {result['client_secret']}")
        print("="*60)
        print("\n📝 How to use:")
        print("1. Add these headers to your API requests:")
        print(f"   CF-Access-Client-Id: {result['client_id']}")
        print(f"   CF-Access-Client-Secret: {result['client_secret']}")
        print("\n2. Example curl command:")
        print(f"   curl https://image2model.pranitlab.com/api/v1/models/generate \\")
        print(f"     -H 'CF-Access-Client-Id: {result['client_id']}' \\")
        print(f"     -H 'CF-Access-Client-Secret: {result['client_secret']}' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"file_id\": \"test\"}}'")
        print("\n3. Or use with existing API key:")
        print(f"   curl https://image2model.pranitlab.com/api/v1/models/generate \\")
        print(f"     -H 'CF-Access-Client-Id: {result['client_id']}' \\")
        print(f"     -H 'CF-Access-Client-Secret: {result['client_secret']}' \\")
        print(f"     -H 'Authorization: Bearer YOUR_API_KEY' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"file_id\": \"test\"}}'")
        
        return result
    else:
        print(f"❌ Error creating service token: {response.status_code}")
        print(response.text)
        return None

def list_service_tokens():
    """List existing service tokens."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/service_tokens"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        tokens = response.json()["result"]
        if tokens:
            print("\n📋 Existing service tokens:")
            for token in tokens:
                print(f"   - {token['name']} (ID: {token['id']})")
                print(f"     Created: {token['created_at']}")
                print(f"     Updated: {token['updated_at']}")
        return tokens
    else:
        print(f"❌ Error listing tokens: {response.status_code}")
        return []

def main():
    print("🔍 Cloudflare Access Service Token Manager")
    print("="*60)
    
    # List existing tokens
    existing_tokens = list_service_tokens()
    
    # Check if we already have an Image2Model token
    has_token = any(token["name"] == "Image2Model API Token" for token in existing_tokens)
    
    if has_token:
        print("\n⚠️  An Image2Model API Token already exists.")
        print("   Creating a new one will not invalidate the old one.")
        response = input("\n   Create a new token anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Create new token
    print("\n🔄 Creating new service token...")
    create_service_token()

if __name__ == "__main__":
    main()