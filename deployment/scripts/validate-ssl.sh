#!/bin/bash
# SSL Certificate Validation Script

set -e

echo "🔒 Validating SSL certificate setup..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root or with sudo"
    exit 1
fi

# Check if certificate files exist
if [ ! -f "/etc/nginx/ssl/cert.pem" ]; then
    echo "❌ Certificate file not found: /etc/nginx/ssl/cert.pem"
    echo "Please run the SSL setup first. See deployment/SSL-SETUP.md"
    exit 1
fi

if [ ! -f "/etc/nginx/ssl/key.pem" ]; then
    echo "❌ Private key file not found: /etc/nginx/ssl/key.pem"
    echo "Please run the SSL setup first. See deployment/SSL-SETUP.md"
    exit 1
fi

# Check file permissions
CERT_PERMS=$(stat -c %a /etc/nginx/ssl/cert.pem 2>/dev/null || stat -f %Lp /etc/nginx/ssl/cert.pem)
KEY_PERMS=$(stat -c %a /etc/nginx/ssl/key.pem 2>/dev/null || stat -f %Lp /etc/nginx/ssl/key.pem)

if [ "$KEY_PERMS" != "600" ]; then
    echo "⚠️  Warning: Private key has incorrect permissions: $KEY_PERMS (should be 600)"
    echo "Fixing permissions..."
    chmod 600 /etc/nginx/ssl/key.pem
fi

# Validate certificate
echo "✓ Certificate file exists"
echo "✓ Private key file exists"

# Check if certificate is valid
if openssl x509 -in /etc/nginx/ssl/cert.pem -noout -checkend 0; then
    echo "✓ Certificate is valid and not expired"
else
    echo "❌ Certificate is expired or invalid"
    exit 1
fi

# Check certificate expiration date
EXPIRY=$(openssl x509 -in /etc/nginx/ssl/cert.pem -noout -enddate | cut -d= -f2)
echo "✓ Certificate expires on: $EXPIRY"

# Check if certificate matches private key
CERT_MOD=$(openssl x509 -noout -modulus -in /etc/nginx/ssl/cert.pem | openssl md5)
KEY_MOD=$(openssl rsa -noout -modulus -in /etc/nginx/ssl/key.pem 2>/dev/null | openssl md5)

if [ "$CERT_MOD" = "$KEY_MOD" ]; then
    echo "✓ Certificate and private key match"
else
    echo "❌ Certificate and private key do not match"
    exit 1
fi

echo "✅ SSL certificate validation passed!"