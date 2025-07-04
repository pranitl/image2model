# Image2Model Deployment Security Guide

## Overview

This guide provides security instructions for deploying Image2Model on a Linode server with Cloudflare Tunnels. It covers the critical security configurations needed for a production deployment.

## Pre-Deployment Checklist

### 1. Environment Configuration

**CRITICAL: Configure .env.production before deployment**

```bash
# Copy the example file
cp .env.production.example .env.production

# Generate secure values
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 24  # For API_KEY
openssl rand -hex 24  # For ADMIN_API_KEY
openssl rand -base64 32  # For passwords
```

Edit `.env.production` and replace ALL placeholder values with your actual credentials:
- `FAL_API_KEY`: Your actual FAL.AI API key
- `SECRET_KEY`: Generated secure key
- `API_KEY`: Generated API key for basic auth
- `ADMIN_API_KEY`: Different key for admin endpoints
- Database and Redis passwords: Strong, unique passwords
- `BACKEND_CORS_ORIGINS`: Your actual domain(s)
- `ALLOWED_HOSTS`: Your domain(s)

### 2. Security Features Implemented

✅ **Authentication & Authorization**
- API key authentication for all endpoints
- Separate admin API key for sensitive operations
- Job ownership tracking for download access control

✅ **Rate Limiting**
- Upload endpoints: 10 requests/minute per IP
- General API: 100 requests/hour per IP

✅ **CORS Protection**
- Restrictive CORS in production mode
- Only specified origins allowed

✅ **Input Validation**
- File type validation
- Path traversal protection
- SQL injection prevention via ORM

✅ **Secure Headers**
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- No cache for sensitive data

## Deployment Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin

# Install firewall
sudo apt install ufw
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 2. Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/image2model.git
cd image2model

# Create production environment file
nano .env.production  # Add your configuration

# Build and start services
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# Check services
docker compose -f docker-compose.prod.yml ps
```

### 3. Cloudflare Tunnel Setup

```bash
# Install cloudflared
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create image2model

# Configure tunnel (create config.yml)
cat > ~/.cloudflared/config.yml << EOF
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/user/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: yourdomain.com
    service: http://localhost:80
    originRequest:
      noTLSVerify: true
  - service: http_status:404
EOF

# Run tunnel as service
sudo cloudflared service install
sudo systemctl start cloudflared
```

### 4. Configure Cloudflare Access (Recommended)

1. Go to Cloudflare Zero Trust Dashboard
2. Create Access Application for your domain
3. Set authentication rules (e.g., email OTP, OAuth)
4. This adds an extra authentication layer before your API

## Security Best Practices

### API Key Management

1. **Never commit API keys to version control**
2. **Rotate keys regularly** (monthly recommended)
3. **Use different keys for different environments**
4. **Monitor API key usage** in logs

### Database Security

```sql
-- Create application-specific user (don't use postgres superuser)
CREATE USER image2model WITH PASSWORD 'strong_password';
CREATE DATABASE image2model_prod OWNER image2model;
GRANT ALL PRIVILEGES ON DATABASE image2model_prod TO image2model;
```

### Monitoring & Logging

1. **Set up log aggregation**:
```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Save logs to file
docker compose -f docker-compose.prod.yml logs > logs_$(date +%Y%m%d).txt
```

2. **Monitor disk usage**:
```bash
# Check disk space
df -h

# Use admin API (requires admin key)
curl -H "Authorization: Bearer YOUR_ADMIN_API_KEY" \
     https://yourdomain.com/api/v1/admin/disk-usage
```

3. **Set up alerts** for:
- High disk usage (>80%)
- Failed authentication attempts
- Rate limit violations
- Application errors

### Regular Maintenance

1. **Daily**: Check application logs for errors
2. **Weekly**: Review disk usage and cleanup old files
3. **Monthly**: 
   - Update dependencies
   - Rotate API keys
   - Review access logs
4. **Quarterly**: Security audit

## Testing Security

### 1. Test Authentication

```bash
# Should fail without API key
curl https://yourdomain.com/api/v1/upload

# Should succeed with API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://yourdomain.com/api/v1/upload
```

### 2. Test Rate Limiting

```bash
# Run multiple requests quickly
for i in {1..15}; do
  curl -H "Authorization: Bearer YOUR_API_KEY" \
       https://yourdomain.com/api/v1/upload
done
# Should see rate limit errors after 10 requests
```

### 3. Test Admin Endpoints

```bash
# Should fail with regular API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://yourdomain.com/api/v1/admin/system-health

# Should succeed with admin key
curl -H "Authorization: Bearer YOUR_ADMIN_API_KEY" \
     https://yourdomain.com/api/v1/admin/system-health
```

## Emergency Procedures

### If Compromised

1. **Immediately revoke all API keys**
2. **Reset all passwords**
3. **Review logs for unauthorized access**
4. **Check for modified files**
5. **Restore from clean backup if needed**

### Backup Strategy

```bash
# Backup database
docker exec image2model-postgres pg_dump -U postgres image2model > backup_$(date +%Y%m%d).sql

# Backup uploaded files
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Store backups securely off-server
```

## Known Limitations

1. **No user authentication system** - relies on API keys
2. **Basic session management** - consider implementing JWT for better security
3. **No encryption at rest** - consider encrypting file storage
4. **Limited audit logging** - enhance for compliance needs

## Quick Security Fixes Applied

1. ✅ Removed hardcoded secrets
2. ✅ Added API authentication
3. ✅ Implemented rate limiting
4. ✅ Fixed CORS configuration
5. ✅ Added job ownership tracking
6. ✅ Secured admin endpoints
7. ✅ Added security headers
8. ✅ Path traversal protection

## Support

For security issues or questions:
1. Check application logs
2. Review this documentation
3. Monitor system health via admin API
4. Keep software updated

Remember: Security is an ongoing process. Regularly review and update your security measures.