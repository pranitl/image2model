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