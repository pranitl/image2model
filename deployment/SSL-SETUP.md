# SSL Certificate Setup Guide

## Overview
This guide explains how to set up SSL certificates for the Image2Model production deployment.

## Certificate Paths
The nginx configuration expects SSL certificates at:
- Certificate: `/etc/nginx/ssl/cert.pem`
- Private Key: `/etc/nginx/ssl/key.pem`

## Setup Instructions

### Option 1: Using Let's Encrypt (Recommended)
```bash
# Install certbot
apt-get update
apt-get install -y certbot

# Generate certificates (replace with your domain)
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Create SSL directory
mkdir -p /etc/nginx/ssl

# Copy certificates to expected locations
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /etc/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /etc/nginx/ssl/key.pem

# Set proper permissions
chmod 644 /etc/nginx/ssl/cert.pem
chmod 600 /etc/nginx/ssl/key.pem
```

### Option 2: Using Existing Certificates
If you have existing SSL certificates:

```bash
# Create SSL directory
mkdir -p /etc/nginx/ssl

# Copy your certificates
cp /path/to/your/certificate.pem /etc/nginx/ssl/cert.pem
cp /path/to/your/private-key.pem /etc/nginx/ssl/key.pem

# Set proper permissions
chmod 644 /etc/nginx/ssl/cert.pem
chmod 600 /etc/nginx/ssl/key.pem
```

## Validation
Run the SSL validation script before deployment:
```bash
./deployment/scripts/validate-ssl.sh
```

## Certificate Renewal
For Let's Encrypt certificates, set up auto-renewal:
```bash
# Add to crontab
0 0 * * * certbot renew --quiet --post-hook "docker exec image2model-frontend nginx -s reload"
```