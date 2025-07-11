# Cloudflare Tunnel to CDN Migration Plan (MVP)

## What We're Doing (Simple Summary)
- **Currently**: image2model.pranitlab.com → Cloudflare → Tunnel → Your Server
- **After Migration**: image2model.pranitlab.com → Cloudflare → Direct to Your Server (port 80/443)
- **n8n stays the same**: Still uses tunnel (no changes)

## Quick Status Check
Based on your progress:
- ✅ Phase 1: Server preparation (firewall, git) - DONE
- ✅ Phase 2: Environment file setup (.env created) - DONE
- ✅ Phase 3: Cloudflare configuration - DONE
  - ✅ SSL certificates (using existing *.pranitlab.com)
  - ✅ DNS updated to A record pointing to 66.228.60.251
  - ✅ SSL mode set to Full
  - ✅ Tunnel config updated (image2model removed)
- 🔄 Phase 4: Docker configuration check - IN PROGRESS
- ⏳ Phase 5: Deploy and test - NEXT

## Overview
Migrate Image2Model from Cloudflare Tunnels to standard Cloudflare DNS + CDN while keeping n8n on tunnels.

## Current Architecture
- **Server**: Linode VPS at 66.228.60.251
- **Access**: Via Cloudflare tunnel (cloudflared service) - shared with n8n
- **Domain**: image2model.pranitlab.com
- **Services**: Docker containers with nginx on port 80
- **Other Services**: n8n.pranitlab.com (must keep on tunnel)

## Target Architecture
- **Server**: Same Linode VPS
- **Image2Model**: Direct connection via Cloudflare CDN proxy
- **n8n**: Remains on Cloudflare tunnel (no changes)
- **SSL**: Full SSL mode (recommended for security)
- **Ports**: 80 and 443 open for Cloudflare IPs only

## Migration Steps

### Phase 1: Server Preparation

1. **Update Firewall Rules** 
   ```bash
   # Keep SSH
   ufw allow 22/tcp
   
   # Allow both HTTP and HTTPS from Cloudflare IPs only
   for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
     ufw allow from $ip to any port 80 proto tcp
     ufw allow from $ip to any port 443 proto tcp
   done
   
   ufw reload
   ```
   **Note**: Adding port 443 is minimal effort and provides better security with end-to-end encryption.

2. **Ensure Git Repository is Set Up**
   ```bash
   ssh root@66.228.60.251
   
   # Check if repo exists
   if [ ! -d "/opt/image2model/.git" ]; then
     cd /opt
     git clone https://github.com/pranitl/image2model.git
   else
     cd /opt/image2model
     git remote set-url origin https://github.com/pranitl/image2model.git
   fi
   ```

### Phase 2: Environment File Preparation

**Note**: Your `.env.production` should already be on the server from previous deployments. If not:

Option A - If .env.production exists on server:
```bash
cd /opt/image2model
ls -la .env*  # Check what env files exist

# If .env.production exists, use it:
cp .env.production .env

# Add missing Docker variables
echo "" >> .env
echo "# Additional Docker Variables" >> .env
echo "BACKEND_HOST=backend" >> .env
echo "BACKEND_PORT=8000" >> .env
echo "POSTGRES_PORT=5432" >> .env
```

Option B - If you need to copy from local:
```bash
# From your LOCAL machine (not SSH), run:
scp /Users/pranit/Documents/AI/image2model/.env.production root@66.228.60.251:/opt/image2model/

# Then SSH back in and continue with Option A above
```

### Phase 3: Cloudflare Configuration (DETAILED STEPS)

#### Step 1: SSL Certificate Setup

**Option A - If you already have *.pranitlab.com certificates:**
```bash
# Check existing certificates
ls -la /etc/cloudflared/*.pem
# OR check other common locations
ls -la /etc/ssl/certs/*pranitlab*

# If found, create symlinks or copy them:
mkdir -p /opt/image2model/ssl
cp /path/to/existing/cert.pem /opt/image2model/ssl/cert.pem
cp /path/to/existing/key.pem /opt/image2model/ssl/key.pem

# Set proper permissions
chmod 600 /opt/image2model/ssl/key.pem
chmod 644 /opt/image2model/ssl/cert.pem
```

