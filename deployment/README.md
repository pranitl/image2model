# Image2Model Deployment Scripts

This directory contains deployment and configuration scripts for the Image2Model application.

## Files Overview

### Configuration Files

- **`access-config.yaml`** - Declarative configuration for Cloudflare Access rules
  - Define public, authenticated, and admin endpoints
  - Configure allowed users and domains
  - Manage API access settings

### Deployment Scripts

- **`deploy.sh`** - Main deployment script for manual deployments
  - Builds Docker containers
  - Deploys to production server
  - Runs health checks
  - Supports various flags (--build-only, --deploy-only, --skip-tests)

- **`cicd-deploy.sh`** - CI/CD pipeline deployment script
  - Designed for GitHub Actions, GitLab CI, Jenkins, etc.
  - Includes Slack notifications
  - Environment variable validation
  - Automated testing and deployment

- **`configure-access.py`** - Cloudflare Access configuration script
  - Reads access-config.yaml
  - Creates/updates Cloudflare Access applications
  - Sets up bypass rules for public endpoints
  - Manages service tokens for API access

## Quick Start

### 1. Manual Deployment

```bash
# Full deployment (build + deploy)
./deployment/deploy.sh

# Build only
./deployment/deploy.sh --build-only

# Deploy only (skip build)
./deployment/deploy.sh --deploy-only

# Skip tests
./deployment/deploy.sh --skip-tests
```

### 2. Configure Cloudflare Access

```bash
# Load environment variables
set -a && source .env.production && set +a

# Apply access configuration
python3 deployment/configure-access.py

# Create new service token
python3 deployment/configure-access.py --create-token
```

### 3. CI/CD Deployment

Set these environment variables in your CI/CD platform:

```bash
# Required
CLOUDFLARE_API_TOKEN=your-token
CLOUDFLARE_ACCOUNT_ID=your-account-id
FAL_API_KEY=your-fal-key
DATABASE_URL=postgresql://...
API_KEY=your-api-key

# Optional
DEPLOY_HOST=66.228.60.251
DEPLOY_USER=root
SLACK_WEBHOOK=https://hooks.slack.com/...
```

Then run:

```bash
./deployment/cicd-deploy.sh
```

## Access Configuration

Edit `access-config.yaml` to manage endpoint access:

```yaml
endpoints:
  # Public endpoints - no authentication required
  public:
    - path: "/"
      description: "Home page"
    - path: "/api/v1/health"
      description: "Health check"

  # Authenticated endpoints - require login
  authenticated:
    - path: "/upload"
      description: "Upload UI"
    - path: "/api/v1/models/generate"
      description: "Model generation"

  # Admin endpoints - require admin privileges
  admin:
    emails:
      - "admin@example.com"
    endpoints:
      - path: "/api/v1/admin/*"
        description: "Admin endpoints"
```

## GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          FAL_API_KEY: ${{ secrets.FAL_API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          API_KEY: ${{ secrets.API_KEY }}
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
        run: |
          chmod +x deployment/cicd-deploy.sh
          ./deployment/cicd-deploy.sh
```

## Testing Access Configuration

After deployment, test your endpoints:

```bash
# Public endpoint (should work)
curl https://image2model.pranitlab.com/api/v1/health/

# Protected endpoint (should require auth)
curl https://image2model.pranitlab.com/api/v1/models/generate

# With API key
curl https://image2model.pranitlab.com/api/v1/models/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test"}'

# With service token
curl https://image2model.pranitlab.com/api/v1/models/generate \
  -H "CF-Access-Client-Id: YOUR_CLIENT_ID" \
  -H "CF-Access-Client-Secret: YOUR_CLIENT_SECRET" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test"}'
```

## Security Notes

1. **Never commit credentials** - Use environment variables
2. **Rotate API keys regularly** - Update in CI/CD secrets
3. **Monitor access logs** - Check Cloudflare dashboard
4. **Test after changes** - Verify both public and protected endpoints

## Troubleshooting

### Deployment fails with "permission denied"
- Ensure SSH key is added to the server
- Check DEPLOY_USER has sudo privileges

### Cloudflare Access not working
- Verify CLOUDFLARE_API_TOKEN has correct permissions
- Check access-config.yaml syntax
- Wait 30-60 seconds for changes to propagate

### Health check fails
- Check Docker logs: `docker logs image2model-backend`
- Verify .env.production has all required variables
- Ensure database is accessible