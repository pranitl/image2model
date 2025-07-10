#!/bin/bash
# MVP Deployment Script
# 
# Features:
# - Uses git rebase instead of pull to maintain clean history
# - Supports both cached and no-cache builds (use --no-cache flag for fresh builds)
# - Ensures proper newline handling when appending to .env files
#
# Usage:
#   ./deploy-mvp.sh              # Normal deployment (uses cache)
#   ./deploy-mvp.sh --no-cache   # Force fresh build without cache

DEPLOY_HOST="66.228.60.251"
NO_CACHE_FLAG=""

# Check for --no-cache argument
if [ "$1" = "--no-cache" ]; then
    NO_CACHE_FLAG="--no-cache"
    echo "🔨 No-cache mode enabled - will rebuild everything from scratch"
fi

echo "🚀 Deploying to $DEPLOY_HOST..."

ssh root@$DEPLOY_HOST << EOF
set -e  # Exit on error

# Pass the no-cache flag from local to remote
NO_CACHE_FLAG="$NO_CACHE_FLAG"

cd /opt/image2model

# Ensure we're on the right repo
if ! git remote -v | grep -q "github.com/pranitl/image2model"; then
    echo "❌ Wrong git repo!"
    exit 1
fi

# Pull latest changes with rebase
echo "📥 Pulling latest code with rebase..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"
git fetch origin $CURRENT_BRANCH
git rebase origin/$CURRENT_BRANCH

# Ensure environment file is up to date
if [ -f ".env.production" ]; then
    cp .env.production .env
    # Ensure file ends with newline before appending
    [ -n "$(tail -c 1 .env)" ] && echo >> .env
    # Add any missing Docker-specific variables
    grep -q "BACKEND_HOST" .env || echo "BACKEND_HOST=backend" >> .env
    grep -q "BACKEND_PORT" .env || echo "BACKEND_PORT=8000" >> .env
    grep -q "POSTGRES_PORT" .env || echo "POSTGRES_PORT=5432" >> .env
fi

# Restart services with optional rebuild
echo "🔄 Restarting services..."
# Use DOCKER_BUILDKIT=1 for better performance and BUILDKIT_PROGRESS=plain for clearer output
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# Down the services first
docker compose -f docker-compose.prod.yml --env-file .env.production down

if [ -n "\$NO_CACHE_FLAG" ]; then
    echo "🔨 Building with --no-cache (fresh build)..."
    docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache
    docker compose -f docker-compose.prod.yml --env-file .env.production up -d
else
    echo "⚡ Building with cache (faster)..."
    # Use --build flag with up for better performance when cache is enabled
    docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
fi

# Wait and check
echo "⏳ Waiting for services..."
sleep 60

# Health check
if curl -f http://localhost/api/v1/health/; then
    echo "✅ Local health check passed!"
    
    # Test via Cloudflare
    echo "🌐 Testing via Cloudflare..."
    if curl -f https://image2model.pranitlab.com/api/v1/health/; then
        echo "✅ Deployment successful! Site is live."
    else
        echo "⚠️  Warning: Cloudflare check failed (might need DNS propagation)"
    fi
else
    echo "❌ Health check failed!"
    docker logs image2model-backend --tail 20
    exit 1
fi
EOF