**Option B - Generate new Origin Certificate (if needed):**
1. **Login to Cloudflare Dashboard**: https://dash.cloudflare.com
2. **Navigate to SSL/TLS** → "Origin Server"
3. **Click "Create Certificate"**
4. Follow the original instructions above

**Note**: Your existing `*.pranitlab.com` certificate will work for `image2model.pranitlab.com`!

#### Step 2: Update DNS Settings
1. **In Cloudflare Dashboard** → Click "DNS" in left sidebar
2. **Find existing records** for image2model.pranitlab.com
3. **Current state**: You might see:
   - CNAME pointing to tunnel.pranitlab.com (DELETE THIS)
   - OR an A record already pointing to 66.228.60.251
4. **If CNAME exists**: Delete it (click "Edit" → "Delete")
5. **Add/Update A record**:
   - Type: A
   - Name: image2model
   - IPv4 address: 66.228.60.251
   - Proxy status: **Proxied** (orange cloud ON) ← This is correct!
   - TTL: Auto
   - Click "Save"

**IMPORTANT**: "Proxied" (orange cloud) is what we want! This means:
- Users connect to Cloudflare
- Cloudflare connects to your server
- This provides DDoS protection, caching, and SSL

#### Step 3: Update SSL/TLS Mode
1. **Still in Cloudflare** → Click "SSL/TLS" → "Overview"
2. **Change encryption mode** to "Full" (not Full strict)
3. **Why Full?**: Because we're using Cloudflare Origin certificates

#### Step 4: Verify Tunnel Config (You already did this ✓)
```bash
# Just to confirm it's done:
cat /etc/cloudflared/config.yml | grep -A2 "hostname:"
# Should only show n8n entries, no image2model
```

### Phase 4: Docker Configuration Updates

**CRITICAL**: The current docker-compose.prod.yml references `frontend-simple` but needs to use `frontend-svelte` with SvelteKit.

#### Step 1: Update docker-compose.prod.yml

The docker-compose.prod.yml needs these changes:

1. **Remove static file mount from nginx**:
   ```yaml
   # Remove this line from nginx volumes:
   - ./frontend-simple:/usr/share/nginx/html:ro
   ```

2. **Update frontend service for SvelteKit**:
   ```yaml
   # Frontend (SvelteKit application)
   frontend:
     build:
       context: ./frontend-svelte
       dockerfile: Dockerfile
       target: production
     container_name: image2model-frontend
     # Expose port 3000 internally
     expose:
       - "3000"
     environment:
       - NODE_ENV=production
       - HOST=0.0.0.0
       - PORT=3000
       - ORIGIN=https://image2model.pranitlab.com
       - API_KEY=${API_KEY}
       - PUBLIC_API_URL=https://image2model.pranitlab.com/api/v1
     networks:
       - frontend-network
     restart: unless-stopped
     command: node build
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
       interval: 30s
       timeout: 10s
       retries: 3
   ```

#### Step 2: Create Updated Nginx Configuration

Create a new nginx configuration file that proxies to SvelteKit:

```bash
# Create nginx.svelte.conf
cat > /opt/image2model/docker/nginx/nginx.svelte.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json image/svg+xml;

    # Client body size for uploads
    client_max_body_size 100M;

    server {
        listen 80;
        server_name _;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Proxy to SvelteKit frontend
        location / {
            proxy_pass http://frontend:3000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # API endpoints
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts for long-running requests
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 300s;
            
            # WebSocket support for SSE
            proxy_buffering off;
            proxy_cache off;
            proxy_set_header Connection '';
            proxy_http_version 1.1;
            chunked_transfer_encoding off;
        }

        # Upload endpoint with extended timeout
        location /api/v1/upload {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Extended timeouts for uploads
            proxy_connect_timeout 60s;
            proxy_send_timeout 300s;
            proxy_read_timeout 600s;
            
            # Disable buffering for uploads
            proxy_request_buffering off;
        }
    }
}
EOF
```

#### Step 3: Update docker-compose to use new nginx config

