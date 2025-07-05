# Image2Model Deployment Security Guide with Cloudflare Tunnels

## Overview

This guide provides comprehensive security instructions for deploying Image2Model on a Linode server with Cloudflare Tunnels as the primary security layer. Cloudflare Tunnels will protect all components, allowing users to simply log in and use the full application without managing API keys.

### Security Architecture

```
[Internet Users] → [Cloudflare Auth] → [Cloudflare Tunnel] → [Linode Server]
                                                                    ↓
                                                         [Nginx (port 80 only)]
                                                                    ↓
                                                    [Frontend:3000] ←→ [Backend:8000]
                                                                    ↓        ↓
                                                            [Redis:6379] [Postgres:5432]
```

**Key Security Points:**
- Only port 80 is exposed on the server (for Cloudflare Tunnel)
- All other services communicate internally via Docker network
- Users authenticate through Cloudflare, not API keys
- Frontend embeds API key for backend communication
- Database and Redis ports are NOT exposed externally

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
sudo apt install docker compose-plugin

# Configure firewall BEFORE starting services
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH (consider restricting by IP later)
sudo ufw allow 80/tcp  # HTTP (for Cloudflare Tunnel only)
# Note: Port 443 not needed - Cloudflare handles SSL termination
sudo ufw enable

# Optional: Restrict SSH to specific IP after setup
# sudo ufw delete allow 22/tcp
# sudo ufw allow from YOUR.IP.ADDRESS to any port 22
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
  # Main application - users access this
  - hostname: yourdomain.com
    service: http://localhost:80
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      # Cloudflare recommends these additional settings
      tcpKeepAlive: 30s
      noHappyEyeballs: false
      keepAliveConnections: 1024
      keepAliveTimeout: 90s
      
  # Admin subdomain (optional) - protected by Cloudflare Access
  - hostname: admin.yourdomain.com
    service: http://localhost:80
    path: /api/v1/admin/*
    originRequest:
      noTLSVerify: true
      
  # Catch-all rule (REQUIRED - must be last)
  - service: http_status:404
EOF

# Run tunnel as service
sudo cloudflared service install
sudo systemctl start cloudflared
```

**Important:** The tunnel configuration above routes ALL traffic through port 80. The nginx proxy in the docker-compose.prod.yml handles routing to the appropriate service:
- `/` → Frontend (port 3000)
- `/api/*` → Backend (port 8000)
- Static assets → Frontend

### 4. Configure Cloudflare Access (Required)

#### Main Application Access
1. Go to Cloudflare Zero Trust Dashboard
2. Create Access Application:
   - Name: "Image2Model App"
   - Subdomain: `yourdomain.com`
   - Path: Leave blank (protects entire domain)
3. Configure authentication policy:
   - Policy name: "Authorized Users"
   - Action: Allow
   - Include: Emails ending in `@yourcompany.com` OR specific email list
   - Authentication methods: Google OAuth, GitHub, Email OTP
4. Advanced settings:
   - Session duration: 24 hours
   - Enable automatic redirection

#### Admin Access (Optional but Recommended)
1. Create separate Access Application:
   - Name: "Image2Model Admin"
   - Subdomain: `admin.yourdomain.com` OR
   - Path: `/api/v1/admin/*`
2. Configure stricter policy:
   - Policy name: "Admin Only"
   - Include: Specific admin emails only
   - Require: Multi-factor authentication

#### User Flow
```
1. User visits yourdomain.com
2. Cloudflare Access intercepts → Shows login page
3. User authenticates (Google/GitHub/Email)
4. Cloudflare validates → Issues JWT token
5. User accesses frontend → Uses embedded API key for backend
6. All API calls include the embedded key (not user-managed)
```

### 5. Docker Compose Production Configuration

The `docker-compose.prod.yml` ensures all services are properly isolated:

```yaml
services:
  nginx:
    ports:
      - "80:80"  # ONLY exposed port
    
  frontend:
    # No ports exposed - accessed via nginx
    
  backend:
    # No ports exposed - accessed via nginx
    environment:
      - API_KEY=${API_KEY}  # Embedded in frontend
      - ADMIN_API_KEY=${ADMIN_API_KEY}  # For admin access
    
  postgres:
    # No ports exposed - internal only
    
  redis:
    # No ports exposed - internal only
```

## How Cloudflare Tunnels Protect Everything

### 1. Complete Port Protection
- **Public exposure**: Only port 80 on the server
- **Cloudflare tunnel**: Encrypts all traffic from Cloudflare edge to your server
- **Internal services**: All communicate via Docker's internal network
- **Database/Redis**: Completely inaccessible from internet

### 2. User Authentication Flow
```
User → Cloudflare Access Login → Frontend → Backend API
         ↓                         ↓           ↓
    (Google/GitHub/Email)    (HTML/JS)   (Embedded API Key)
```

### 3. API Key Usage
- **Users**: Never see or manage API keys
- **Frontend**: Has embedded API key for backend communication
- **Purpose**: Internal service-to-service authentication
- **Risk mitigation**: Even if someone bypasses Cloudflare, they need the API key

### 4. Admin Endpoint Protection
Admin endpoints (`/api/v1/admin/*`) have triple protection:
1. Cloudflare Access authentication (user level)
2. Optional separate Access policy for admin subdomain
3. Separate ADMIN_API_KEY requirement

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

## Monitoring with Cloudflare

### 1. Access Logs
- View all authentication attempts in Zero Trust dashboard
- Set up alerts for failed logins
- Monitor for suspicious access patterns

### 2. Analytics
- Track usage patterns
- Identify potential DDoS attempts
- Monitor bandwidth usage

### 3. Security Events
- Configure notifications for:
  - Multiple failed auth attempts
  - Access from new locations
  - Expired sessions

## Troubleshooting

### Common Issues

1. **"Not authenticated" error**
   - Ensure API_KEY is set in .env.production
   - Restart containers after changing environment
   - Check frontend has correct API key embedded

2. **Can't access through Cloudflare**
   - Verify tunnel is running: `sudo systemctl status cloudflared`
   - Check tunnel routes: `cloudflared tunnel route ip show`
   - Ensure DNS points to tunnel

3. **Admin endpoints not working**
   - Verify ADMIN_API_KEY is set
   - Check if using correct Authorization header
   - Ensure admin Access policy is configured

## Production Checklist

- [ ] All secrets removed from code and docker-compose.yml
- [ ] .env.production configured with strong values
- [ ] Cloudflare Tunnel installed and running
- [ ] Cloudflare Access policies configured
- [ ] Only port 80 exposed on server
- [ ] Frontend has embedded API key
- [ ] Admin endpoints protected with separate key
- [ ] Monitoring and alerts configured
- [ ] Backup strategy implemented
- [ ] SSL certificate active (via Cloudflare)

## Additional Security Recommendations

### Token Validation
While Cloudflare Tunnels protect the infrastructure, consider implementing [application token validation](https://developers.cloudflare.com/cloudflare-one/identity/authorization-cookie/) for an extra security layer. This ensures requests that somehow bypass Cloudflare are rejected.

### Docker Security
- Avoid using `docker run --publish-all` which exposes all ports
- Bind sensitive services to localhost only:
  ```bash
  # Good - only accessible internally
  docker run -p 127.0.0.1:5432:5432 postgres
  
  # Bad - exposed to all interfaces
  docker run -p 5432:5432 postgres
  ```

### Monitoring Best Practices
- Enable Cloudflare's Web Analytics for traffic insights
- Set up log aggregation for both Cloudflare and application logs
- Configure alerts for:
  - Tunnel disconnections
  - High error rates
  - Unusual traffic patterns

## Known Limitations

1. **Cloudflare dependency** - Application requires Cloudflare for authentication
2. **Basic session management** - Relies on Cloudflare's session handling
3. **No user-specific rate limiting** - Rate limits apply per IP
4. **Limited audit logging** - Enhance application logs for compliance needs

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