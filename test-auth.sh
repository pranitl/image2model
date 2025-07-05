#!/bin/bash

# Test authentication endpoints

API_BASE="http://localhost:8000/api/v1"
API_KEY="dev-api-key-123456"
ADMIN_KEY="dev-admin-api-key-789012"

echo "Testing public endpoints (no auth required)..."
echo "Health check:"
curl -s "$API_BASE/../health" | jq '.'

echo -e "\n\nTesting authenticated endpoints..."
echo "Upload endpoint (requires API key):"
curl -s -X POST "$API_BASE/upload/" \
  -H "Authorization: Bearer $API_KEY" \
  -F "files=@frontend-simple/assets/favicon.svg" \
  -F "face_limit=5000" | jq '.'

echo -e "\n\nTesting admin endpoints..."
echo "Disk usage (requires admin key):"
curl -s "$API_BASE/admin/disk-usage" \
  -H "Authorization: Bearer $ADMIN_KEY" | jq '.'

echo -e "\n\nTesting without authentication (should fail)..."
echo "Upload without auth:"
curl -s -X POST "$API_BASE/upload/" \
  -F "files=@frontend-simple/assets/favicon.svg" \
  -F "face_limit=5000" | jq '.'