```bash
# Update nginx service to use the new config
# In docker-compose.prod.yml, change:
- ./docker/nginx/nginx.prod.conf:/etc/nginx/nginx.conf:ro

# To:
- ./docker/nginx/nginx.svelte.conf:/etc/nginx/nginx.conf:ro
```

#### Step 4: SSL Configuration Decision

For MVP simplicity, we recommend:
- Use **Cloudflare Flexible SSL** mode
- Only expose port 80 from Docker
- Let Cloudflare handle all SSL

This means:
- No need to mount SSL certificates in Docker
- No need for port 443 in docker-compose
- Simpler configuration overall

If you already set Cloudflare to "Full" SSL mode, you can change it back to "Flexible" in the Cloudflare dashboard.

### Phase 5: Deploy and Test

1. **Complete Testing Checklist**
   ```bash
   # From server (basic health)
   curl http://localhost/health
   curl https://localhost/health -k
   
   # Wait for DNS propagation (5-10 mins)
   
   # Test all critical endpoints from outside
   curl https://image2model.pranitlab.com/api/v1/health/
   curl https://image2model.pranitlab.com/
   
   # Test API with your API key
   curl -H "X-API-Key: 23defad33e6c8f646ef4472d26d529bbfcbb6f6176460205" \
        https://image2model.pranitlab.com/api/v1/models/
   
   # Verify n8n still works
   curl https://n8n.pranitlab.com/
   ```
## Simplified Deployment Script

Create `deployment/deploy-mvp.sh`:

```bash
#!/bin/bash
# MVP Quick Deployment Script

DEPLOY_HOST="66.228.60.251"

echo "🚀 Deploying to $DEPLOY_HOST..."

ssh root@$DEPLOY_HOST << 'EOF'
set -e  # Exit on error

cd /opt/image2model

# Ensure we're on the right repo
if ! git remote -v | grep -q "github.com/pranitl/image2model"; then
    echo "❌ Wrong git repo!"
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Ensure environment file is up to date
if [ -f ".env.production" ]; then
    cp .env.production .env
    # Add any missing Docker-specific variables
    grep -q "BACKEND_HOST" .env || echo "BACKEND_HOST=backend" >> .env
    grep -q "BACKEND_PORT" .env || echo "BACKEND_PORT=8000" >> .env
    grep -q "POSTGRES_PORT" .env || echo "POSTGRES_PORT=5432" >> .env
fi

# Quick rebuild and restart
echo "🔄 Restarting services..."
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Wait and check
echo "⏳ Waiting for services..."
sleep 60

# Health check
if curl -f http://localhost/api/v1/health/; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed!"
    docker logs image2model-backend --tail 20
    exit 1
fi
EOF
```

Make it executable: `chmod +x deployment/deploy-mvp.sh`

## Environment Management

**Current Setup Issues**:
- `.env.production` has production values but missing some Docker variables
- Docker expects `.env` (not `.env.production`)
- Some variables differ between development and production

**Solution**:
1. **On Server**: `.env` is created from `.env.production` + additional vars
2. **In Git**: Only track `.env.example` (never commit `.env.production`)
3. **Updates**: Edit `.env.production` on server, then re-run deploy script

**Important Variables to Verify**:
```bash
# These must be in your server's .env:
DATABASE_URL=postgresql://image2model:9BNzCO3DgbSFllM5oiV1Iw@postgres:5432/image2model_prod
BACKEND_CORS_ORIGINS=https://image2model.pranitlab.com
ALLOWED_HOSTS=image2model.pranitlab.com,localhost
FAL_API_KEY=33c641da-1ab0-4a27-9d6f-dae97cded760:ba85710275317e3fde78262fc3d0af16

# These are added by deploy script:
BACKEND_HOST=backend
BACKEND_PORT=8000
POSTGRES_PORT=5432
```

## Quick Monitoring (MVP Level)

- **Cloudflare Dashboard**: Check traffic and errors
- **Basic Health Check**: `curl https://image2model.pranitlab.com/api/v1/health/`
- **Server Logs**: `docker logs image2model-backend --tail 50`

## Benefits of This Simplified Approach

1. **Dead Simple**
   - No SSL certificates to manage (Cloudflare handles it)
   - One command deployment
   - Direct server access when needed

2. **Fast Deployment**
   - Git pull + docker restart = ~120 seconds
   - No build artifacts to transfer
   - Immediate rollback with git

3. **Cost Effective**
   - Everything is free (Cloudflare, no SSL certs needed)
   - Minimal server resources
   - No complex infrastructure

## Migration Checklist

### Pre-Migration
- [ ] Backup current cloudflared config
- [ ] Test n8n is working properly
- [ ] Verify git repo points to correct origin

### Migration Steps
- [ ] Update firewall for ports 80 & 443 (Cloudflare IPs only)
- [ ] Fix environment variables (.env from .env.production)
- [ ] Generate Cloudflare Origin Certificate
- [ ] Save SSL certs to `/opt/image2model/ssl/`
- [ ] Update nginx config for SSL
- [ ] Remove image2model from tunnel config (keep n8n!)
- [ ] Update Cloudflare DNS to direct IP (66.228.60.251)
- [ ] Set Cloudflare SSL to "Full"
- [ ] Deploy with updated configuration
- [ ] Test all endpoints thoroughly
- [ ] Verify n8n still works

## Total Migration Time: ~45 minutes

1. **Prep** (15 mins): Firewall, SSL certs, environment fixes
2. **Switch** (10 mins): Update tunnel config, DNS, deploy
3. **Wait** (10 mins): DNS propagation
4. **Test** (10 mins): Verify everything works including n8n

## Key Differences from Original Plan

1. **DON'T disable cloudflared** - Just remove image2model entries
2. **Use Full SSL** - More secure, minimal extra effort
3. **Fix env variables** - Critical for deployment to work
4. **Test n8n** - Ensure we don't break existing services

## Quick Rollback Plan

If something breaks:
```bash
# Re-add image2model to tunnel config
nano /etc/cloudflared/config.yml
# Add back the image2model sections
systemctl restart cloudflared
# Change DNS back to tunnel
```

## Common Issues & Solutions

### "Connection refused" errors
- **Check**: Is nginx container running? `docker ps | grep nginx`
- **Fix**: `docker compose -f docker-compose.prod.yml up -d`

### SSL certificate errors
- **Check**: Did you save both cert.pem and key.pem?
- **Check**: Are permissions correct? `ls -la /opt/image2model/ssl/`
- **Fix**: Re-create certificates in Cloudflare dashboard

### DNS not resolving
- **Check**: DNS propagation can take 5-10 minutes
- **Test**: `nslookup image2model.pranitlab.com`
- **Expected**: Should return Cloudflare IPs (not 66.228.60.251)

### n8n stopped working
- **Check**: `systemctl status cloudflared`
- **Check**: Is n8n still in tunnel config? `cat /etc/cloudflared/config.yml`
- **Fix**: Make sure you didn't accidentally remove n8n entries

## Files That Need Updates (Summary)

### On Local Machine (then push to git):
1. **docker-compose.prod.yml**:
   - Remove `./frontend-simple` references
   - Update frontend service to use `frontend-svelte`
   - Update nginx config path to `nginx.svelte.conf`

2. **Create docker/nginx/nginx.svelte.conf**:
   - New nginx config that proxies to frontend:3000
   - Handles API routing to backend:8000

### On Server (after git pull):
1. **.env file**:
   - Already created from .env.production
   - Already has additional Docker variables

2. **SSL Decision**:
   - Option A: Change Cloudflare to "Flexible" SSL (easier)
   - Option B: Keep "Full" SSL and mount certificates (more secure)

## Complete Migration Command Sequence

```bash
# On local machine
cd /Users/pranit/Documents/AI/image2model
git add docker-compose.prod.yml docker/nginx/nginx.svelte.conf
git commit -m "Update deployment for frontend-svelte and Cloudflare CDN"
git push origin main

# On server
ssh root@66.228.60.251
cd /opt/image2model
git pull origin main
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Wait 60 seconds for services to start
sleep 60

# Test
curl http://localhost/health
curl http://localhost/api/v1/health/

# Test from outside (after DNS propagation)
curl https://image2model.pranitlab.com/
curl https://image2model.pranitlab.com/api/v1/health/
```